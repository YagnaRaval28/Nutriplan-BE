# Product Requirements Document (PRD)
# NutriPlan AI — Recipe & Diet Planner Platform

**Version:** 1.1
**Date:** 2026-05-09
**Status:** Draft
**Note:** Web-first product. Mobile app is Phase 3. All tools used are free/open-source.

---

## 1. Product Vision

NutriPlan AI is a multi-role health and nutrition platform that connects users with professional dieticians and doctors, powered by AI-driven recipe generation and meal planning. The platform enables everyday users to track their diet, calculate macros and calories, and get personalized AI-generated recipes — while giving health professionals a powerful portal to manage their clients and patients remotely.

---

## 2. Problem Statement

- People struggle to track their daily food intake and understand their nutritional needs.
- Dieticians and doctors lack a digital tool to remotely assign and monitor diet plans for their clients/patients.
- Gym enthusiasts and fitness-focused users need precise macro tracking with AI support.
- There is no single platform that brings together users, dieticians, doctors, and AI in one seamless experience.

---

## 3. Target Audience

| Persona | Description |
|---------|-------------|
| General User | Anyone wanting to manage diet, track calories, or lose/gain weight |
| Gym Enthusiast | Fitness-focused users who need precise macro tracking |
| Dietician | Licensed nutrition professional managing multiple clients |
| Doctor | Medical professional suggesting diet plans for patients |
| Super Admin | Platform administrator managing all users and operations |

---

## 4. User Roles & Permissions

### 4.1 General User
- Register and create a personal health profile
- Log daily food intake manually or via AI food recognition
- Track calories and macros (protein, carbs, fats, fiber, sugar)
- View assigned diet plans from dieticians/doctors
- Generate AI-powered recipes based on their preferences and goals
- View weekly and monthly health and nutrition reports
- Message their assigned dietician
- Manage subscription plan

### 4.2 Dietician
- Register and get verified by Super Admin
- Create and manage a client list
- Build and assign customized diet plans to clients
- Define meal schedules (breakfast, lunch, dinner, snacks) by day
- Monitor client progress (calorie logs, weight trend)
- Message clients directly in the platform
- View client weekly/monthly reports

### 4.3 Doctor
- Register and get verified by Super Admin
- Search and link patients by user ID or email
- Suggest diet plans associated with specific medical conditions
- View patient health history and food logs
- Add medical notes to patient profiles

### 4.4 Super Admin
- Approve or reject dietician and doctor registrations
- View and manage all platform users
- Access platform-wide analytics (active users, revenue, subscriptions)
- Manage the food database (add, edit, remove items)
- Configure subscription plans and pricing
- Handle support escalations

---

## 5. Core Features

### 5.1 User Authentication & Profiles
- Email/password registration with email verification
- OAuth login (Google)
- Role-based access control (user, dietician, doctor, admin)
- Health profile setup: age, weight, height, gender, health goals, allergies, medical conditions
- Profile photo upload

### 5.2 Food Database & Search
- Searchable food database with 500,000+ items
- Each item has: calories, protein, carbs, fats, fiber, sugar, sodium per serving
- Support for custom serving sizes and units (grams, oz, cups, pieces)
- Barcode scanner support (mobile)
- User can add custom food items

### 5.3 Food Logging & Macro Tracking
- Log meals by meal type: Breakfast, Lunch, Dinner, Snacks
- Real-time daily macro and calorie summary
- Visual progress bars for daily goals
- Water intake tracking
- Historical log view by date

### 5.4 Diet Plan Management
- Dietician/Doctor creates a structured diet plan
- Plan contains daily meal schedules for a date range
- Each meal lists specific food items with quantities
- Plan assigned to a specific user/patient
- User receives notification when a plan is assigned
- User can view active plan in their dashboard

### 5.5 AI Recipe Generation (LangGraph)
- User inputs preferences: cuisine type, dietary restriction, available ingredients, calorie target
- LangGraph agent processes user profile + preferences
- AI generates a detailed recipe: ingredients, steps, cook time, servings
- AI calculates full nutritional breakdown for the recipe
- Recipe can be saved to favorites or added directly to food log
- AI can suggest a full weekly meal plan

### 5.6 Reports & Analytics

**For Users:**
- Daily calorie and macro summary
- Weekly report: calorie trend, goal achievement, top foods consumed
- Monthly report: weight progress, average daily intake, streak tracking
- Comparison charts (actual vs. goal)

**For Dieticians:**
- Client progress overview
- Client adherence rate to diet plan
- Client calorie and macro trend over time

**For Admins:**
- Total users, active users, new signups
- Revenue and subscription breakdown
- Platform usage statistics

### 5.7 Messaging
- In-app direct messaging between user and their dietician
- Notification for new messages (email + push)
- Message history stored per conversation

### 5.8 Notifications
- Email: welcome, email verification, new diet plan assigned, weekly report
- Push (mobile): meal reminders, daily log reminder, message received
- In-app: system alerts, plan updates

### 5.9 Subscription & Payments
- Stripe-powered subscription billing
- Multiple plans: Free, Basic, Pro, Dietician, Dietician Pro
- Secure payment flow via Stripe Checkout
- Subscription management: upgrade, downgrade, cancel
- Webhook-based real-time status updates
- Invoice history available in user account

---

## 6. Subscription Plans

| Plan | Price | Target | Key Features |
|------|-------|--------|--------------|
| Free | $0/month | General users | Calorie tracking, 3 AI recipes/month, 7-day history |
| Basic | $9.99/month | Regular users | Unlimited tracking, 20 AI recipes/month, weekly reports |
| Pro | $19.99/month | Serious users | Everything in Basic + dietician access, monthly reports, food photo AI |
| Dietician Starter | $49.99/month | Dieticians | Manage up to 50 clients, client reports |
| Dietician Pro | $99.99/month | Dieticians | Unlimited clients, advanced analytics, priority support |

---

## 7. User Flows

### 7.1 New User Onboarding
```
Register → Verify Email → Complete Health Profile → Choose Subscription Plan → Dashboard
```

### 7.2 Daily Food Logging
```
Open App → Add Food Log → Search Food Item → Select Serving Size → Log → View Daily Summary
```

### 7.3 AI Recipe Generation
```
Click "Generate Recipe" → Fill Preferences Form → AI Processes Request → View Recipe + Macros → Save or Log Recipe
```

### 7.4 Dietician Assigns Diet Plan
```
Dietician Login → Select Client → Create Diet Plan → Add Meals per Day → Assign Plan → Client Gets Notified
```

### 7.5 Doctor Suggests Diet
```
Doctor Login → Search Patient → View Patient Profile → Create Diet Suggestion → Link to Medical Condition → Save
```

### 7.6 Subscription Purchase
```
User Views Plans → Selects Plan → Stripe Checkout → Payment Success → Webhook Updates DB → Access Unlocked
```

---

## 8. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Performance | API response time < 300ms for standard endpoints |
| AI Response | Recipe generation < 10 seconds |
| Uptime | 99.9% availability |
| Security | All passwords hashed (bcrypt), JWT authentication, HTTPS only |
| Data Privacy | GDPR and HIPAA-aligned data handling for medical data |
| Scalability | Docker-based, deployable on Render.com free tier |
| Platform | Web-first (responsive). Mobile app is Phase 3. |

---

## 9. Development Phases

### Phase 1 — MVP Web (Months 1–3)
- [ ] Project setup (FastAPI + Next.js + PostgreSQL + Docker)
- [ ] User authentication (register, login, email verify via Resend)
- [ ] Health profile setup (goals, allergies, medical conditions)
- [ ] Food database integration (Open Food Facts API)
- [ ] Manual food logging and macro tracking
- [ ] Basic AI recipe generation (LangGraph + Groq free LLM)
- [ ] Dietician portal (create and assign diet plans)
- [ ] Weekly nutrition reports (web dashboard with charts)
- [ ] Fully free stack — no payment integration yet

### Phase 2 — Core Web Product (Months 3–5)
- [ ] Doctor portal
- [ ] Super Admin dashboard
- [ ] Monthly reports and advanced analytics
- [ ] In-app messaging (user ↔ dietician via WebSocket)
- [ ] Email notifications (Resend.com)
- [ ] Image upload for profile photos (Cloudinary free)
- [ ] Stripe payment integration (subscription plans — activate when ready)

### Phase 3 — Growth & Mobile (Months 5–8)
- [ ] Flutter mobile app (iOS + Android)
- [ ] Food photo calorie detection via AI (image upload)
- [ ] Push notifications (Firebase — free tier)
- [ ] Dietician marketplace (users browse and hire dieticians)
- [ ] Advanced AI meal planning (weekly + monthly auto-generate)
- [ ] Barcode scanner for food logging (mobile only)

---

## 10. Success Metrics

| Metric | Target (Month 6) |
|--------|-----------------|
| Registered Users | 5,000+ |
| Active Dieticians | 100+ |
| Daily Active Users | 1,000+ |
| Paid Subscribers | 500+ |
| Monthly Revenue | $10,000+ |
| AI Recipes Generated | 50,000+ |
| App Store Rating | 4.5+ |

---

## 11. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Medical data privacy breach | HIPAA-aligned storage, encrypted fields, audit logs |
| AI generating incorrect dietary advice | Disclaimer added, dietician review option |
| Low dietician adoption | Offer free plan for dieticians during beta |
| Payment failure handling | Stripe retry logic + grace period for subscriptions |
| Food database gaps | Integration with Open Food Facts API as fallback |

---

*Document Owner: Product Team*  
*Last Updated: 2026-05-07*
