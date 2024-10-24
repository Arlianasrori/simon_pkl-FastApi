from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,DateTime,Enum
from sqlalchemy.orm import relationship
from ..db.db import Base
from datetime import datetime
from enum import Enum as enum

class DataTypeNotificationEnum(enum) :
    ABSEN = "absen"
    PENGAJUAN = "pengajuan"

class Notification(Base):
    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True)
    id_siswa = Column(Integer, ForeignKey('siswa.id'),nullable=True)
    id_dudi = Column(Integer, ForeignKey('dudi.id'),nullable=True)
    id_pembimbing_dudi = Column(Integer, ForeignKey('pembimbing_dudi.id'),nullable=True)
    id_guru_pembimbing = Column(Integer, ForeignKey('guru_pembimbing.id'),nullable=True)
    title = Column(String(255))
    body = Column(String(1500))
    created_at = Column(DateTime, default=datetime.now())

    siswa = relationship("Siswa", back_populates="notifications")
    dudi = relationship("Dudi", back_populates="notifications")
    pembimbing_dudi = relationship("PembimbingDudi", back_populates="notifications")
    guru_pembimbing = relationship("GuruPembimbing", back_populates="notifications")
    reads = relationship("NotificationRead", back_populates="notification")
    data = relationship("NotificationData", back_populates="notification",uselist=False)

class NotificationRead(Base):
    __tablename__ = 'notification_read'

    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notification.id'))
    id_siswa = Column(Integer, ForeignKey('siswa.id'),nullable=True)
    id_pembimbing_dudi = Column(Integer, ForeignKey('pembimbing_dudi.id'),nullable=True)
    id_guru_pembimbing = Column(Integer, ForeignKey('guru_pembimbing.id'),nullable=True)
    is_read = Column(Boolean, default=True)

    notification = relationship("Notification", back_populates="reads")
    siswa = relationship("Siswa", back_populates="notification_reads")
    pembimbing_dudi = relationship("PembimbingDudi", back_populates="notification_reads")
    guru_pembimbing = relationship("GuruPembimbing", back_populates="notification_reads")

class NotificationData(Base) :
    __tablename__ = "notification_data"

    id_notification = Column(Integer,ForeignKey("notification.id"),primary_key=True)
    data_type = Column(Enum(DataTypeNotificationEnum),nullable=False)
    data_id = Column(Integer,nullable=False)

    notification = relationship("Notification", back_populates="data")