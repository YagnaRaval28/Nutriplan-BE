def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor equation."""
    if gender == "male":
        return round((10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5, 2)
    elif gender == "female":
        return round((10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161, 2)
    else:
        return round((10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 78, 2)


ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 2)


def calculate_calorie_goal(tdee: float, health_goal: str) -> int:
    goals = {
        "weight_loss": -500,
        "weight_gain": 500,
        "muscle_gain": 300,
        "maintain": 0,
    }
    return round(tdee + goals.get(health_goal, 0))


def calculate_macro_goals(calorie_goal: int, weight_kg: float, health_goal: str) -> dict:
    protein_g = round(weight_kg * 2)
    protein_cal = protein_g * 4

    if health_goal in ("weight_loss",):
        fat_ratio = 0.25
    elif health_goal in ("muscle_gain", "weight_gain"):
        fat_ratio = 0.28
    else:
        fat_ratio = 0.27

    fats_cal = round(calorie_goal * fat_ratio)
    fats_g = round(fats_cal / 9)

    carbs_cal = calorie_goal - protein_cal - fats_cal
    carbs_g = round(carbs_cal / 4)

    return {
        "daily_protein_goal": max(protein_g, 50),
        "daily_carbs_goal": max(carbs_g, 50),
        "daily_fats_goal": max(fats_g, 20),
        "daily_fiber_goal": 25,
        "daily_water_goal_ml": round(weight_kg * 35),
    }


def compute_consumed_nutrition(food_item, quantity: float, serving_size: float) -> dict:
    ratio = quantity / float(serving_size)
    return {
        "calories_consumed": round(float(food_item.calories) * ratio, 2),
        "protein_consumed_g": round(float(food_item.protein_g) * ratio, 2),
        "carbs_consumed_g": round(float(food_item.carbs_g) * ratio, 2),
        "fats_consumed_g": round(float(food_item.fats_g) * ratio, 2),
        "fiber_consumed_g": round(float(food_item.fiber_g) * ratio, 2),
    }
