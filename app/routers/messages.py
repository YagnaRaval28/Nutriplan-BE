from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.db.session import get_db
from app.models.user import User
from app.models.message import Conversation, Message
from app.schemas.message import SendMessageRequest
from app.utils.security import get_current_user
from datetime import datetime, timezone
from typing import Dict
import json

router = APIRouter()

# In-memory WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active.pop(user_id, None)

    async def send_to(self, user_id: str, data: dict):
        ws = self.active.get(user_id)
        if ws:
            await ws.send_text(json.dumps(data))


manager = ConnectionManager()


def _get_or_create_conversation(db: Session, user1_id, user2_id) -> Conversation:
    conv = db.query(Conversation).filter(
        or_(
            and_(Conversation.participant_1 == user1_id, Conversation.participant_2 == user2_id),
            and_(Conversation.participant_1 == user2_id, Conversation.participant_2 == user1_id),
        )
    ).first()
    if not conv:
        conv = Conversation(participant_1=user1_id, participant_2=user2_id)
        db.add(conv)
        db.flush()
    return conv


@router.post("")
def send_message(body: SendMessageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    receiver = db.query(User).filter(User.id == body.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    conv = _get_or_create_conversation(db, current_user.id, body.receiver_id)
    msg = Message(conversation_id=conv.id, sender_id=current_user.id, content=body.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"id": str(msg.id), "conversation_id": str(msg.conversation_id),
            "sender_id": str(msg.sender_id), "content": msg.content, "sent_at": str(msg.sent_at)}


@router.get("/conversations")
def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convs = db.query(Conversation).filter(
        or_(Conversation.participant_1 == current_user.id, Conversation.participant_2 == current_user.id)
    ).all()

    result = []
    for conv in convs:
        other_id = conv.participant_2 if str(conv.participant_1) == str(current_user.id) else conv.participant_1
        other = db.query(User).filter(User.id == other_id).first()
        last_msg = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.sent_at.desc()).first()
        unread = db.query(Message).filter(
            Message.conversation_id == conv.id,
            Message.sender_id != current_user.id,
            Message.read_at == None,
        ).count()
        result.append({
            "id": str(conv.id),
            "other_user_id": str(other_id),
            "other_user_name": other.name if other else "Unknown",
            "last_message": last_msg.content if last_msg else None,
            "last_message_at": str(last_msg.sent_at) if last_msg else None,
            "unread_count": unread,
        })
    return result


@router.get("/{conversation_id}")
def get_messages(conversation_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conv.participant_1) != str(current_user.id) and str(conv.participant_2) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.sent_at).all()
    # Mark all as read
    for m in msgs:
        if str(m.sender_id) != str(current_user.id) and not m.read_at:
            m.read_at = datetime.now(timezone.utc)
    db.commit()

    return [{"id": str(m.id), "sender_id": str(m.sender_id), "content": m.content,
             "sent_at": str(m.sent_at), "read_at": str(m.read_at) if m.read_at else None} for m in msgs]


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            receiver_id = payload.get("receiver_id")
            content = payload.get("content")
            if receiver_id and content:
                await manager.send_to(receiver_id, {
                    "type": "message",
                    "from": user_id,
                    "content": content,
                })
    except WebSocketDisconnect:
        manager.disconnect(user_id)
