# API Specification
# NutriPlan AI — REST API Reference

**Base URL:** `https://api.nutriplan.ai/v1`  
**Auth:** Bearer Token (JWT)  
**Format:** JSON  
**Version:** 1.0

---

## Authentication APIs

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "user"
}
```
**Roles allowed:** `user`, `dietician`, `doctor`

**Response 201:**
```json
{
  "message": "Registration successful. Please verify your email.",
  "user_id": "uuid"
}
```

---

### POST /auth/login
Login and get access token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

---

### POST /auth/refresh-token
Get a new access token using refresh token.

**Request Body:**
```json
{ "refresh_token": "eyJ..." }
```

**Response 200:**
```json
{ "access_token": "eyJ...", "expires_in": 3600 }
```

---

### POST /auth/verify-email
Verify email with token sent to inbox.

**Request Body:**
```json
{ "token": "verification_token_here" }
```

---

### POST /auth/forgot-password
Send a password reset link to email.

**Request Body:**
```json
{ "email": "john@example.com" }
```

---

### POST /auth/reset-password
Reset password using token from email.

**Request Body:**
```json
{
  "token": "reset_token",
  "new_password": "NewSecurePass123!"
}
```

---

### POST /auth/logout
Invalidate the current session token.

**Headers:** `Authorization: Bearer <token>`

---

## User Profile APIs

### GET /users/profile
Get the authenticated user's profile.

**Response 200:**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "age": 28,
  "weight": 75.5,
  "height": 178,
  "gender": "male",
  "health_goals": ["weight_loss", "muscle_gain"],
  "allergies": ["peanuts", "gluten"],
  "medical_conditions": [],
  "daily_calorie_goal": 2000,
  "subscription_plan": "pro",
  "profile_photo_url": "https://...",
  "created_at": "2026-05-07T10:00:00Z"
}
```

---

### PUT /users/profile
Update user profile details.

**Request Body:**
```json
{
  "name": "John Doe",
  "age": 28,
  "weight": 74.0,
  "height": 178,
  "health_goals": ["weight_loss"],
  "allergies": ["peanuts"],
  "daily_calorie_goal": 1800
}
```

---

### GET /users/dashboard
Get the user's daily summary dashboard.

**Response 200:**
```json
{
  "date": "2026-05-07",
  "calories_consumed": 1450,
  "calories_goal": 2000,
  "macros": {
    "protein": { "consumed": 98, "goal": 150, "unit": "g" },
    "carbs": { "consumed": 160, "goal": 200, "unit": "g" },
    "fats": { "consumed": 45, "goal": 65, "unit": "g" },
    "fiber": { "consumed": 18, "goal": 25, "unit": "g" }
  },
  "water_intake_ml": 1200,
  "meals_logged": 3,
  "active_diet_plan": {
    "plan_id": "uuid",
    "plan_name": "Weight Loss Plan",
    "today_meals": []
  }
}
```

---

## Food Database APIs

### GET /foods/search
Search food items from the database.

**Query Params:** `?q=apple&limit=10&page=1`

**Response 200:**
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Apple (Raw)",
      "brand": null,
      "serving_size": 100,
      "unit": "g",
      "calories": 52,
      "protein": 0.3,
      "carbs": 13.8,
      "fats": 0.2,
      "fiber": 2.4,
      "sugar": 10.4,
      "sodium": 1
    }
  ],
  "total": 42,
  "page": 1
}
```

---

### GET /foods/{food_id}
Get a single food item by ID.

---

### POST /foods/custom
User adds a custom food item.

**Request Body:**
```json
{
  "name": "My Protein Shake",
  "serving_size": 300,
  "unit": "ml",
  "calories": 180,
  "protein": 25,
  "carbs": 10,
  "fats": 3,
  "fiber": 1
}
```

---

## Food Log APIs

### POST /food-logs
Log a food item for the current user.

**Request Body:**
```json
{
  "food_item_id": "uuid",
  "meal_type": "breakfast",
  "quantity": 150,
  "unit": "g",
  "logged_at": "2026-05-07T08:30:00Z"
}
```

**Response 201:**
```json
{
  "log_id": "uuid",
  "food_name": "Apple (Raw)",
  "calories_consumed": 78,
  "macros_consumed": {
    "protein": 0.45,
    "carbs": 20.7,
    "fats": 0.3
  }
}
```

---

### GET /food-logs
Get food logs for a specific date.

**Query Params:** `?date=2026-05-07`

**Response 200:**
```json
{
  "date": "2026-05-07",
  "logs": [
    {
      "log_id": "uuid",
      "meal_type": "breakfast",
      "food_name": "Apple (Raw)",
      "quantity": 150,
      "unit": "g",
      "calories": 78,
      "logged_at": "2026-05-07T08:30:00Z"
    }
  ],
  "daily_totals": {
    "calories": 1450,
    "protein": 98,
    "carbs": 160,
    "fats": 45
  }
}
```

---

### DELETE /food-logs/{log_id}
Delete a specific food log entry.

---

### GET /food-logs/summary
Get macro summary for a date range.

**Query Params:** `?start_date=2026-05-01&end_date=2026-05-07`

---

## Diet Plan APIs

### POST /diet-plans
Create a new diet plan. (Dietician/Doctor only)

**Request Body:**
```json
{
  "plan_name": "Weight Loss - Week 1",
  "assigned_to_user_id": "uuid",
  "start_date": "2026-05-10",
  "end_date": "2026-05-16",
  "notes": "Low carb, high protein plan",
  "meals": [
    {
      "day": "monday",
      "meal_type": "breakfast",
      "food_items": [
        { "food_item_id": "uuid", "quantity": 100, "unit": "g" }
      ]
    }
  ]
}
```

---

### GET /diet-plans/mine
Get the active diet plan assigned to the authenticated user.

---

### GET /diet-plans/{plan_id}
Get a specific diet plan by ID.

---

### PUT /diet-plans/{plan_id}
Update an existing diet plan. (Dietician/Doctor only)

---

### DELETE /diet-plans/{plan_id}
Delete a diet plan. (Dietician/Doctor only)

---

### GET /dietician/clients
Get list of clients assigned to the logged-in dietician.

**Response 200:**
```json
{
  "clients": [
    {
      "user_id": "uuid",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "active_plan": "Weight Loss Plan",
      "last_log_date": "2026-05-06",
      "adherence_rate": 85
    }
  ]
}
```

---

### GET /dietician/clients/{user_id}/progress
Get detailed progress report for a specific client.

**Query Params:** `?period=weekly` or `?period=monthly`

---

## AI Recipe APIs

### POST /ai/generate-recipe
Generate an AI recipe based on user preferences.

**Request Body:**
```json
{
  "cuisine_type": "Indian",
  "dietary_preference": "vegetarian",
  "calorie_target": 500,
  "available_ingredients": ["chicken", "spinach", "garlic"],
  "exclude_ingredients": ["peanuts"],
  "meal_type": "lunch",
  "servings": 2
}
```

**Response 200:**
```json
{
  "recipe_id": "uuid",
  "title": "Garlic Spinach Chicken Bowl",
  "description": "A protein-rich, low-carb lunch bowl...",
  "ingredients": [
    { "name": "Chicken breast", "quantity": 200, "unit": "g" },
    { "name": "Spinach", "quantity": 100, "unit": "g" }
  ],
  "steps": [
    "Step 1: Season chicken with salt and pepper...",
    "Step 2: Heat pan over medium heat..."
  ],
  "cook_time_minutes": 25,
  "servings": 2,
  "nutrition_per_serving": {
    "calories": 498,
    "protein": 42,
    "carbs": 12,
    "fats": 18,
    "fiber": 4
  }
}
```

---

### POST /ai/suggest-meal-plan
Generate an AI-powered weekly meal plan.

**Request Body:**
```json
{
  "weekly_calorie_goal": 14000,
  "dietary_preference": "non-vegetarian",
  "cuisine_preferences": ["Indian", "Mediterranean"],
  "exclude_ingredients": ["peanuts", "gluten"]
}
```

**Response 200:**
```json
{
  "plan_id": "uuid",
  "week_start": "2026-05-10",
  "days": {
    "monday": {
      "breakfast": { ... },
      "lunch": { ... },
      "dinner": { ... },
      "snacks": { ... }
    }
  },
  "weekly_totals": {
    "calories": 13850,
    "protein": 980,
    "carbs": 1540,
    "fats": 450
  }
}
```

---

### POST /ai/analyze-food-photo
Upload a food photo for AI calorie estimation. (Pro plan only)

**Request:** Multipart form-data with `image` field.

**Response 200:**
```json
{
  "detected_foods": [
    {
      "name": "Grilled Chicken",
      "estimated_quantity": 150,
      "unit": "g",
      "estimated_calories": 248,
      "confidence": 0.87
    }
  ],
  "total_estimated_calories": 620,
  "note": "Estimates may vary. Review before logging."
}
```

---

### GET /ai/recipes/history
Get list of AI recipes generated by the user.

---

## Report APIs

### GET /reports/weekly
Get a weekly nutrition report.

**Query Params:** `?week=2026-W19`

**Response 200:**
```json
{
  "week": "2026-W19",
  "start_date": "2026-05-04",
  "end_date": "2026-05-10",
  "summary": {
    "avg_daily_calories": 1820,
    "calorie_goal": 2000,
    "goal_achievement_percent": 91,
    "days_logged": 6,
    "streak_days": 4
  },
  "daily_breakdown": [
    {
      "date": "2026-05-04",
      "calories": 1750,
      "protein": 95,
      "carbs": 180,
      "fats": 48
    }
  ],
  "top_foods": ["Chicken Breast", "Brown Rice", "Apple"]
}
```

---

### GET /reports/monthly
Get a monthly nutrition report.

**Query Params:** `?month=2026-05`

---

### GET /reports/progress
Get weight and calorie progress over time.

**Query Params:** `?from=2026-04-01&to=2026-05-07`

---

## Messaging APIs

### POST /messages
Send a message to a user or dietician.

**Request Body:**
```json
{
  "receiver_id": "uuid",
  "content": "Hello, I have a question about my diet plan."
}
```

---

### GET /messages/conversations
Get list of all conversations for the authenticated user.

---

### GET /messages/{conversation_id}
Get all messages in a conversation.

---

## Subscription & Payment APIs

### GET /subscriptions/plans
Get all available subscription plans.

**Response 200:**
```json
{
  "plans": [
    {
      "plan_id": "free",
      "name": "Free",
      "price": 0,
      "currency": "USD",
      "interval": "month",
      "features": ["Calorie tracking", "3 AI recipes/month", "7-day history"]
    },
    {
      "plan_id": "basic",
      "name": "Basic",
      "price": 9.99,
      "currency": "USD",
      "interval": "month",
      "features": ["Unlimited tracking", "20 AI recipes/month", "Weekly reports"]
    }
  ]
}
```

---

### POST /subscriptions/create
Start a new subscription.

**Request Body:**
```json
{ "plan_id": "pro" }
```

**Response 200:**
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_..."
}
```

---

### PUT /subscriptions/upgrade
Upgrade or downgrade the current subscription.

**Request Body:**
```json
{ "new_plan_id": "dietician_pro" }
```

---

### DELETE /subscriptions/cancel
Cancel the current subscription (takes effect at period end).

---

### GET /subscriptions/status
Get the current subscription status for the user.

**Response 200:**
```json
{
  "plan": "pro",
  "status": "active",
  "current_period_end": "2026-06-07T00:00:00Z",
  "cancel_at_period_end": false
}
```

---

### POST /payments/webhook
Stripe webhook endpoint (internal use — called by Stripe).

**Events handled:**
- `checkout.session.completed` → activate subscription
- `invoice.payment_succeeded` → renew subscription
- `invoice.payment_failed` → mark subscription past_due
- `customer.subscription.deleted` → deactivate subscription

---

### GET /payments/history
Get the payment/invoice history for the user.

---

## Admin APIs

### GET /admin/users
Get all users with filters.

**Query Params:** `?role=user&status=active&page=1&limit=20`

---

### GET /admin/dieticians
Get all dieticians with verification status.

---

### GET /admin/doctors
Get all doctors with verification status.

---

### PUT /admin/verify/{user_id}
Approve or reject a dietician/doctor registration.

**Request Body:**
```json
{
  "action": "approve",
  "notes": "License verified successfully."
}
```

---

### GET /admin/analytics
Get platform-wide analytics.

**Response 200:**
```json
{
  "total_users": 5420,
  "active_users_today": 1230,
  "new_signups_this_month": 430,
  "total_dieticians": 112,
  "total_doctors": 45,
  "revenue": {
    "this_month": 12450.00,
    "last_month": 9870.00,
    "currency": "USD"
  },
  "subscriptions_by_plan": {
    "free": 4200,
    "basic": 650,
    "pro": 420,
    "dietician_starter": 90,
    "dietician_pro": 60
  },
  "ai_recipes_generated": 54200
}
```

---

### POST /admin/food-database
Add a new food item to the central database.

---

## Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "You are not authorized to perform this action.",
    "details": null
  }
}
```

**Common HTTP Status Codes:**

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient role/permissions) |
| 404 | Resource not found |
| 409 | Conflict (e.g., email already registered) |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests (rate limit) |
| 500 | Internal Server Error |

---

*Last Updated: 2026-05-07*
