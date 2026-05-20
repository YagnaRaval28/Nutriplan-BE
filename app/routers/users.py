from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from app.db.session import get_db
from app.models.user import User, UserHealthProfile, WeightLog, DieticianProfile, DoctorProfile
from app.models.food import FoodLog, WaterLog
from app.schemas.user import (
    HealthProfileCreate, HealthProfileResponse, UserProfileResponse,
    UserProfileUpdate, WeightLogCreate, WeightLogResponse, DashboardResponse,
    DieticianProfileCreate, DoctorProfileCreate,
)
from app.utils.security import get_current_user, require_role
from app.utils.calculations import (
    calculate_bmi, calculate_bmr, calculate_tdee,
    calculate_calorie_goal, calculate_macro_goals,
)

router = APIRouter()


@router.get("/search")
def search_users(
    q: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    users = db.query(User).filter(
        User.id != current_user.id,
        User.is_active == True,
        (User.name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%")),
    ).limit(10).all()
    return [{"id": str(u.id), "name": u.name, "email": u.email, "role": u.role} for u in users]


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.refresh(current_user)
    return current_user


@router.put("/profile")
def update_profile(body: UserProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.name:
        current_user.name = body.name
    if body.profile_photo_url:
        current_user.profile_photo_url = body.profile_photo_url
    db.commit()
    return {"message": "Profile updated"}


@router.post("/health-profile")
def create_or_update_health_profile(
    body: HealthProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserHealthProfile).filter(UserHealthProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserHealthProfile(user_id=current_user.id)
        db.add(profile)

    for field, val in body.model_dump(exclude_none=True).items():
        setattr(profile, field, val)

    if profile.weight_kg and profile.height_cm:
        profile.bmi = calculate_bmi(float(profile.weight_kg), float(profile.height_cm))

    if profile.weight_kg and profile.height_cm and profile.age and profile.gender:
        profile.bmr = calculate_bmr(float(profile.weight_kg), float(profile.height_cm), profile.age, profile.gender)
        profile.tdee = calculate_tdee(float(profile.bmr), profile.activity_level or "moderate")
        calorie_goal = calculate_calorie_goal(float(profile.tdee), profile.health_goal or "maintain")
        profile.daily_calorie_goal = calorie_goal
        macros = calculate_macro_goals(calorie_goal, float(profile.weight_kg), profile.health_goal or "maintain")
        for k, v in macros.items():
            setattr(profile, k, v)

    db.commit()
    db.refresh(profile)
    return HealthProfileResponse.model_validate(profile)


@router.get("/health-profile", response_model=HealthProfileResponse)
def get_health_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserHealthProfile).filter(UserHealthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    return profile


@router.get("/dashboard")
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        cast(FoodLog.logged_at, Date) == today,
    ).all()

    total_cal = sum(float(l.calories_consumed) for l in logs)
    total_protein = sum(float(l.protein_consumed_g) for l in logs)
    total_carbs = sum(float(l.carbs_consumed_g) for l in logs)
    total_fats = sum(float(l.fats_consumed_g) for l in logs)
    total_fiber = sum(float(l.fiber_consumed_g) for l in logs)

    water_today = db.query(func.sum(WaterLog.amount_ml)).filter(
        WaterLog.user_id == current_user.id,
        cast(WaterLog.logged_at, Date) == today,
    ).scalar() or 0

    profile = db.query(UserHealthProfile).filter(UserHealthProfile.user_id == current_user.id).first()
    calorie_goal = profile.daily_calorie_goal if profile else 2000
    protein_goal = profile.daily_protein_goal if profile else 150
    carbs_goal = profile.daily_carbs_goal if profile else 200
    fats_goal = profile.daily_fats_goal if profile else 65
    fiber_goal = profile.daily_fiber_goal if profile else 25

    return {
        "date": str(today),
        "calories_consumed": round(total_cal, 2),
        "calories_goal": calorie_goal,
        "macros": {
            "protein": {"consumed": round(total_protein, 2), "goal": protein_goal, "unit": "g"},
            "carbs": {"consumed": round(total_carbs, 2), "goal": carbs_goal, "unit": "g"},
            "fats": {"consumed": round(total_fats, 2), "goal": fats_goal, "unit": "g"},
            "fiber": {"consumed": round(total_fiber, 2), "goal": fiber_goal, "unit": "g"},
        },
        "water_intake_ml": int(water_today),
        "meals_logged": len(logs),
    }


@router.post("/weight-logs", response_model=WeightLogResponse, status_code=201)
def log_weight(body: WeightLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log = WeightLog(user_id=current_user.id, weight_kg=body.weight_kg, notes=body.notes)
    db.add(log)
    if current_user.health_profile:
        current_user.health_profile.weight_kg = body.weight_kg
        current_user.health_profile.bmi = calculate_bmi(body.weight_kg, float(current_user.health_profile.height_cm or 170))
    db.commit()
    db.refresh(log)
    return log


@router.get("/weight-logs")
def get_weight_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(WeightLog).filter(WeightLog.user_id == current_user.id).order_by(WeightLog.logged_at.desc()).limit(30).all()
    return [WeightLogResponse.model_validate(l) for l in logs]


@router.post("/dietician-profile")
def create_dietician_profile(
    body: DieticianProfileCreate,
    current_user: User = Depends(require_role("dietician")),
    db: Session = Depends(get_db),
):
    if db.query(DieticianProfile).filter(DieticianProfile.user_id == current_user.id).first():
        raise HTTPException(status_code=409, detail="Profile already exists")
    profile = DieticianProfile(user_id=current_user.id, **body.model_dump())
    db.add(profile)
    db.commit()
    return {"message": "Dietician profile submitted for verification"}


@router.post("/doctor-profile")
def create_doctor_profile(
    body: DoctorProfileCreate,
    current_user: User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    if db.query(DoctorProfile).filter(DoctorProfile.user_id == current_user.id).first():
        raise HTTPException(status_code=409, detail="Profile already exists")
    profile = DoctorProfile(user_id=current_user.id, **body.model_dump())
    db.add(profile)
    db.commit()
    return {"message": "Doctor profile submitted for verification"}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.put("/change-password")
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.utils.security import hash_password, verify_password
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
