from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.db.session import get_db
from app.models.user import User, DieticianProfile, DoctorProfile
from app.models.food import FoodItem, FoodLog
from app.models.payment import UserSubscription, SubscriptionPlan, PaymentHistory
from app.models.ai_recipe import AIRecipeHistory
from app.schemas.food import CustomFoodCreate
from app.utils.security import require_role

router = APIRouter()


@router.get("/users")
def get_all_users(
    role: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total, "page": page,
        "users": [{"id": str(u.id), "name": u.name, "email": u.email,
                   "role": u.role, "is_active": u.is_active,
                   "is_email_verified": u.is_email_verified,
                   "created_at": str(u.created_at)} for u in users],
    }


@router.get("/dieticians")
def get_dieticians(
    status: str = Query(None),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    query = db.query(DieticianProfile, User).join(User, DieticianProfile.user_id == User.id)
    if status:
        query = query.filter(DieticianProfile.verification_status == status)
    rows = query.all()
    return [{"user_id": str(u.id), "name": u.name, "email": u.email,
             "license_number": d.license_number, "specialization": d.specialization,
             "verification_status": d.verification_status,
             "created_at": str(d.created_at)} for d, u in rows]


@router.get("/doctors")
def get_doctors(
    status: str = Query(None),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    query = db.query(DoctorProfile, User).join(User, DoctorProfile.user_id == User.id)
    if status:
        query = query.filter(DoctorProfile.verification_status == status)
    rows = query.all()
    return [{"user_id": str(u.id), "name": u.name, "email": u.email,
             "license_number": d.license_number, "specialization": d.specialization,
             "hospital_name": d.hospital_name,
             "verification_status": d.verification_status} for d, u in rows]


@router.put("/verify/{user_id}")
def verify_professional(
    user_id: str,
    action: str = Query(..., regex="^(approve|reject)$"),
    notes: str = Query(None),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = None
    if user.role == "dietician":
        profile = db.query(DieticianProfile).filter(DieticianProfile.user_id == user_id).first()
    elif user.role == "doctor":
        profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == user_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    profile.verification_status = "approved" if action == "approve" else "rejected"
    profile.verified_at = datetime.utcnow() if action == "approve" else None
    profile.verified_by = current_user.id
    profile.rejection_notes = notes
    db.commit()
    return {"message": f"Profile {profile.verification_status}"}


@router.put("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    return {"user_id": user_id, "is_active": user.is_active}


@router.get("/analytics")
def get_analytics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    total_users = db.query(func.count(User.id)).filter(User.role == "user").scalar()
    total_dieticians = db.query(func.count(User.id)).filter(User.role == "dietician").scalar()
    total_doctors = db.query(func.count(User.id)).filter(User.role == "doctor").scalar()
    new_this_month = db.query(func.count(User.id)).filter(
        extract("month", User.created_at) == now.month,
        extract("year", User.created_at) == now.year,
    ).scalar()
    ai_recipes_total = db.query(func.count(AIRecipeHistory.id)).scalar()

    revenue_this_month = db.query(func.sum(PaymentHistory.amount)).filter(
        PaymentHistory.status == "succeeded",
        extract("month", PaymentHistory.paid_at) == now.month,
        extract("year", PaymentHistory.paid_at) == now.year,
    ).scalar() or 0

    sub_breakdown = db.query(SubscriptionPlan.plan_key, func.count(UserSubscription.id)).join(
        UserSubscription, SubscriptionPlan.id == UserSubscription.plan_id
    ).filter(UserSubscription.status == "active").group_by(SubscriptionPlan.plan_key).all()

    return {
        "total_users": total_users,
        "total_dieticians": total_dieticians,
        "total_doctors": total_doctors,
        "new_signups_this_month": new_this_month,
        "ai_recipes_generated": ai_recipes_total,
        "revenue": {"this_month": float(revenue_this_month), "currency": "USD"},
        "subscriptions_by_plan": {k: v for k, v in sub_breakdown},
    }


@router.post("/food-database", status_code=201)
def add_food_item(
    body: CustomFoodCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    item = FoodItem(**body.model_dump(), is_custom=False, created_by=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": str(item.id), "name": item.name, "message": "Food item added to database"}


@router.delete("/food-database/{food_id}")
def delete_food_item(
    food_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    item = db.query(FoodItem).filter(FoodItem.id == food_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    db.delete(item)
    db.commit()
    return {"message": "Food item deleted"}
