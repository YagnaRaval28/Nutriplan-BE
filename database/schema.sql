-- =============================================================
-- NutriPlan AI — PostgreSQL Schema
-- Run this file FIRST to create all tables
-- Command: psql -U postgres -d nutriplan -f schema.sql
-- =============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================
-- 1. USERS & AUTH
-- =============================================================

CREATE TABLE IF NOT EXISTS users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(100) NOT NULL,
    email               VARCHAR(255) UNIQUE NOT NULL,
    password_hash       VARCHAR(255),
    role                VARCHAR(20) NOT NULL DEFAULT 'user'
                            CHECK (role IN ('user', 'dietician', 'doctor', 'admin')),
    is_active           BOOLEAN DEFAULT TRUE,
    is_email_verified   BOOLEAN DEFAULT FALSE,
    profile_photo_url   TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auth_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL,
    token_type  VARCHAR(20) NOT NULL
                    CHECK (token_type IN ('refresh', 'email_verify', 'password_reset')),
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================
-- 2. HEALTH PROFILES
-- =============================================================

CREATE TABLE IF NOT EXISTS user_health_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    age                 INT,
    gender              VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    weight_kg           DECIMAL(5,2),
    height_cm           DECIMAL(5,2),
    bmi                 DECIMAL(4,2),
    -- Calculated targets (auto-computed on profile save)
    bmr                 DECIMAL(8,2),   -- Basal Metabolic Rate
    tdee                DECIMAL(8,2),   -- Total Daily Energy Expenditure
    daily_calorie_goal  INT DEFAULT 2000,
    daily_protein_goal  INT DEFAULT 150,   -- grams
    daily_carbs_goal    INT DEFAULT 200,   -- grams
    daily_fats_goal     INT DEFAULT 65,    -- grams
    daily_fiber_goal    INT DEFAULT 25,    -- grams
    daily_water_goal_ml INT DEFAULT 2500,
    -- User goals and restrictions
    health_goal         VARCHAR(30) DEFAULT 'maintain'
                            CHECK (health_goal IN ('weight_loss', 'weight_gain', 'maintain', 'muscle_gain')),
    activity_level      VARCHAR(20) DEFAULT 'moderate'
                            CHECK (activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
    allergies           TEXT[],            -- e.g. ['peanuts', 'gluten']
    medical_conditions  TEXT[],            -- e.g. ['diabetes', 'hypertension']
    diet_type           VARCHAR(30) DEFAULT 'non_vegetarian'
                            CHECK (diet_type IN ('vegetarian', 'vegan', 'non_vegetarian', 'eggetarian', 'keto', 'paleo')),
    cuisine_preferences TEXT[],            -- e.g. ['Indian', 'Mediterranean']
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS weight_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    weight_kg   DECIMAL(5,2) NOT NULL,
    notes       TEXT,
    logged_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- 3. PROFESSIONAL PROFILES
-- =============================================================

CREATE TABLE IF NOT EXISTS dietician_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    license_number      VARCHAR(100) UNIQUE NOT NULL,
    specialization      VARCHAR(100),
    experience_years    INT,
    bio                 TEXT,
    education           TEXT,
    verification_status VARCHAR(20) DEFAULT 'pending'
                            CHECK (verification_status IN ('pending', 'approved', 'rejected')),
    verified_at         TIMESTAMPTZ,
    verified_by         UUID REFERENCES users(id),
    rejection_notes     TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS doctor_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    license_number      VARCHAR(100) UNIQUE NOT NULL,
    specialization      VARCHAR(100),
    hospital_name       VARCHAR(200),
    experience_years    INT,
    bio                 TEXT,
    verification_status VARCHAR(20) DEFAULT 'pending'
                            CHECK (verification_status IN ('pending', 'approved', 'rejected')),
    verified_at         TIMESTAMPTZ,
    verified_by         UUID REFERENCES users(id),
    rejection_notes     TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dietician_client_links (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dietician_id    UUID NOT NULL REFERENCES users(id),
    client_id       UUID NOT NULL REFERENCES users(id),
    status          VARCHAR(20) DEFAULT 'active'
                        CHECK (status IN ('active', 'inactive')),
    linked_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(dietician_id, client_id)
);

-- =============================================================
-- 4. FOOD DATABASE
-- =============================================================

CREATE TABLE IF NOT EXISTS food_categories (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(100) UNIQUE NOT NULL,   -- e.g. 'Grains', 'Protein', 'Dairy'
    icon    VARCHAR(10)                     -- emoji icon e.g. '🌾'
);

CREATE TABLE IF NOT EXISTS food_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(200) NOT NULL,
    name_hindi      VARCHAR(200),           -- Hindi name for Indian foods
    brand           VARCHAR(100),
    barcode         VARCHAR(50),
    category_id     INT REFERENCES food_categories(id),
    -- Serving info
    serving_size    DECIMAL(8,2) NOT NULL,
    unit            VARCHAR(20) NOT NULL,   -- 'g', 'ml', 'piece', 'cup', 'tbsp'
    -- Nutrition per serving
    calories        DECIMAL(8,2) NOT NULL DEFAULT 0,
    protein_g       DECIMAL(8,2) DEFAULT 0,
    carbs_g         DECIMAL(8,2) DEFAULT 0,
    fats_g          DECIMAL(8,2) DEFAULT 0,
    fiber_g         DECIMAL(8,2) DEFAULT 0,
    sugar_g         DECIMAL(8,2) DEFAULT 0,
    sodium_mg       DECIMAL(8,2) DEFAULT 0,
    -- Tags for filtering
    is_vegetarian   BOOLEAN DEFAULT TRUE,
    is_vegan        BOOLEAN DEFAULT FALSE,
    is_gluten_free  BOOLEAN DEFAULT FALSE,
    common_allergens TEXT[],               -- e.g. ['gluten', 'dairy']
    -- Meta
    is_custom       BOOLEAN DEFAULT FALSE, -- TRUE if added by a user
    created_by      UUID REFERENCES users(id),
    image_url       TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_food_items_name_search
    ON food_items USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_food_items_barcode
    ON food_items(barcode);
CREATE INDEX IF NOT EXISTS idx_food_items_category
    ON food_items(category_id);

-- =============================================================
-- 5. FOOD LOGGING
-- =============================================================

CREATE TABLE IF NOT EXISTS food_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    food_item_id        UUID NOT NULL REFERENCES food_items(id),
    meal_type           VARCHAR(20) NOT NULL
                            CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    quantity            DECIMAL(8,2) NOT NULL,
    unit                VARCHAR(20) NOT NULL,
    -- Calculated at log time (quantity / serving_size * nutrition)
    calories_consumed   DECIMAL(8,2) NOT NULL DEFAULT 0,
    protein_consumed_g  DECIMAL(8,2) DEFAULT 0,
    carbs_consumed_g    DECIMAL(8,2) DEFAULT 0,
    fats_consumed_g     DECIMAL(8,2) DEFAULT 0,
    fiber_consumed_g    DECIMAL(8,2) DEFAULT 0,
    logged_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_food_logs_user_date
    ON food_logs(user_id, logged_at DESC);

CREATE TABLE IF NOT EXISTS water_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount_ml   INT NOT NULL,
    logged_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- 6. DIET PLANS
-- =============================================================

CREATE TABLE IF NOT EXISTS diet_plans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_name       VARCHAR(200) NOT NULL,
    created_by      UUID NOT NULL REFERENCES users(id),   -- dietician or doctor
    assigned_to     UUID NOT NULL REFERENCES users(id),   -- user/patient
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    notes           TEXT,
    health_goal     VARCHAR(30),
    status          VARCHAR(20) DEFAULT 'active'
                        CHECK (status IN ('active', 'completed', 'cancelled')),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_diet_plans_assigned_to
    ON diet_plans(assigned_to);

CREATE TABLE IF NOT EXISTS diet_plan_meals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diet_plan_id    UUID NOT NULL REFERENCES diet_plans(id) ON DELETE CASCADE,
    day_of_week     VARCHAR(10) NOT NULL
                        CHECK (day_of_week IN ('monday','tuesday','wednesday','thursday','friday','saturday','sunday')),
    meal_type       VARCHAR(20) NOT NULL
                        CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS diet_plan_meal_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_id         UUID NOT NULL REFERENCES diet_plan_meals(id) ON DELETE CASCADE,
    food_item_id    UUID NOT NULL REFERENCES food_items(id),
    quantity        DECIMAL(8,2) NOT NULL,
    unit            VARCHAR(20) NOT NULL,
    calories        DECIMAL(8,2),
    notes           TEXT
);

-- =============================================================
-- 7. AI RECIPE HISTORY
-- =============================================================

CREATE TABLE IF NOT EXISTS ai_recipe_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- What user asked for
    prompt_input    JSONB NOT NULL,
    -- What AI generated
    recipe_title    VARCHAR(200),
    recipe_data     JSONB NOT NULL,    -- full recipe: ingredients, steps, cook time
    nutrition_data  JSONB,             -- calories, protein, carbs, fats per serving
    -- User actions
    is_saved        BOOLEAN DEFAULT FALSE,
    is_logged       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_recipes_user
    ON ai_recipe_history(user_id, created_at DESC);

-- =============================================================
-- 8. REPORTS
-- =============================================================

CREATE TABLE IF NOT EXISTS reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_type     VARCHAR(20) NOT NULL
                        CHECK (report_type IN ('weekly', 'monthly')),
    period_label    VARCHAR(20),       -- e.g. '2026-W19' or '2026-05'
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    report_data     JSONB NOT NULL,    -- full report snapshot
    generated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_user
    ON reports(user_id, report_type, start_date DESC);

-- =============================================================
-- 9. MESSAGING
-- =============================================================

CREATE TABLE IF NOT EXISTS conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_1   UUID NOT NULL REFERENCES users(id),
    participant_2   UUID NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(participant_1, participant_2)
);

CREATE TABLE IF NOT EXISTS messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id     UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id           UUID NOT NULL REFERENCES users(id),
    content             TEXT NOT NULL,
    sent_at             TIMESTAMPTZ DEFAULT NOW(),
    read_at             TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation
    ON messages(conversation_id, sent_at DESC);

-- =============================================================
-- 10. SUBSCRIPTIONS & PAYMENTS
-- =============================================================

CREATE TABLE IF NOT EXISTS subscription_plans (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_key            VARCHAR(50) UNIQUE NOT NULL,   -- 'free', 'basic', 'pro'
    name                VARCHAR(100) NOT NULL,
    price               DECIMAL(10,2) NOT NULL DEFAULT 0,
    currency            VARCHAR(10) DEFAULT 'USD',
    interval            VARCHAR(20) DEFAULT 'month',
    stripe_price_id     VARCHAR(100),
    features            TEXT[],
    ai_recipes_per_month INT DEFAULT 3,
    max_clients         INT,            -- for dietician plans
    target_role         VARCHAR(20) DEFAULT 'user',
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_subscriptions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id                 UUID NOT NULL REFERENCES subscription_plans(id),
    stripe_customer_id      VARCHAR(100),
    stripe_subscription_id  VARCHAR(100) UNIQUE,
    status                  VARCHAR(30) DEFAULT 'active'
                                CHECK (status IN ('active', 'past_due', 'cancelled', 'trialing', 'incomplete')),
    current_period_start    TIMESTAMPTZ,
    current_period_end      TIMESTAMPTZ,
    cancel_at_period_end    BOOLEAN DEFAULT FALSE,
    cancelled_at            TIMESTAMPTZ,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment_history (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                     UUID NOT NULL REFERENCES users(id),
    subscription_id             UUID REFERENCES user_subscriptions(id),
    stripe_payment_intent_id    VARCHAR(100),
    stripe_invoice_id           VARCHAR(100),
    amount                      DECIMAL(10,2) NOT NULL,
    currency                    VARCHAR(10) DEFAULT 'USD',
    status                      VARCHAR(30)
                                    CHECK (status IN ('succeeded', 'failed', 'refunded', 'pending')),
    paid_at                     TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================
-- DONE
-- =============================================================
-- Tables created:
--   users, auth_tokens
--   user_health_profiles, weight_logs
--   dietician_profiles, doctor_profiles, dietician_client_links
--   food_categories, food_items
--   food_logs, water_logs
--   diet_plans, diet_plan_meals, diet_plan_meal_items
--   ai_recipe_history
--   reports
--   conversations, messages
--   subscription_plans, user_subscriptions, payment_history
-- =============================================================
