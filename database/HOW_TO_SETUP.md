# Database Setup Guide
# Run these 2 files to get the full database ready

---

## Your PostgreSQL Credentials

```
Host:     localhost
Port:     5432
User:     postgres
Password: Yagna@209
Database: nutriplan   ← we will create this new database
```

---

## Step 1: Create the Database

Open your terminal (CMD or PowerShell) and run:

```bash
psql -U postgres -h localhost -p 5432
```

It will ask for your password → type `Yagna@209`

Then inside psql, run:

```sql
CREATE DATABASE nutriplan;
\q
```

---

## Step 2: Run the Schema File (creates all tables)

In your terminal, navigate to the database folder:

```bash
cd c:\Users\yagna\Recipe_Langgraph\database
```

Then run:

```bash
psql -U postgres -h localhost -p 5432 -d nutriplan -f schema.sql
```

Password: `Yagna@209`

---

## Step 3: Run the Seed File (fills with food data)

```bash
psql -U postgres -h localhost -p 5432 -d nutriplan -f seed.sql
```

Password: `Yagna@209`

---

## Step 4: Verify it worked

```bash
psql -U postgres -h localhost -p 5432 -d nutriplan -c "SELECT COUNT(*) FROM food_items;"
```

You should see **170+** rows.

Also verify categories:

```bash
psql -U postgres -h localhost -p 5432 -d nutriplan -c "SELECT name FROM food_categories;"
```

---

## Your .env File

Create a `.env` file in your project root with these exact values:

```env
PG_HOST=localhost
PG_PORT=5432
PG_DBNAME=nutriplan
PG_USER=postgres
PG_PASSWORD=Yagna@209

DATABASE_URL=postgresql://postgres:Yagna@209@localhost:5432/nutriplan
```

---

## Reset Database (if you want to start fresh)

```bash
psql -U postgres -h localhost -p 5432 -d nutriplan -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -U postgres -h localhost -p 5432 -d nutriplan -f schema.sql
psql -U postgres -h localhost -p 5432 -d nutriplan -f seed.sql
```

---

## What gets created

### Tables (20 total)
| Table | Purpose |
|-------|---------|
| users | All user accounts (user, dietician, doctor, admin) |
| auth_tokens | JWT refresh + email verification tokens |
| user_health_profiles | Weight, height, goals, BMR, TDEE |
| weight_logs | Daily weight tracking |
| dietician_profiles | Dietician license and verification |
| doctor_profiles | Doctor license and verification |
| dietician_client_links | Which dietician manages which user |
| food_categories | 16 food categories |
| food_items | 170+ food items with full nutrition data |
| food_logs | Daily food intake per user |
| water_logs | Daily water intake |
| diet_plans | Plans created by dieticians/doctors |
| diet_plan_meals | Meals within each plan |
| diet_plan_meal_items | Food items within each meal |
| ai_recipe_history | All AI-generated recipes |
| reports | Weekly/monthly report snapshots |
| conversations | Message threads |
| messages | Individual messages |
| subscription_plans | 5 subscription tiers |
| user_subscriptions | Active subscription per user |
| payment_history | All payment records |

### Seed Data included
- **170+ food items** (Indian + International)
- **16 food categories**
- **5 subscription plans** (Free → Dietician Pro)
- **1 Super Admin account**
  - Email: `admin@nutriplan.ai`
  - Password: `Admin@123` ← change this after first login
