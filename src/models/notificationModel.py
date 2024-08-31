from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..db.db import Base

class Notification(Base):
    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True)
    id_siswa = Column(Integer, ForeignKey('siswa.id'))
    id_dudi = Column(Integer, ForeignKey('dudi.id'))
    id_pembimbing_dudi = Column(Integer, ForeignKey('pembimbing_dudi.id'))
    id_guru_pembimbing = Column(Integer, ForeignKey('guru_pembimbing.id'))
    title = Column(String(255))
    body = Column(String(1500))
    is_read = Column(Boolean, default=False)

    siswa = relationship("Siswa", back_populates="notifications")
    dudi = relationship("Dudi", back_populates="notifications")
    pembimbing_dudi = relationship("PembimbingDudi", back_populates="notifications")
    guru_pembimbing = relationship("GuruPembimbing", back_populates="notifications")

class NotificationRead(Base):
    __tablename__ = 'notification_read'

    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notification.id'))
    id_siswa = Column(Integer, ForeignKey('siswa.id'))
    id_pembimbing_dudi = Column(Integer, ForeignKey('pembimbing_dudi.id'))
    id_guru_pembimbing = Column(Integer, ForeignKey('guru_pembimbing.id'))
    is_read = Column(Boolean, default=False)

    notification = relationship("Notification", back_populates="reads")
    siswa = relationship("Siswa", back_populates="notification_reads")
    pembimbing_dudi = relationship("PembimbingDudi", back_populates="notification_reads")
    guru_pembimbing = relationship("GuruPembimbing", back_populates="notification_reads")