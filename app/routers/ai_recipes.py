import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.ai_recipe import AIRecipeHistory
from app.schemas.ai_recipe import RecipeGenerateRequest, MealPlanRequest
from app.utils.security import get_current_user
from app.ai.graph import recipe_graph, meal_plan_graph

router = APIRouter()


def _check_recipe_limit(user: User, db: Session):
    from app.models.payment import UserSubscription, SubscriptionPlan
    from sqlalchemy import func, extract
    from datetime import datetime

    sub = db.query(UserSubscription).filter(UserSubscription.user_id == user.id).first()
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == sub.plan_id
    ).first() if sub else None

    limit = plan.ai_recipes_per_month if plan else 3
    if limit >= 999:
        return

    now = datetime.utcnow()
    count = db.query(func.count(AIRecipeHistory.id)).filter(
        AIRecipeHistory.user_id == user.id,
        extract("month", AIRecipeHistory.created_at) == now.month,
        extract("year", AIRecipeHistory.created_at) == now.year,
    ).scalar()

    if count >= limit:
        raise HTTPException(status_code=403, detail=f"Monthly AI recipe limit ({limit}) reached. Upgrade your plan.")


@router.post("/generate-recipe")
def generate_recipe(
    body: RecipeGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_recipe_limit(current_user, db)

    initial_state = {
        "user_id": str(current_user.id),
        "request": body.model_dump(),
        "user_profile": None,
        "health_profile": None,
        "active_diet_plan": None,
        "recipe_raw": None,
        "nutrition_data": None,
        "is_valid": False,
        "validation_issues": [],
        "retry_count": 0,
        "final_recipe": None,
        "error": None,
    }

    result = recipe_graph.invoke(initial_state)

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    recipe = result.get("final_recipe")
    if not recipe:
        raise HTTPException(status_code=500, detail="Recipe generation failed")

    history = AIRecipeHistory(
        user_id=current_user.id,
        prompt_input=body.model_dump(),
        recipe_title=recipe.get("title"),
        recipe_data=recipe,
        nutrition_data=recipe.get("nutrition_per_serving"),
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    return {"recipe_id": str(history.id), **recipe, "created_at": str(history.created_at)}


@router.post("/suggest-meal-plan")
def suggest_meal_plan(
    body: MealPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    initial_state = {
        "user_id": str(current_user.id),
        "request": body.model_dump(),
        "user_profile": None,
        "health_profile": None,
        "meal_plan_raw": None,
        "final_meal_plan": None,
        "error": None,
    }

    result = meal_plan_graph.invoke(initial_state)

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    return {"week_start": "next monday", "days": result.get("final_meal_plan")}


@router.get("/recipes/history")
def get_recipe_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.query(AIRecipeHistory).filter(
        AIRecipeHistory.user_id == current_user.id
    ).order_by(AIRecipeHistory.created_at.desc()).limit(20).all()

    return [
        {
            "id": str(r.id), "recipe_title": r.recipe_title,
            "recipe_data": r.recipe_data, "nutrition_data": r.nutrition_data,
            "is_saved": r.is_saved, "created_at": str(r.created_at),
        }
        for r in records
    ]


@router.patch("/recipes/{recipe_id}/save")
def toggle_save_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(AIRecipeHistory).filter(
        AIRecipeHistory.id == recipe_id, AIRecipeHistory.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Recipe not found")
    record.is_saved = not record.is_saved
    db.commit()
    return {"is_saved": record.is_saved}
