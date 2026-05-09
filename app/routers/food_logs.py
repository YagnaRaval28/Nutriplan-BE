from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date, func

from app.db.session import get_db
from app.models.food import FoodItem, FoodLog, WaterLog
from app.models.user import User
from app.schemas.food import FoodLogCreate, FoodLogResponse, WaterLogCreate, WaterLogResponse
from app.utils.security import get_current_user
from app.utils.calculations import compute_consumed_nutrition

router = APIRouter()


@router.post("", response_model=FoodLogResponse, status_code=201)
def log_food(body: FoodLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    food = db.query(FoodItem).filter(FoodItem.id == body.food_item_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")

    nutrition = compute_consumed_nutrition(food, body.quantity, float(food.serving_size))
    log = FoodLog(
        user_id=current_user.id,
        food_item_id=body.food_item_id,
        meal_type=body.meal_type,
        quantity=body.quantity,
        unit=body.unit,
        logged_at=body.logged_at or datetime.now(timezone.utc),
        **nutrition,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return FoodLogResponse(
        id=log.id, food_item_id=log.food_item_id, food_name=food.name,
        meal_type=log.meal_type, quantity=float(log.quantity), unit=log.unit,
        calories_consumed=float(log.calories_consumed),
        protein_consumed_g=float(log.protein_consumed_g),
        carbs_consumed_g=float(log.carbs_consumed_g),
        fats_consumed_g=float(log.fats_consumed_g),
        fiber_consumed_g=float(log.fiber_consumed_g),
        logged_at=log.logged_at,
    )


@router.get("")
def get_food_logs(
    date_str: str = Query(None, alias="date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    logs = db.query(FoodLog, FoodItem.name).join(FoodItem).filter(
        FoodLog.user_id == current_user.id,
        cast(FoodLog.logged_at, Date) == target_date,
    ).all()

    log_list = []
    totals = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fats_g": 0.0, "fiber_g": 0.0}
    for log, food_name in logs:
        totals["calories"] += float(log.calories_consumed)
        totals["protein_g"] += float(log.protein_consumed_g)
        totals["carbs_g"] += float(log.carbs_consumed_g)
        totals["fats_g"] += float(log.fats_consumed_g)
        totals["fiber_g"] += float(log.fiber_consumed_g)
        log_list.append(FoodLogResponse(
            id=log.id, food_item_id=log.food_item_id, food_name=food_name,
            meal_type=log.meal_type, quantity=float(log.quantity), unit=log.unit,
            calories_consumed=float(log.calories_consumed),
            protein_consumed_g=float(log.protein_consumed_g),
            carbs_consumed_g=float(log.carbs_consumed_g),
            fats_consumed_g=float(log.fats_consumed_g),
            fiber_consumed_g=float(log.fiber_consumed_g),
            logged_at=log.logged_at,
        ))

    return {"date": str(target_date), "logs": log_list, "daily_totals": {**{"date": str(target_date)}, **{k: round(v, 2) for k, v in totals.items()}}}


@router.delete("/{log_id}")
def delete_food_log(log_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log = db.query(FoodLog).filter(FoodLog.id == log_id, FoodLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")
    db.delete(log)
    db.commit()
    return {"message": "Deleted"}


@router.get("/summary")
def get_macro_summary(
    start_date: str = Query(...),
    end_date: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    rows = db.query(
        cast(FoodLog.logged_at, Date).label("log_date"),
        func.sum(FoodLog.calories_consumed).label("calories"),
        func.sum(FoodLog.protein_consumed_g).label("protein_g"),
        func.sum(FoodLog.carbs_consumed_g).label("carbs_g"),
        func.sum(FoodLog.fats_consumed_g).label("fats_g"),
        func.sum(FoodLog.fiber_consumed_g).label("fiber_g"),
    ).filter(
        FoodLog.user_id == current_user.id,
        cast(FoodLog.logged_at, Date) >= start,
        cast(FoodLog.logged_at, Date) <= end,
    ).group_by(cast(FoodLog.logged_at, Date)).order_by(cast(FoodLog.logged_at, Date)).all()

    return [{"date": str(r.log_date), "calories": round(float(r.calories), 2),
             "protein_g": round(float(r.protein_g), 2), "carbs_g": round(float(r.carbs_g), 2),
             "fats_g": round(float(r.fats_g), 2), "fiber_g": round(float(r.fiber_g), 2)} for r in rows]


@router.post("/water", response_model=WaterLogResponse, status_code=201)
def log_water(body: WaterLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log = WaterLog(user_id=current_user.id, amount_ml=body.amount_ml)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/water/today")
def get_water_today(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(func.sum(WaterLog.amount_ml)).filter(
        WaterLog.user_id == current_user.id,
        cast(WaterLog.logged_at, Date) == date.today(),
    ).scalar() or 0
    return {"date": str(date.today()), "total_ml": int(total)}
