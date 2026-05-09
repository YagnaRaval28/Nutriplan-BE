# Database Schema
# NutriPlan AI — PostgreSQL Schema Reference

**Database:** PostgreSQL 15+  
**Version:** 1.0  
**Date:** 2026-05-07

---

## Overview

The database is split into logical groups:
1. **Auth & Users** — accounts, roles, profiles
2. **Food & Nutrition** — food database, food logs
3. **Diet Plans** — plans, meals, assignments
4. **AI** — recipe history
5. **Reports** — weekly/monthly report snapshots
6. **Messaging** — in-app chat
7. **Payments** — subscriptions, invoices

---

## 1. Auth & Users

### Table: `users`
Core identity table for all roles.

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255),
    role            VARCHAR(20) NOT NULL CHECK (role IN ('user', 'dietician', 'doctor', 'admin')),
    is_active       BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    profile_photo_url TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Table: `user_health_profiles`
Health and goal data for general users.

```sql
CREATE TABLE user_health_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    age                 INT,
    gender              VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    weight_kg           DECIMAL(5,2),
    height_cm           DECIMAL(5,2),
    bmi                 DECIMAL(4,2),
    health_goals        TEXT[],
    allergies           TEXT[],
    medical_conditions  TEXT[],
    daily_calorie_goal  INT DEFAULT 2000,
    daily_protein_goal  INT DEFAULT 150,
    daily_carbs_goal    INT DEFAULT 200,
    daily_fats_goal     INT DEFAULT 65,
    daily_water_goal_ml INT DEFAULT 2500,
    activity_level      VARCHAR(20) CHECK (activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Table: `dietician_profiles`
Extended profile for dieticians.

```sql
CREATE TABLE dietician_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    license_number      VARCHAR(100) UNIQUE NOT NULL,
    specialization      VARCHAR(100),
    experience_years    INT,
    bio                 TEXT,
    education           TEXT,
    verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'approved', 'rejected')),
    verified_at         TIMESTAMPTZ,
    verified_by         UUID REFERENCES users(id),
    rejection_notes     TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Table: `doctor_profiles`
Extended profile for doctors.

```sql
CREATE TABLE doctor_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    license_number      VARCHAR(100) UNIQUE NOT NULL,
    specialization      VARCHAR(100),
    hospital_name       VARCHAR(200),
    experience_years    INT,
    bio                 TEXT,
    verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'approved', 'rejected')),
    verified_at         TIMESTAMPTZ,
    verified_by         UUID REFERENCES users(id),
    rejection_notes     TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Table: `auth_tokens`
Stores refresh tokens and email verification tokens.

```sql
CREATE TABLE auth_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL,
    token_type  VARCHAR(20) CHECK (token_type IN ('refresh', 'email_verify', 'password_reset')),
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 2. Food & Nutrition

### Table: `food_items`
Central food database.

```sql
CREATE TABLE food_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(200) NOT NULL,
    brand           VARCHAR(100),
    barcode         VARCHAR(50),
    category        VARCHAR(50),
    serving_size    DECIMAL(8,2) NOT NULL,
    unit            VARCHAR(20) NOT NULL,
    calories        DECIMAL(8,2) NOT NULL,
    protein_g       DECIMAL(8,2) DEFAULT 0,
    carbs_g         DECIMAL(8,2) DEFAULT 0,
    fats_g          DECIMAL(8,2) DEFAULT 0,
    fiber_g         DECIMAL(8,2) DEFAULT 0,
    sugar_g         DECIMAL(8,2) DEFAULT 0,
    sodium_mg       DECIMAL(8,2) DEFAULT 0,
    image_url       TEXT,
    is_custom       BOOLEAN DEFAULT FALSE,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_food_items_name ON food_items USING gin(to_tsvector('english', name));
CREATE INDEX idx_food_items_barcode ON food_items(barcode);
```

---

### Table: `food_logs`
Daily food intake records per user.

```sql
CREATE TABLE food_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID REFERENCES users(id) ON DELETE CASCADE,
    food_item_id        UUID REFERENCES food_items(id),
    meal_type           VARCHAR(20) CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    quantity            DECIMAL(8,2) NOT NULL,
    unit                VARCHAR(20) NOT NULL,
    calories_consumed   DECIMAL(8,2) NOT NULL,
    protein_consumed_g  DECIMAL(8,2) DEFAULT 0,
    carbs_consumed_g    DECIMAL(8,2) DEFAULT 0,
    fats_consumed_g     DECIMAL(8,2) DEFAULT 0,
    fiber_consumed_g    DECIMAL(8,2) DEFAULT 0,
    logged_at           TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_food_logs_user_date ON food_logs(user_id, logged_at);
```

---

### Table: `water_logs`
Daily water intake tracking.

```sql
CREATE TABLE water_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    amount_ml   INT NOT NULL,
    logged_at   TIMESTAMPTZ NOT NULL
);
```

---

## 3. Diet Plans

### Table: `diet_plans`
Diet plan created by dietician or doctor.

```sql
CREATE TABLE diet_plans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_name       VARCHAR(200) NOT NULL,
    created_by      UUID REFERENCES users(id),
    assigned_to     UUID REFERENCES users(id),
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    notes           TEXT,
    status          VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_diet_plans_assigned_to ON diet_plans(assigned_to);
```

---

### Table: `diet_plan_meals`
Individual meals within a diet plan.

```sql
CREATE TABLE diet_plan_meals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diet_plan_id    UUID REFERENCES diet_plans(id) ON DELETE CASCADE,
    day_of_week     VARCHAR(10) CHECK (day_of_week IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')),
    meal_type       VARCHAR(20) CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Table: `diet_plan_meal_items`
Food items within each meal of the plan.

```sql
CREATE TABLE diet_plan_meal_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_id         UUID REFERENCES diet_plan_meals(id) ON DELETE CASCADE,
    food_item_id    UUID REFERENCES food_items(id),
    quantity        DECIMAL(8,2) NOT NULL,
    unit            VARCHAR(20) NOT NULL,
    calories        DECIMAL(8,2),
    notes           TEXT
);
```

---

### Table: `dietician_client_links`
Maps dieticians to their clients.

```sql
CREATE TABLE dietician_client_links (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dietician_id    UUID REFERENCES users(id),
    client_id       UUID REFERENCES users(id),
    status          VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    linked_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(dietician_id, client_id)
);
```

---

## 4. AI Recipe History

### Table: `ai_recipe_history`
Stores all AI-generated recipes per user.

```sql
CREATE TABLE ai_recipe_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    prompt_input    JSONB NOT NULL,
    recipe_title    VARCHAR(200),
    recipe_data     JSONB NOT NULL,
    nutrition_data  JSONB,
    is_saved        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_recipes_user ON ai_recipe_history(user_id, created_at DESC);
```

**`recipe_data` JSON structure:**
```json
{
  "title": "Garlic Spinach Chicken Bowl",
  "description": "...",
  "ingredients": [...],
  "steps": [...],
  "cook_time_minutes": 25,
  "servings": 2
}
```

---

## 5. Reports

### Table: `reports`
Pre-generated report snapshots.

```sql
CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    report_type     VARCHAR(20) CHECK (report_type IN ('weekly', 'monthly')),
    period_label    VARCHAR(20),
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    report_data     JSONB NOT NULL,
    generated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reports_user ON reports(user_id, report_type, start_date DESC);
```

---

### Table: `weight_logs`
Tracks user body weight over time.

```sql
CREATE TABLE weight_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    weight_kg   DECIMAL(5,2) NOT NULL,
    logged_at   TIMESTAMPTZ NOT NULL
);
```

---

## 6. Messaging

### Table: `conversations`
One-to-one conversation thread.

```sql
CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_1   UUID REFERENCES users(id),
    participant_2   UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(participant_1, participant_2)
);
```

---

### Table: `messages`
Individual messages in a conversation.

```sql
CREATE TABLE messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id     UUID REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id           UUID REFERENCES users(id),
    content             TEXT NOT NULL,
    sent_at             TIMESTAMPTZ DEFAULT NOW(),
    read_at             TIMESTAMPTZ
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, sent_at DESC);
```

---

## 7. Payments & Subscriptions

### Table: `subscription_plans`
Platform plan configuration (managed by admin).

```sql
CREATE TABLE subscription_plans (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_key            VARCHAR(50) UNIQUE NOT NULL,
    name                VARCHAR(100) NOT NULL,
    price               DECIMAL(10,2) NOT NULL,
    currency            VARCHAR(10) DEFAULT 'USD',
    interval            VARCHAR(20) DEFAULT 'month',
    stripe_price_id     VARCHAR(100),
    features            TEXT[],
    target_role         VARCHAR(20),
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Table: `user_subscriptions`
Active subscription per user.

```sql
CREATE TABLE user_subscriptions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    plan_id                 UUID REFERENCES subscription_plans(id),
    stripe_customer_id      VARCHAR(100),
    stripe_subscription_id  VARCHAR(100) UNIQUE,
    status                  VARCHAR(30) CHECK (status IN ('active', 'past_due', 'cancelled', 'trialing', 'incomplete')),
    current_period_start    TIMESTAMPTZ,
    current_period_end      TIMESTAMPTZ,
    cancel_at_period_end    BOOLEAN DEFAULT FALSE,
    cancelled_at            TIMESTAMPTZ,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Table: `payment_history`
Record of every payment transaction.

```sql
CREATE TABLE payment_history (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID REFERENCES users(id),
    subscription_id         UUID REFERENCES user_subscriptions(id),
    stripe_payment_intent_id VARCHAR(100),
    stripe_invoice_id       VARCHAR(100),
    amount                  DECIMAL(10,2) NOT NULL,
    currency                VARCHAR(10) DEFAULT 'USD',
    status                  VARCHAR(30) CHECK (status IN ('succeeded', 'failed', 'refunded', 'pending')),
    paid_at                 TIMESTAMPTZ,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Indexes Summary

```sql
-- Performance indexes
CREATE INDEX idx_food_logs_user_date       ON food_logs(user_id, logged_at);
CREATE INDEX idx_diet_plans_assigned_to    ON diet_plans(assigned_to);
CREATE INDEX idx_ai_recipes_user           ON ai_recipe_history(user_id, created_at DESC);
CREATE INDEX idx_reports_user              ON reports(user_id, report_type, start_date DESC);
CREATE INDEX idx_messages_conversation     ON messages(conversation_id, sent_at DESC);
CREATE INDEX idx_food_items_name           ON food_items USING gin(to_tsvector('english', name));
CREATE INDEX idx_food_items_barcode        ON food_items(barcode);
```

---

## Redis Usage (Cache Layer)

| Key Pattern | Purpose | TTL |
|-------------|---------|-----|
| `session:{user_id}` | JWT session data | 1 hour |
| `daily_summary:{user_id}:{date}` | Daily macro totals | 1 hour |
| `food_search:{query}` | Search result cache | 10 minutes |
| `rate_limit:{user_id}:{endpoint}` | API rate limiting | 1 minute |
| `ai_recipe_limit:{user_id}:{month}` | Monthly AI recipe counter | 30 days |

---

## ChromaDB (Vector Database)

Used for semantic food and recipe search.

| Collection | Content | Use Case |
|------------|---------|----------|
| `food_embeddings` | Food item descriptions | "find high protein low carb foods" |
| `recipe_embeddings` | AI recipe titles + descriptions | Similar recipe recommendations |
| `diet_plan_embeddings` | Diet plan notes | Suggest similar plans |

---

*Last Updated: 2026-05-07*
