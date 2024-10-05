from sqlalchemy import Column, Integer,String, Enum, DateTime, ForeignKey,Date
from sqlalchemy.orm import relationship
from ..db.db import Base
import enum
from datetime import datetime


class StatusPengajuanENUM(enum.Enum):
    proses = "proses"
    diterima = "diterima"
    ditolak = "ditolak"
    dibatalkan = "dibatalkan"

class StatusCancelPKLENUM(enum.Enum):
    proses = "proses"
    dibatalkan = "dibatalkan"
    setuju = "setuju"
    tidak_setuju = "tidak_setuju"


class PengajuanPKL(Base):
    __tablename__ = 'pengajuan_pkl'

    id = Column(Integer, primary_key=True)
    id_siswa = Column(Integer, ForeignKey('siswa.id'))
    id_dudi = Column(Integer, ForeignKey('dudi.id'))
    status = Column(Enum(StatusPengajuanENUM), default=StatusPengajuanENUM.proses.value)
    waktu_pengajuan = Column(DateTime, default=datetime.utcnow())
    alasan_pembatalan = Column(String,nullable=True)

    siswa = relationship("Siswa", back_populates="pengajuan_pkl")
    dudi = relationship("Dudi", back_populates="pengajuan_pkl")

class PengajuanCancelPKL(Base):
    __tablename__ = 'pengajuan_cancel_pkl'

    id = Column(Integer, primary_key=True)
    id_siswa = Column(Integer, ForeignKey('siswa.id'))
    id_dudi = Column(Integer, ForeignKey('dudi.id'))
    status = Column(Enum(StatusCancelPKLENUM), default=StatusCancelPKLENUM.proses.value)
    alasan = Column(String,nullable=False)
    waktu_pengajuan = Column(DateTime, default=datetime.utcnow())

    siswa = relationship("Siswa", back_populates="pengajuan_cancel_pkl")
    dudi = relationship("Dudi", back_populates="pengajuan_cancel_pkl")