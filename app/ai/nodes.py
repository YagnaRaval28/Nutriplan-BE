import json
import re
from app.ai.state import RecipeAgentState, MealPlanAgentState
from app.ai.prompts import RECIPE_GENERATION_PROMPT, MEAL_PLAN_PROMPT, NUTRITION_VALIDATOR_PROMPT


def _get_llm():
    from langchain_groq import ChatGroq
    from app.config import settings
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=settings.GROQ_API_KEY, temperature=0.7)


def _parse_json_from_response(text: str) -> dict:
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        return json.loads(match.group())
    raise ValueError("No valid JSON found in LLM response")


# ── Recipe Agent Nodes ────────────────────────────────────────────────────────

def profile_analyzer(state: RecipeAgentState) -> RecipeAgentState:
    from app.db.session import SessionLocal
    from app.models.user import User, UserHealthProfile
    from app.models.diet_plan import DietPlan

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == state["user_id"]).first()
        profile = db.query(UserHealthProfile).filter(UserHealthProfile.user_id == state["user_id"]).first()
        active_plan = db.query(DietPlan).filter(
            DietPlan.assigned_to == state["user_id"], DietPlan.status == "active"
        ).first()

        state["user_profile"] = {"name": user.name, "role": user.role} if user else {}
        state["health_profile"] = {
            "age": int(profile.age) if profile and profile.age else 25,
            "gender": profile.gender if profile and profile.gender else "male",
            "weight_kg": float(profile.weight_kg) if profile and profile.weight_kg else 70,
            "height_cm": float(profile.height_cm) if profile and profile.height_cm else 170,
            "health_goal": profile.health_goal if profile else "maintain",
            "diet_type": profile.diet_type if profile else "non_vegetarian",
            "allergies": profile.allergies if profile and profile.allergies else [],
            "medical_conditions": profile.medical_conditions if profile and profile.medical_conditions else [],
            "daily_calorie_goal": int(profile.daily_calorie_goal) if profile and profile.daily_calorie_goal else 2000,
            "daily_protein_goal": int(profile.daily_protein_goal) if profile and profile.daily_protein_goal else 150,
            "daily_carbs_goal": int(profile.daily_carbs_goal) if profile and profile.daily_carbs_goal else 200,
            "daily_fats_goal": int(profile.daily_fats_goal) if profile and profile.daily_fats_goal else 65,
        } if profile else {}
        state["active_diet_plan"] = {"plan_name": active_plan.plan_name} if active_plan else None
    finally:
        db.close()

    state["is_valid"] = False
    state["validation_issues"] = []
    state["retry_count"] = 0
    return state


def recipe_generator(state: RecipeAgentState) -> RecipeAgentState:
    llm = _get_llm()
    hp = state.get("health_profile", {})
    req = state.get("request", {})
    allergies = (hp.get("allergies") or []) + (req.get("exclude_ingredients") or [])

    prompt = RECIPE_GENERATION_PROMPT.format(
        age=hp.get("age", 25),
        gender=hp.get("gender", "male"),
        weight_kg=hp.get("weight_kg", 70),
        health_goal=hp.get("health_goal", "maintain"),
        diet_type=hp.get("diet_type", "non_vegetarian"),
        allergies=", ".join(allergies) if allergies else "None",
        medical_conditions=", ".join(hp.get("medical_conditions") or []) or "None",
        calorie_target=req.get("calorie_target", 500),
        meal_type=req.get("meal_type", "lunch"),
        cuisine_type=req.get("cuisine_type", "Any"),
        dietary_preference=req.get("dietary_preference", "non_vegetarian"),
        available_ingredients=", ".join(req.get("available_ingredients") or []) or "any",
        exclude_ingredients=", ".join(req.get("exclude_ingredients") or []) or "None",
        servings=req.get("servings", 2),
    )

    try:
        response = llm.invoke(prompt)
        state["recipe_raw"] = _parse_json_from_response(response.content)
    except Exception as e:
        state["error"] = f"Recipe generation failed: {str(e)}"
        state["recipe_raw"] = None

    return state


def nutrition_calculator(state: RecipeAgentState) -> RecipeAgentState:
    if not state.get("recipe_raw"):
        return state

    from app.db.session import SessionLocal
    from app.models.food import FoodItem
    from sqlalchemy import or_

    recipe = state["recipe_raw"]
    ingredients = recipe.get("ingredients", [])
    db = SessionLocal()
    total = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fats_g": 0.0, "fiber_g": 0.0}

    try:
        for ing in ingredients:
            name = ing.get("name", "")
            qty = float(ing.get("quantity", 100))
            food = db.query(FoodItem).filter(
                or_(FoodItem.name.ilike(f"%{name}%"), FoodItem.name_hindi.ilike(f"%{name}%"))
            ).first()

            if food:
                ratio = qty / float(food.serving_size)
                total["calories"] += float(food.calories) * ratio
                total["protein_g"] += float(food.protein_g) * ratio
                total["carbs_g"] += float(food.carbs_g) * ratio
                total["fats_g"] += float(food.fats_g) * ratio
                total["fiber_g"] += float(food.fiber_g) * ratio
    finally:
        db.close()

    servings = recipe.get("servings", 1)
    state["nutrition_data"] = {
        "per_serving": {k: round(v / servings, 2) for k, v in total.items()},
        "total": {k: round(v, 2) for k, v in total.items()},
    }
    return state


def nutrition_validator(state: RecipeAgentState) -> RecipeAgentState:
    if not state.get("recipe_raw"):
        state["is_valid"] = False
        return state

    llm = _get_llm()
    hp = state.get("health_profile", {})
    req = state.get("request", {})
    allergies = (hp.get("allergies") or []) + (req.get("exclude_ingredients") or [])

    prompt = NUTRITION_VALIDATOR_PROMPT.format(
        recipe=json.dumps(state["recipe_raw"]),
        calorie_target=req.get("calorie_target", 500),
        allergies=", ".join(allergies) if allergies else "None",
        exclude_ingredients=", ".join(req.get("exclude_ingredients") or []) or "None",
    )

    try:
        response = llm.invoke(prompt)
        result = _parse_json_from_response(response.content)
        state["is_valid"] = result.get("is_valid", False)
        state["validation_issues"] = result.get("issues", [])
    except Exception:
        state["is_valid"] = True  # allow through on validator error

    return state


def finalize_recipe(state: RecipeAgentState) -> RecipeAgentState:
    state["final_recipe"] = {
        **state["recipe_raw"],
        "nutrition_per_serving": state.get("nutrition_data", {}).get("per_serving", {}),
    }
    return state


def should_retry(state: RecipeAgentState) -> str:
    if state.get("error"):
        return "end_with_error"
    if state["is_valid"]:
        return "finalize"
    if state["retry_count"] >= 2:
        state["is_valid"] = True
        return "finalize"
    state["retry_count"] += 1
    return "retry"


# ── Meal Plan Nodes ───────────────────────────────────────────────────────────

def meal_plan_profile_analyzer(state: MealPlanAgentState) -> MealPlanAgentState:
    from app.db.session import SessionLocal
    from app.models.user import UserHealthProfile

    db = SessionLocal()
    try:
        profile = db.query(UserHealthProfile).filter(UserHealthProfile.user_id == state["user_id"]).first()
        state["health_profile"] = {
            "health_goal": profile.health_goal if profile else "maintain",
            "diet_type": profile.diet_type if profile else "non_vegetarian",
            "allergies": profile.allergies if profile and profile.allergies else [],
            "medical_conditions": profile.medical_conditions if profile and profile.medical_conditions else [],
            "daily_calorie_goal": int(profile.daily_calorie_goal) if profile and profile.daily_calorie_goal else 2000,
            "daily_protein_goal": int(profile.daily_protein_goal) if profile and profile.daily_protein_goal else 150,
            "daily_carbs_goal": int(profile.daily_carbs_goal) if profile and profile.daily_carbs_goal else 200,
            "daily_fats_goal": int(profile.daily_fats_goal) if profile and profile.daily_fats_goal else 65,
        }
    finally:
        db.close()
    return state


def meal_plan_generator(state: MealPlanAgentState) -> MealPlanAgentState:
    llm = _get_llm()
    hp = state.get("health_profile", {})
    req = state.get("request", {})
    allergies = (hp.get("allergies") or []) + (req.get("exclude_ingredients") or [])

    prompt = MEAL_PLAN_PROMPT.format(
        health_goal=hp.get("health_goal", "maintain"),
        diet_type=hp.get("diet_type", "non_vegetarian"),
        allergies=", ".join(allergies) if allergies else "None",
        medical_conditions=", ".join(hp.get("medical_conditions") or []) or "None",
        daily_calorie_goal=req.get("weekly_calorie_goal", 14000) // 7,
        protein_goal=hp.get("daily_protein_goal", 150),
        carbs_goal=hp.get("daily_carbs_goal", 200),
        fats_goal=hp.get("daily_fats_goal", 65),
        cuisine_preferences=", ".join(req.get("cuisine_preferences") or ["Indian"]),
        dietary_preference=req.get("dietary_preference", "non_vegetarian"),
        exclude_ingredients=", ".join(req.get("exclude_ingredients") or []) or "None",
    )

    try:
        response = llm.invoke(prompt)
        state["meal_plan_raw"] = _parse_json_from_response(response.content)
        state["final_meal_plan"] = state["meal_plan_raw"]
    except Exception as e:
        state["error"] = f"Meal plan generation failed: {str(e)}"

    return state
