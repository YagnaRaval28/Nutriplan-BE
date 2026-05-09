from typing import TypedDict, Optional, List, Any


class RecipeAgentState(TypedDict):
    # Inputs
    user_id: str
    request: dict

    # Profile data (filled by profile_analyzer node)
    user_profile: Optional[dict]
    health_profile: Optional[dict]
    active_diet_plan: Optional[dict]

    # Generation
    recipe_raw: Optional[dict]
    nutrition_data: Optional[dict]

    # Validation
    is_valid: bool
    validation_issues: List[str]
    retry_count: int

    # Final output
    final_recipe: Optional[dict]
    error: Optional[str]


class MealPlanAgentState(TypedDict):
    user_id: str
    request: dict
    user_profile: Optional[dict]
    health_profile: Optional[dict]
    meal_plan_raw: Optional[dict]
    final_meal_plan: Optional[dict]
    error: Optional[str]
