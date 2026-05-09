# Payment & Subscription Guide
# NutriPlan AI — Monetization & Billing

**Version:** 1.0  
**Date:** 2026-05-07  
**Payment Provider:** Stripe

---

## 1. Subscription Plans

### User Plans

| Plan | Monthly Price | Annual Price | Best For |
|------|-------------|-------------|----------|
| Free | $0 | $0 | Casual users trying the app |
| Basic | $9.99 | $95.99 (20% off) | Regular health-conscious users |
| Pro | $19.99 | $191.99 (20% off) | Serious fitness & diet management |

### Professional Plans

| Plan | Monthly Price | Annual Price | Best For |
|------|-------------|-------------|----------|
| Dietician Starter | $49.99 | $479.99 (20% off) | New dieticians, up to 50 clients |
| Dietician Pro | $99.99 | $959.99 (20% off) | Established dieticians, unlimited clients |

---

## 2. Feature Comparison

| Feature | Free | Basic | Pro | Dietician Starter | Dietician Pro |
|---------|------|-------|-----|-------------------|---------------|
| Calorie tracking | ✓ | ✓ | ✓ | — | — |
| Food logging | ✓ | ✓ | ✓ | — | — |
| AI recipe generation | 3/month | 20/month | Unlimited | — | — |
| Weekly reports | 7-day history | ✓ | ✓ | — | — |
| Monthly reports | ✗ | ✗ | ✓ | — | — |
| Dietician access | ✗ | ✗ | ✓ | — | — |
| Food photo AI | ✗ | ✗ | ✓ | — | — |
| In-app messaging | ✗ | ✓ | ✓ | ✓ | ✓ |
| Clients manageable | — | — | — | 50 | Unlimited |
| Client progress reports | — | — | — | ✓ | ✓ |
| Advanced analytics | — | — | — | ✗ | ✓ |
| Priority support | ✗ | ✗ | ✗ | ✗ | ✓ |

---

## 3. Stripe Integration Flow

### Step 1 — Create Stripe Products & Prices
Each plan is a Stripe Product with a Price attached.

```
Stripe Dashboard:
  Product: "NutriPlan Basic"
    → Price: $9.99/month  (price_id: price_basic_monthly)
    → Price: $95.99/year  (price_id: price_basic_annual)

  Product: "NutriPlan Pro"
    → Price: $19.99/month (price_id: price_pro_monthly)
    → Price: $191.99/year (price_id: price_pro_annual)
```

### Step 2 — User Selects Plan (Frontend)
```
User clicks "Upgrade to Pro"
   ↓
Frontend calls: POST /subscriptions/create { plan_id: "pro" }
```

### Step 3 — Backend Creates Checkout Session
```python
import stripe

stripe.api_key = STRIPE_SECRET_KEY

# Create or retrieve Stripe customer
customer = stripe.Customer.create(
    email=user.email,
    name=user.name,
    metadata={"user_id": str(user.id)}
)

# Create checkout session
session = stripe.checkout.Session.create(
    customer=customer.id,
    payment_method_types=["card"],
    line_items=[{"price": "price_pro_monthly", "quantity": 1}],
    mode="subscription",
    success_url="https://nutriplan.ai/dashboard?success=true",
    cancel_url="https://nutriplan.ai/plans?cancelled=true",
    metadata={"user_id": str(user.id), "plan_id": "pro"}
)

return {"checkout_url": session.url}
```

### Step 4 — User Completes Payment on Stripe
Stripe handles all card collection securely (PCI compliant). NutriPlan never sees raw card data.

### Step 5 — Stripe Sends Webhook
```
POST /payments/webhook
Headers: stripe-signature: t=...,v1=...

Event: checkout.session.completed
```

### Step 6 — Backend Processes Webhook
```python
@router.post("/payments/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Verify webhook signature
    event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_WEBHOOK_SECRET
    )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        subscription_id = session["subscription"]

        # Activate subscription in DB
        await activate_user_subscription(user_id, subscription_id)

    elif event["type"] == "invoice.payment_succeeded":
        # Renew subscription for next period
        await renew_subscription(event["data"]["object"])

    elif event["type"] == "invoice.payment_failed":
        # Mark as past_due, notify user
        await mark_subscription_past_due(event["data"]["object"])

    elif event["type"] == "customer.subscription.deleted":
        # Cancel subscription access
        await cancel_user_subscription(event["data"]["object"])
```

---

## 4. Subscription Lifecycle

```
User Signs Up
     │
     ▼
[Free Plan] ──────────────────► [Cancels] → Back to Free
     │
     │ Upgrades
     ▼
[Paid Plan: Active]
     │
     ├── Monthly renewal → [invoice.payment_succeeded] → Stays Active
     │
     ├── Payment fails → [invoice.payment_failed] → [Past Due]
     │                                                     │
     │                         Retry (3 attempts, 7 days)  │
     │                         ┌───────── Retries ─────────┘
     │                         │
     │                         ├── Payment succeeds → Back to Active
     │                         └── All retries fail → [Cancelled]
     │
     └── User cancels → [cancel_at_period_end = true]
                            │
                            ▼
                      Access until period end
                            │
                            ▼
                      [Cancelled] → Downgraded to Free
```

---

## 5. Webhook Events to Handle

| Stripe Event | Action |
|-------------|--------|
| `checkout.session.completed` | Activate subscription, unlock features |
| `invoice.payment_succeeded` | Renew subscription for next billing period |
| `invoice.payment_failed` | Mark as `past_due`, send payment failure email |
| `customer.subscription.updated` | Handle plan upgrade/downgrade |
| `customer.subscription.deleted` | Cancel subscription, downgrade to Free |
| `charge.refunded` | Log refund, optionally revoke access |

---

## 6. Plan Upgrade / Downgrade

**Upgrading (e.g., Basic → Pro):**
- Stripe prorates the difference immediately
- New features unlock right away

**Downgrading (e.g., Pro → Basic):**
- Change takes effect at next billing period end
- User keeps Pro access until then

```python
# Upgrade subscription
stripe.Subscription.modify(
    stripe_subscription_id,
    items=[{"id": current_item_id, "price": new_price_id}],
    proration_behavior="create_prorations"
)
```

---

## 7. Cancellation Policy

- Users can cancel anytime from account settings
- Access continues until the current billing period ends
- No refunds for partial months (can add 7-day refund policy optionally)
- After cancellation, account downgrades to Free plan

---

## 8. Trial Period (Optional — Recommended for Launch)

Offer a **14-day free trial** on Basic and Pro plans:

```python
session = stripe.checkout.Session.create(
    subscription_data={
        "trial_period_days": 14
    },
    ...
)
```

- No card charge during trial
- User gets full plan access
- Email sent 3 days before trial ends
- Auto-charges when trial ends if card saved

---

## 9. Revenue Projections

### Conservative Scenario (Month 6)
| Plan | Users | Monthly Revenue |
|------|-------|----------------|
| Free | 4,200 | $0 |
| Basic | 500 | $4,995 |
| Pro | 300 | $5,997 |
| Dietician Starter | 60 | $2,999 |
| Dietician Pro | 30 | $2,999 |
| **Total** | **5,090** | **$16,990/month** |

### Annual Revenue (Year 1 Target): ~$120,000–$200,000

---

## 10. Future Monetization Options

| Option | Description | Timeline |
|--------|-------------|----------|
| Dietician Marketplace | Users browse and book dietician consultations (platform takes 15% commission) | Phase 3 |
| One-time AI meal plan | Buy a custom 4-week AI meal plan for $29.99 without subscription | Phase 2 |
| Corporate Wellness | B2B plan for companies offering NutriPlan to employees | Phase 3 |
| White-label | License the platform to hospitals or wellness brands | Phase 4 |
| Premium Food Database | Restaurants and brands pay to list verified nutritional data | Phase 3 |

---

## 11. Refund Policy (Recommended)

- **7-day money-back guarantee** for new subscribers (easy goodwill builder)
- No refunds after 7 days
- Refunds processed via Stripe in 5–10 business days
- Refund handled via: `stripe.Refund.create(charge=charge_id)`

---

*Last Updated: 2026-05-07*
