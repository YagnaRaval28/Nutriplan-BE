import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, ARRAY, Text, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class FoodCategory(Base):
    __tablename__ = "food_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    icon = Column(String(10))

    food_items = relationship("FoodItem", back_populates="category")


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    name_hindi = Column(String(200))
    brand = Column(String(100))
    barcode = Column(String(50))
    category_id = Column(Integer, ForeignKey("food_categories.id"))
    serving_size = Column(Numeric(8, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    calories = Column(Numeric(8, 2), nullable=False, default=0)
    protein_g = Column(Numeric(8, 2), default=0)
    carbs_g = Column(Numeric(8, 2), default=0)
    fats_g = Column(Numeric(8, 2), default=0)
    fiber_g = Column(Numeric(8, 2), default=0)
    sugar_g = Column(Numeric(8, 2), default=0)
    sodium_mg = Column(Numeric(8, 2), default=0)
    is_vegetarian = Column(Boolean, default=True)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    common_allergens = Column(ARRAY(Text))
    is_custom = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    image_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("FoodCategory", back_populates="food_items")
    food_logs = relationship("FoodLog", back_populates="food_item")


class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_item_id = Column(UUID(as_uuid=True), ForeignKey("food_items.id"), nullable=False)
    meal_type = Column(String(20), nullable=False)
    quantity = Column(Numeric(8, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    calories_consumed = Column(Numeric(8, 2), nullable=False, default=0)
    protein_consumed_g = Column(Numeric(8, 2), default=0)
    carbs_consumed_g = Column(Numeric(8, 2), default=0)
    fats_consumed_g = Column(Numeric(8, 2), default=0)
    fiber_consumed_g = Column(Numeric(8, 2), default=0)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="food_logs")
    food_item = relationship("FoodItem", back_populates="food_logs")


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount_ml = Column(Integer, nullable=False)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())
