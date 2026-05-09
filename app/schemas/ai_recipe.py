from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class RecipeGenerateRequest(BaseModel):
    cuisine_type: Optional[str] = "Any"
    dietary_preference: Optional[str] = "non_vegetarian"
    calorie_target: Optional[int] = 500
    available_ingredients: Optional[List[str]] = []
    exclude_ingredients: Optional[List[str]] = []
    meal_type: Optional[str] = "lunch"
    servings: Optional[int] = 2


class MealPlanRequest(BaseModel):
    weekly_calorie_goal: Optional[int] = 14000
    dietary_preference: Optional[str] = "non_vegetarian"
    cuisine_preferences: Optional[List[str]] = ["Indian"]
    exclude_ingredients: Optional[List[str]] = []


class IngredientItem(BaseModel):
    name: str
    quantity: float
    unit: str


class NutritionInfo(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float
    fiber_g: float


class RecipeResponse(BaseModel):
    recipe_id: UUID
    title: str
    description: str
    ingredients: List[IngredientItem]
    steps: List[str]
    cook_time_minutes: int
    servings: int
    nutrition_per_serving: NutritionInfo
    created_at: datetime

    class Config:
        from_attributes = True


class RecipeHistoryResponse(BaseModel):
    id: UUID
    recipe_title: Optional[str]
    recipe_data: dict
    nutrition_data: Optional[dict]
    is_saved: bool
    created_at: datetime

    class Config:
        from_attributes = True
