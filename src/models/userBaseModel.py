from sqlalchemy import Column, Integer,Enum,String
from sqlalchemy.orm import relationship
from ..db.db import Base
from .types import UserTypeEnum


class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    user_type = Column(Enum(UserTypeEnum),nullable=False)
    
    room_users = relationship("RoomUsers", back_populates="user")
    message_sender = relationship("Message", back_populates="sender",foreign_keys="[Message.sender_id]")
    message_receiver = relationship("Message", back_populates="receiver",foreign_keys="[Message.receiver_id]")
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }