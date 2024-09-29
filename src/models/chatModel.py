from sqlalchemy import Column, DateTime, String, Boolean, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from enum import Enum as enum
from ..db.db import Base
from datetime import datetime

class RoomUsers(Base):
    __tablename__ = "room_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("room.id"), nullable=False)
    
    room = relationship("Room", back_populates="room_users")
    user = relationship("User", back_populates="room_users")

class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())
    
    messages = relationship("Message", back_populates="room")
    room_users = relationship("RoomUsers", back_populates="room")

class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    room_id = Column(Integer, ForeignKey("room.id"), nullable=False)
    sender_id = Column(Integer,ForeignKey("user.id"), nullable=False)
    receiver_id = Column(Integer,ForeignKey("user.id"), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow())
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow())
    
    media = relationship("MediaMessage", back_populates="message")
    room = relationship("Room", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id],back_populates="message_sender")
    receiver = relationship("User", foreign_keys=[receiver_id],back_populates="message_receiver")
    
class MediaMessage(Base):
    __tablename__ = "media_message"

    id = Column(Integer, primary_key=True)
    type = Column(String)  # Type of media (image, video, etc.)
    url = Column(String)
    message_id = Column(Integer, ForeignKey("message.id"))

    message = relationship("Message", back_populates="media")

    def __repr__(self) -> str:
        return f"media {self.message_id}-{self.type}-{self.url}"