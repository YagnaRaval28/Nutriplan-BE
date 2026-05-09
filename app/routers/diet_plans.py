from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date, func

from app.db.session import get_db
from app.models.diet_plan import DietPlan, DietPlanMeal, DietPlanMealItem
from app.models.user import User, DieticianClientLink
from app.models.food import FoodItem, FoodLog
from app.schemas.diet_plan import DietPlanCreate, DietPlanUpdate, DietPlanResponse, ClientProgressResponse
from app.utils.security import get_current_user, require_role
from datetime import date

router = APIRouter()


def _build_plan_response(plan: DietPlan, db: Session) -> dict:
    meals_out = []
    for meal in plan.meals:
        items_out = []
        for item in meal.items:
            food = db.query(FoodItem).filter(FoodItem.id == item.food_item_id).first()
            items_out.append({
                "id": str(item.id), "food_item_id": str(item.food_item_id),
                "food_name": food.name if food else "Unknown",
                "quantity": float(item.quantity), "unit": item.unit,
                "calories": float(item.calories) if item.calories else None,
                "notes": item.notes,
            })
        meals_out.append({"id": str(meal.id), "day_of_week": meal.day_of_week,
                          "meal_type": meal.meal_type, "notes": meal.notes, "items": items_out})
    return {
        "id": str(plan.id), "plan_name": plan.plan_name,
        "created_by": str(plan.created_by), "assigned_to": str(plan.assigned_to),
        "start_date": str(plan.start_date), "end_date": str(plan.end_date),
        "notes": plan.notes, "health_goal": plan.health_goal,
        "status": plan.status, "created_at": str(plan.created_at), "meals": meals_out,
    }


@router.post("", status_code=201)
def create_diet_plan(
    body: DietPlanCreate,
    current_user: User = Depends(require_role("dietician", "doctor", "admin")),
    db: Session = Depends(get_db),
):
    assignee = db.query(User).filter(User.id == body.assigned_to_user_id).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assigned user not found")

    plan = DietPlan(
        plan_name=body.plan_name, created_by=current_user.id,
        assigned_to=body.assigned_to_user_id, start_date=body.start_date,
        end_date=body.end_date, notes=body.notes, health_goal=body.health_goal,
    )
    db.add(plan)
    db.flush()

    for meal_data in body.meals:
        meal = DietPlanMeal(
            diet_plan_id=plan.id, day_of_week=meal_data.day_of_week,
            meal_type=meal_data.meal_type, notes=meal_data.notes,
        )
        db.add(meal)
        db.flush()
        for fi in meal_data.food_items:
            food = db.query(FoodItem).filter(FoodItem.id == fi.food_item_id).first()
            cal = round(float(food.calories) * fi.quantity / float(food.serving_size), 2) if food else None
            db.add(DietPlanMealItem(
                meal_id=meal.id, food_item_id=fi.food_item_id,
                quantity=fi.quantity, unit=fi.unit, calories=cal, notes=fi.notes,
            ))

    if current_user.role == "dietician":
        existing = db.query(DieticianClientLink).filter(
            DieticianClientLink.dietician_id == current_user.id,
            DieticianClientLink.client_id == body.assigned_to_user_id,
        ).first()
        if not existing:
            db.add(DieticianClientLink(dietician_id=current_user.id, client_id=body.assigned_to_user_id))

    db.commit()
    db.refresh(plan)
    return _build_plan_response(plan, db)


@router.get("/mine")
def get_my_plan(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(DietPlan).filter(
        DietPlan.assigned_to == current_user.id,
        DietPlan.status == "active",
    ).order_by(DietPlan.created_at.desc()).first()
    if not plan:
        raise HTTPException(status_code=404, detail="No active diet plan found")
    return _build_plan_response(plan, db)


@router.get("/{plan_id}")
def get_plan(plan_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(DietPlan).filter(DietPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if str(plan.assigned_to) != str(current_user.id) and str(plan.created_by) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return _build_plan_response(plan, db)


@router.put("/{plan_id}")
def update_plan(
    plan_id: str, body: DietPlanUpdate,
    current_user: User = Depends(require_role("dietician", "doctor", "admin")),
    db: Session = Depends(get_db),
):
    plan = db.query(DietPlan).filter(DietPlan.id == plan_id, DietPlan.created_by == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or not authorized")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(plan, k, v)
    db.commit()
    return {"message": "Plan updated"}


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: str,
    current_user: User = Depends(require_role("dietician", "doctor", "admin")),
    db: Session = Depends(get_db),
):
    plan = db.query(DietPlan).filter(DietPlan.id == plan_id, DietPlan.created_by == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or not authorized")
    db.delete(plan)
    db.commit()
    return {"message": "Plan deleted"}


@router.get("/dietician/clients")
def get_clients(current_user: User = Depends(require_role("dietician")), db: Session = Depends(get_db)):
    links = db.query(DieticianClientLink).filter(
        DieticianClientLink.dietician_id == current_user.id,
        DieticianClientLink.status == "active",
    ).all()
    result = []
    for link in links:
        client = db.query(User).filter(User.id == link.client_id).first()
        if not client:
            continue
        active_plan = db.query(DietPlan).filter(
            DietPlan.assigned_to == client.id, DietPlan.status == "active"
        ).first()
        last_log = db.query(FoodLog).filter(FoodLog.user_id == client.id).order_by(FoodLog.logged_at.desc()).first()
        result.append({
            "user_id": str(client.id), "name": client.name, "email": client.email,
            "active_plan": active_plan.plan_name if active_plan else None,
            "last_log_date": str(last_log.logged_at.date()) if last_log else None,
        })
    return result


@router.get("/dietician/clients/{user_id}/progress")
def get_client_progress(
    user_id: str,
    current_user: User = Depends(require_role("dietician", "doctor", "admin")),
    db: Session = Depends(get_db),
):
    from datetime import timedelta
    end = date.today()
    start = end - timedelta(days=7)
    rows = db.query(
        cast(FoodLog.logged_at, Date).label("log_date"),
        func.sum(FoodLog.calories_consumed).label("calories"),
    ).filter(
        FoodLog.user_id == user_id,
        cast(FoodLog.logged_at, Date) >= start,
    ).group_by(cast(FoodLog.logged_at, Date)).all()
    return {"user_id": user_id, "weekly_logs": [{"date": str(r.log_date), "calories": round(float(r.calories), 2)} for r in rows]}
