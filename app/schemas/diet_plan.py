from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime


class MealItemCreate(BaseModel):
    food_item_id: UUID
    quantity: float
    unit: str
    notes: Optional[str] = None


class MealCreate(BaseModel):
    day_of_week: str
    meal_type: str
    notes: Optional[str] = None
    food_items: List[MealItemCreate] = []


class DietPlanCreate(BaseModel):
    plan_name: str
    assigned_to_user_id: UUID
    start_date: date
    end_date: date
    notes: Optional[str] = None
    health_goal: Optional[str] = None
    meals: List[MealCreate] = []


class DietPlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class MealItemResponse(BaseModel):
    id: UUID
    food_item_id: UUID
    food_name: str
    quantity: float
    unit: str
    calories: Optional[float]
    notes: Optional[str]

    class Config:
        from_attributes = True


class MealResponse(BaseModel):
    id: UUID
    day_of_week: str
    meal_type: str
    notes: Optional[str]
    items: List[MealItemResponse]

    class Config:
        from_attributes = True


class DietPlanResponse(BaseModel):
    id: UUID
    plan_name: str
    created_by: UUID
    assigned_to: UUID
    start_date: date
    end_date: date
    notes: Optional[str]
    health_goal: Optional[str]
    status: str
    created_at: datetime
    meals: List[MealResponse]

    class Config:
        from_attributes = True


class ClientProgressResponse(BaseModel):
    user_id: UUID
    name: str
    email: str
    active_plan: Optional[str]
    last_log_date: Optional[date]
    adherence_rate: float
    avg_daily_calories: float
