from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class SubscriptionPlanResponse(BaseModel):
    id: UUID
    plan_key: str
    name: str
    price: float
    currency: str
    interval: str
    features: Optional[List[str]]
    ai_recipes_per_month: int
    max_clients: Optional[int]
    target_role: str

    class Config:
        from_attributes = True


class CreateSubscriptionRequest(BaseModel):
    plan_id: str


class UpgradeSubscriptionRequest(BaseModel):
    new_plan_id: str


class SubscriptionStatusResponse(BaseModel):
    plan: str
    plan_name: str
    status: str
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    ai_recipes_remaining: Optional[int]


class PaymentHistoryResponse(BaseModel):
    id: UUID
    amount: float
    currency: str
    status: str
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str
