import uuid
from sqlalchemy import Column, Boolean, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.session import Base


class AIRecipeHistory(Base):
    __tablename__ = "ai_recipe_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    prompt_input = Column(JSONB, nullable=False)
    recipe_title = Column(String(200))
    recipe_data = Column(JSONB, nullable=False)
    nutrition_data = Column(JSONB)
    is_saved = Column(Boolean, default=False)
    is_logged = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
