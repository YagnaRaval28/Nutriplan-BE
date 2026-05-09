from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class FoodItemResponse(BaseModel):
    id: UUID
    name: str
    name_hindi: Optional[str]
    brand: Optional[str]
    serving_size: float
    unit: str
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float
    fiber_g: float
    sugar_g: float
    sodium_mg: float
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool
    common_allergens: Optional[List[str]]
    image_url: Optional[str]

    class Config:
        from_attributes = True


class FoodSearchResponse(BaseModel):
    results: List[FoodItemResponse]
    total: int
    page: int
    limit: int


class CustomFoodCreate(BaseModel):
    name: str
    serving_size: float
    unit: str
    calories: float
    protein_g: float = 0
    carbs_g: float = 0
    fats_g: float = 0
    fiber_g: float = 0
    sugar_g: float = 0
    sodium_mg: float = 0
    is_vegetarian: bool = True
    is_vegan: bool = False
    is_gluten_free: bool = False


class FoodLogCreate(BaseModel):
    food_item_id: UUID
    meal_type: str
    quantity: float
    unit: str
    logged_at: Optional[datetime] = None


class FoodLogResponse(BaseModel):
    id: UUID
    food_item_id: UUID
    food_name: str
    meal_type: str
    quantity: float
    unit: str
    calories_consumed: float
    protein_consumed_g: float
    carbs_consumed_g: float
    fats_consumed_g: float
    fiber_consumed_g: float
    logged_at: datetime

    class Config:
        from_attributes = True


class DailyMacroSummary(BaseModel):
    date: str
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float
    fiber_g: float


class DailyLogsResponse(BaseModel):
    date: str
    logs: List[FoodLogResponse]
    daily_totals: DailyMacroSummary


class WaterLogCreate(BaseModel):
    amount_ml: int


class WaterLogResponse(BaseModel):
    id: UUID
    amount_ml: int
    logged_at: datetime

    class Config:
        from_attributes = True
