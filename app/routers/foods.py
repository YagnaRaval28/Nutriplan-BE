from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.db.session import get_db
from app.models.food import FoodItem, FoodCategory
from app.models.user import User
from app.schemas.food import FoodItemResponse, FoodSearchResponse, CustomFoodCreate
from app.utils.security import get_current_user

router = APIRouter()


@router.get("/search", response_model=FoodSearchResponse)
def search_foods(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    vegetarian: bool = None,
    vegan: bool = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(FoodItem).filter(
        or_(
            FoodItem.name.ilike(f"%{q}%"),
            FoodItem.name_hindi.ilike(f"%{q}%"),
            FoodItem.brand.ilike(f"%{q}%"),
        )
    )
    if vegetarian is not None:
        query = query.filter(FoodItem.is_vegetarian == vegetarian)
    if vegan is not None:
        query = query.filter(FoodItem.is_vegan == vegan)

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return FoodSearchResponse(
        results=[FoodItemResponse.model_validate(i) for i in items],
        total=total, page=page, limit=limit,
    )


@router.get("/categories")
def get_categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(FoodCategory).all()


@router.get("/{food_id}", response_model=FoodItemResponse)
def get_food_item(food_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    item = db.query(FoodItem).filter(FoodItem.id == food_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    return item


@router.post("/custom", response_model=FoodItemResponse, status_code=201)
def create_custom_food(
    body: CustomFoodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = FoodItem(**body.model_dump(), is_custom=True, created_by=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
