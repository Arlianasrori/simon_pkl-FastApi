from sqlalchemy import Column, Integer, String
from ..db.db import Base

class Developer(Base):
    __tablename__ = 'developer'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    def __repr__(self):
        return f"<Developer(id={self.id}, username='{self.username}')>"