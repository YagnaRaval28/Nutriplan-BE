from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class SendMessageRequest(BaseModel):
    receiver_id: UUID
    content: str


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    sent_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: UUID
    other_user_id: UUID
    other_user_name: str
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    unread_count: int
