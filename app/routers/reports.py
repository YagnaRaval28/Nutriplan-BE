from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from app.db.session import get_db
from app.models.user import User, UserHealthProfile
from app.models.food import FoodLog
from app.models.report import Report
from app.utils.security import get_current_user

router = APIRouter()


def _build_daily_breakdown(user_id, start: date, end: date, db: Session):
    rows = db.query(
        cast(FoodLog.logged_at, Date).label("log_date"),
        func.sum(FoodLog.calories_consumed).label("calories"),
        func.sum(FoodLog.protein_consumed_g).label("protein_g"),
        func.sum(FoodLog.carbs_consumed_g).label("carbs_g"),
        func.sum(FoodLog.fats_consumed_g).label("fats_g"),
    ).filter(
        FoodLog.user_id == user_id,
        cast(FoodLog.logged_at, Date) >= start,
        cast(FoodLog.logged_at, Date) <= end,
    ).group_by(cast(FoodLog.logged_at, Date)).order_by(cast(FoodLog.logged_at, Date)).all()
    return [{"date": str(r.log_date), "calories": round(float(r.calories), 2),
             "protein_g": round(float(r.protein_g), 2), "carbs_g": round(float(r.carbs_g), 2),
             "fats_g": round(float(r.fats_g), 2)} for r in rows]


@router.get("/weekly")
def get_weekly_report(
    week: str = Query(None, description="ISO week e.g. 2026-W19"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    if week:
        year, w = week.split("-W")
        start = date.fromisocalendar(int(year), int(w), 1)
    else:
        start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    breakdown = _build_daily_breakdown(current_user.id, start, end, db)
    days_logged = len(breakdown)
    avg_cal = round(sum(d["calories"] for d in breakdown) / days_logged, 2) if days_logged else 0

    profile = db.query(UserHealthProfile).filter(UserHealthProfile.user_id == current_user.id).first()
    calorie_goal = int(profile.daily_calorie_goal) if profile and profile.daily_calorie_goal else 2000
    achievement = round((avg_cal / calorie_goal) * 100, 1) if calorie_goal else 0

    return {
        "week": week or f"{today.isocalendar()[0]}-W{today.isocalendar()[1]}",
        "start_date": str(start), "end_date": str(end),
        "summary": {
            "avg_daily_calories": avg_cal,
            "calorie_goal": calorie_goal,
            "goal_achievement_percent": achievement,
            "days_logged": days_logged,
        },
        "daily_breakdown": breakdown,
    }


@router.get("/monthly")
def get_monthly_report(
    month: str = Query(None, description="Month e.g. 2026-05"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    if month:
        year, m = month.split("-")
        start = date(int(year), int(m), 1)
    else:
        start = date(today.year, today.month, 1)

    if start.month == 12:
        end = date(start.year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(start.year, start.month + 1, 1) - timedelta(days=1)

    breakdown = _build_daily_breakdown(current_user.id, start, end, db)
    days_logged = len(breakdown)
    avg_cal = round(sum(d["calories"] for d in breakdown) / days_logged, 2) if days_logged else 0
    total_calories = round(sum(d["calories"] for d in breakdown), 2)

    return {
        "month": month or f"{today.year}-{today.month:02d}",
        "start_date": str(start), "end_date": str(end),
        "summary": {
            "total_calories_consumed": total_calories,
            "avg_daily_calories": avg_cal,
            "days_logged": days_logged,
            "days_in_month": (end - start).days + 1,
        },
        "daily_breakdown": breakdown,
    }


@router.get("/progress")
def get_progress(
    from_date: str = Query(...),
    to_date: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.user import WeightLog
    start = date.fromisoformat(from_date)
    end = date.fromisoformat(to_date)

    breakdown = _build_daily_breakdown(current_user.id, start, end, db)
    weight_logs = db.query(WeightLog).filter(
        WeightLog.user_id == current_user.id,
        cast(WeightLog.logged_at, Date) >= start,
        cast(WeightLog.logged_at, Date) <= end,
    ).order_by(WeightLog.logged_at).all()

    return {
        "calorie_trend": breakdown,
        "weight_trend": [{"date": str(w.logged_at.date()), "weight_kg": float(w.weight_kg)} for w in weight_logs],
    }
