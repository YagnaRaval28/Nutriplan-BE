import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, ARRAY, Text, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_key = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False, default=0)
    currency = Column(String(10), default="USD")
    interval = Column(String(20), default="month")
    stripe_price_id = Column(String(100))
    features = Column(ARRAY(Text))
    ai_recipes_per_month = Column(Integer, default=3)
    max_clients = Column(Integer)
    target_role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    stripe_customer_id = Column(String(100))
    stripe_subscription_id = Column(String(100), unique=True)
    status = Column(String(30), default="active")
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    cancelled_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="subscription")
    plan = relationship("SubscriptionPlan")


class PaymentHistory(Base):
    __tablename__ = "payment_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("user_subscriptions.id"))
    stripe_payment_intent_id = Column(String(100))
    stripe_invoice_id = Column(String(100))
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(30))
    paid_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
