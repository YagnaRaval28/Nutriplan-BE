import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.session import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    report_type = Column(String(20), nullable=False)
    period_label = Column(String(20))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    report_data = Column(JSONB, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
