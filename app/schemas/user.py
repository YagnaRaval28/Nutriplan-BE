from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class HealthProfileCreate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    health_goal: Optional[str] = "maintain"
    activity_level: Optional[str] = "moderate"
    allergies: Optional[List[str]] = []
    medical_conditions: Optional[List[str]] = []
    diet_type: Optional[str] = "non_vegetarian"
    cuisine_preferences: Optional[List[str]] = []
    daily_calorie_goal: Optional[int] = None


class HealthProfileResponse(BaseModel):
    age: Optional[int]
    gender: Optional[str]
    weight_kg: Optional[float]
    height_cm: Optional[float]
    bmi: Optional[float]
    bmr: Optional[float]
    tdee: Optional[float]
    daily_calorie_goal: Optional[int]
    daily_protein_goal: Optional[int]
    daily_carbs_goal: Optional[int]
    daily_fats_goal: Optional[int]
    daily_water_goal_ml: Optional[int]
    health_goal: Optional[str]
    activity_level: Optional[str]
    allergies: Optional[List[str]]
    medical_conditions: Optional[List[str]]
    diet_type: Optional[str]
    cuisine_preferences: Optional[List[str]]

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool
    is_email_verified: bool
    profile_photo_url: Optional[str]
    created_at: datetime
    health_profile: Optional[HealthProfileResponse]

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    profile_photo_url: Optional[str] = None


class WeightLogCreate(BaseModel):
    weight_kg: float
    notes: Optional[str] = None


class WeightLogResponse(BaseModel):
    id: UUID
    weight_kg: float
    notes: Optional[str]
    logged_at: datetime

    class Config:
        from_attributes = True


class DashboardMacros(BaseModel):
    protein: dict
    carbs: dict
    fats: dict
    fiber: dict


class DashboardResponse(BaseModel):
    date: str
    calories_consumed: float
    calories_goal: int
    macros: DashboardMacros
    water_intake_ml: int
    meals_logged: int


class DieticianProfileCreate(BaseModel):
    license_number: str
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    education: Optional[str] = None


class DoctorProfileCreate(BaseModel):
    license_number: str
    specialization: Optional[str] = None
    hospital_name: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
