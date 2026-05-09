import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, ARRAY, Text, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    profile_photo_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    health_profile = relationship("UserHealthProfile", back_populates="user", uselist=False)
    dietician_profile = relationship(
        "DieticianProfile", back_populates="user", uselist=False,
        foreign_keys="DieticianProfile.user_id",
    )
    doctor_profile = relationship(
        "DoctorProfile", back_populates="user", uselist=False,
        foreign_keys="DoctorProfile.user_id",
    )
    food_logs = relationship("FoodLog", back_populates="user")
    weight_logs = relationship("WeightLog", back_populates="user")
    subscription = relationship("UserSubscription", back_populates="user", uselist=False)
    auth_tokens = relationship("AuthToken", back_populates="user")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    token_type = Column(String(20), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="auth_tokens")


class UserHealthProfile(Base):
    __tablename__ = "user_health_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    weight_kg = Column(Numeric(5, 2))
    height_cm = Column(Numeric(5, 2))
    bmi = Column(Numeric(4, 2))
    bmr = Column(Numeric(8, 2))
    tdee = Column(Numeric(8, 2))
    daily_calorie_goal = Column(Integer, default=2000)
    daily_protein_goal = Column(Integer, default=150)
    daily_carbs_goal = Column(Integer, default=200)
    daily_fats_goal = Column(Integer, default=65)
    daily_fiber_goal = Column(Integer, default=25)
    daily_water_goal_ml = Column(Integer, default=2500)
    health_goal = Column(String(30), default="maintain")
    activity_level = Column(String(20), default="moderate")
    allergies = Column(ARRAY(Text))
    medical_conditions = Column(ARRAY(Text))
    diet_type = Column(String(30), default="non_vegetarian")
    cuisine_preferences = Column(ARRAY(Text))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="health_profile")


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    weight_kg = Column(Numeric(5, 2), nullable=False)
    notes = Column(Text)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="weight_logs")


class DieticianProfile(Base):
    __tablename__ = "dietician_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    license_number = Column(String(100), unique=True, nullable=False)
    specialization = Column(String(100))
    experience_years = Column(Integer)
    bio = Column(Text)
    education = Column(Text)
    verification_status = Column(String(20), default="pending")
    verified_at = Column(DateTime(timezone=True))
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    rejection_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="dietician_profile", foreign_keys=[user_id])


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    license_number = Column(String(100), unique=True, nullable=False)
    specialization = Column(String(100))
    hospital_name = Column(String(200))
    experience_years = Column(Integer)
    bio = Column(Text)
    verification_status = Column(String(20), default="pending")
    verified_at = Column(DateTime(timezone=True))
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    rejection_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="doctor_profile", foreign_keys=[user_id])


class DieticianClientLink(Base):
    __tablename__ = "dietician_client_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dietician_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="active")
    linked_at = Column(DateTime(timezone=True), server_default=func.now())
