import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Numeric, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class DietPlan(Base):
    __tablename__ = "diet_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_name = Column(String(200), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    notes = Column(Text)
    health_goal = Column(String(30))
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    meals = relationship("DietPlanMeal", back_populates="diet_plan", cascade="all, delete-orphan")


class DietPlanMeal(Base):
    __tablename__ = "diet_plan_meals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diet_plan_id = Column(UUID(as_uuid=True), ForeignKey("diet_plans.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String(10), nullable=False)
    meal_type = Column(String(20), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    diet_plan = relationship("DietPlan", back_populates="meals")
    items = relationship("DietPlanMealItem", back_populates="meal", cascade="all, delete-orphan")


class DietPlanMealItem(Base):
    __tablename__ = "diet_plan_meal_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meal_id = Column(UUID(as_uuid=True), ForeignKey("diet_plan_meals.id", ondelete="CASCADE"), nullable=False)
    food_item_id = Column(UUID(as_uuid=True), ForeignKey("food_items.id"), nullable=False)
    quantity = Column(Numeric(8, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    calories = Column(Numeric(8, 2))
    notes = Column(Text)

    meal = relationship("DietPlanMeal", back_populates="items")
    food_item = relationship("FoodItem")
