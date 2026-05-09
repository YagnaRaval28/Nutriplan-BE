from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.user import User
from app.models.payment import SubscriptionPlan, UserSubscription, PaymentHistory
from app.schemas.payment import CreateSubscriptionRequest, UpgradeSubscriptionRequest
from app.utils.security import get_current_user
from app.config import settings

router = APIRouter()


def _get_stripe():
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def _get_or_create_stripe_customer(stripe, user: User, sub: UserSubscription):
    if sub and sub.stripe_customer_id:
        return sub.stripe_customer_id
    customer = stripe.Customer.create(email=user.email, name=user.name, metadata={"user_id": str(user.id)})
    return customer.id


@router.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    return [
        {
            "id": str(p.id), "plan_key": p.plan_key, "name": p.name,
            "price": float(p.price), "currency": p.currency, "interval": p.interval,
            "features": p.features or [], "ai_recipes_per_month": p.ai_recipes_per_month,
            "max_clients": p.max_clients, "target_role": p.target_role,
        }
        for p in plans
    ]


@router.post("/create")
def create_subscription(
    body: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.plan_key == body.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if float(plan.price) == 0:
        sub = db.query(UserSubscription).filter(UserSubscription.user_id == current_user.id).first()
        if not sub:
            sub = UserSubscription(user_id=current_user.id, plan_id=plan.id, status="active")
            db.add(sub)
        else:
            sub.plan_id = plan.id
            sub.status = "active"
        db.commit()
        return {"message": "Free plan activated"}

    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Payment not configured yet. Contact admin.")

    stripe = _get_stripe()
    sub = db.query(UserSubscription).filter(UserSubscription.user_id == current_user.id).first()
    customer_id = _get_or_create_stripe_customer(stripe, current_user, sub)

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
        mode="subscription",
        success_url="http://localhost:3001/dashboard?success=true",
        cancel_url="http://localhost:3001/subscriptions?cancelled=true",
        metadata={"user_id": str(current_user.id), "plan_key": plan.plan_key},
    )

    if not sub:
        sub = UserSubscription(user_id=current_user.id, plan_id=plan.id,
                               stripe_customer_id=customer_id, status="incomplete")
        db.add(sub)
    else:
        sub.stripe_customer_id = customer_id
    db.commit()

    return {"checkout_url": session.url, "session_id": session.id}


@router.put("/upgrade")
def upgrade_subscription(
    body: UpgradeSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = db.query(UserSubscription).filter(UserSubscription.user_id == current_user.id).first()
    if not sub or not sub.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active Stripe subscription to upgrade")

    new_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.plan_key == body.new_plan_id).first()
    if not new_plan or not new_plan.stripe_price_id:
        raise HTTPException(status_code=404, detail="Plan not found")

    stripe = _get_stripe()
    stripe_sub = stripe.Subscription.retrieve(sub.stripe_subscription_id)
    stripe.Subscription.modify(
        sub.stripe_subscription_id,
        items=[{"id": stripe_sub["items"]["data"][0]["id"], "price": new_plan.stripe_price_id}],
        proration_behavior="create_prorations",
    )
    sub.plan_id = new_plan.id
    db.commit()
    return {"message": f"Upgraded to {new_plan.name}"}


@router.delete("/cancel")
def cancel_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sub = db.query(UserSubscription).filter(UserSubscription.user_id == current_user.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription")

    if sub.stripe_subscription_id and settings.STRIPE_SECRET_KEY:
        stripe = _get_stripe()
        stripe.Subscription.modify(sub.stripe_subscription_id, cancel_at_period_end=True)
        sub.cancel_at_period_end = True
    else:
        sub.status = "cancelled"
        sub.cancelled_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Subscription will be cancelled at period end"}


@router.get("/status")
def subscription_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sub = db.query(UserSubscription).filter(UserSubscription.user_id == current_user.id).first()
    if not sub:
        free_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.plan_key == "free").first()
        return {"plan": "free", "plan_name": "Free", "status": "active",
                "current_period_end": None, "cancel_at_period_end": False,
                "ai_recipes_remaining": free_plan.ai_recipes_per_month if free_plan else 3}

    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == sub.plan_id).first()
    from sqlalchemy import func, extract
    count = db.query(func.count()).filter(
        __import__("app.models.ai_recipe", fromlist=["AIRecipeHistory"]).AIRecipeHistory.user_id == current_user.id,
        extract("month", __import__("app.models.ai_recipe", fromlist=["AIRecipeHistory"]).AIRecipeHistory.created_at) == datetime.utcnow().month,
    ).scalar() or 0
    limit = plan.ai_recipes_per_month if plan else 3
    remaining = max(0, limit - count) if limit < 999 else None

    return {
        "plan": plan.plan_key if plan else "free",
        "plan_name": plan.name if plan else "Free",
        "status": sub.status,
        "current_period_end": str(sub.current_period_end) if sub.current_period_end else None,
        "cancel_at_period_end": sub.cancel_at_period_end,
        "ai_recipes_remaining": remaining,
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook not configured")

    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    data = event["data"]["object"]

    if event["type"] == "checkout.session.completed":
        user_id = data["metadata"].get("user_id")
        plan_key = data["metadata"].get("plan_key")
        stripe_sub_id = data.get("subscription")
        if user_id and plan_key:
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.plan_key == plan_key).first()
            sub = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
            if sub and plan:
                sub.plan_id = plan.id
                sub.stripe_subscription_id = stripe_sub_id
                sub.status = "active"
                db.commit()

    elif event["type"] == "invoice.payment_succeeded":
        stripe_sub_id = data.get("subscription")
        sub = db.query(UserSubscription).filter(UserSubscription.stripe_subscription_id == stripe_sub_id).first()
        if sub:
            sub.status = "active"
            db.add(PaymentHistory(
                user_id=sub.user_id, subscription_id=sub.id,
                stripe_invoice_id=data.get("id"),
                amount=data.get("amount_paid", 0) / 100,
                currency=data.get("currency", "usd").upper(),
                status="succeeded", paid_at=datetime.now(timezone.utc),
            ))
            db.commit()

    elif event["type"] == "invoice.payment_failed":
        stripe_sub_id = data.get("subscription")
        sub = db.query(UserSubscription).filter(UserSubscription.stripe_subscription_id == stripe_sub_id).first()
        if sub:
            sub.status = "past_due"
            db.commit()

    elif event["type"] == "customer.subscription.deleted":
        stripe_sub_id = data.get("id")
        sub = db.query(UserSubscription).filter(UserSubscription.stripe_subscription_id == stripe_sub_id).first()
        if sub:
            sub.status = "cancelled"
            sub.cancelled_at = datetime.now(timezone.utc)
            free_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.plan_key == "free").first()
            if free_plan:
                sub.plan_id = free_plan.id
            db.commit()

    return {"received": True}


@router.get("/payments/history")
def payment_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(PaymentHistory).filter(
        PaymentHistory.user_id == current_user.id
    ).order_by(PaymentHistory.created_at.desc()).all()
    return [{"id": str(r.id), "amount": float(r.amount), "currency": r.currency,
             "status": r.status, "paid_at": str(r.paid_at) if r.paid_at else None,
             "created_at": str(r.created_at)} for r in records]
