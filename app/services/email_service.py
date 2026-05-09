from app.config import settings
import resend


def _send(to: str, subject: str, html: str):
    if not settings.RESEND_API_KEY:
        print(f"[EMAIL - no key] To: {to} | Subject: {subject}")
        return
    resend.api_key = settings.RESEND_API_KEY
    resend.Emails.send({"from": settings.FROM_EMAIL, "to": to, "subject": subject, "html": html})


def send_verification_email(email: str, name: str, token: str):
    link = f"http://localhost:3001/verify-email?token={token}"
    _send(email, "Verify your NutriPlan AI email", f"""
    <h2>Welcome to NutriPlan AI, {name}!</h2>
    <p>Click the link below to verify your email address:</p>
    <a href="{link}" style="background:#22c55e;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;">
      Verify Email
    </a>
    <p>This link expires in 24 hours.</p>
    """)


def send_password_reset_email(email: str, name: str, token: str):
    link = f"http://localhost:3001/reset-password?token={token}"
    _send(email, "Reset your NutriPlan AI password", f"""
    <h2>Password Reset Request</h2>
    <p>Hi {name}, click the link below to reset your password:</p>
    <a href="{link}" style="background:#ef4444;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;">
      Reset Password
    </a>
    <p>This link expires in 2 hours. If you did not request this, ignore this email.</p>
    """)


def send_diet_plan_assigned_email(email: str, name: str, plan_name: str, dietician_name: str):
    _send(email, "New Diet Plan Assigned — NutriPlan AI", f"""
    <h2>New Diet Plan Assigned!</h2>
    <p>Hi {name}, your dietician <strong>{dietician_name}</strong> has assigned you a new diet plan:</p>
    <h3>{plan_name}</h3>
    <p>Login to your NutriPlan AI dashboard to view it.</p>
    <a href="http://localhost:3001/diet-plan" style="background:#22c55e;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;">
      View Diet Plan
    </a>
    """)


def send_weekly_report_email(email: str, name: str, avg_calories: float, goal: int, days_logged: int):
    _send(email, "Your Weekly NutriPlan AI Report", f"""
    <h2>Weekly Report for {name}</h2>
    <p>Here's a summary of your nutrition this week:</p>
    <ul>
      <li>Average daily calories: <strong>{avg_calories} kcal</strong></li>
      <li>Daily calorie goal: <strong>{goal} kcal</strong></li>
      <li>Days logged: <strong>{days_logged}/7</strong></li>
    </ul>
    <p>Keep it up! Login to see your full report.</p>
    <a href="http://localhost:3001/reports" style="background:#6366f1;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;">
      View Full Report
    </a>
    """)
