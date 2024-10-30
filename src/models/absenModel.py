from sqlalchemy import Column, Integer, String, Enum, ForeignKey,Time,Date,Float,Boolean,UniqueConstraint
from sqlalchemy.orm import relationship
from ..db.db import Base
import enum
import datetime


class StatusAbsenMasukKeluarEnum(enum.Enum):
    hadir = "hadir"
    telat = "telat"
    tidak_hadir = "tidak_hadir"
    izin = "izin"
    sakit = "sakit"

class StatusAbsenEnum(enum.Enum):
    hadir = "hadir"
    tidak_hadir = "tidak_hadir"
    izin = "izin"
    sakit = "sakit"

class StatusOtherAbsenEnum(enum.Enum):
    izin = "izin"
    telat = "telat"
    diluar_radius = "diluar_radius"

class HariEnum(enum.Enum):
    senin = "senin"
    selasa = "selasa"
    rabu = "rabu"
    kamis = "kamis"
    jumat = "jumat"
    sabtu = "sabtu"
    minggu = "minggu"

# class AbsenJadwal(Base):
#     __tablename__ = 'absen_jadwal'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     id_dudi = Column(Integer, ForeignKey('dudi.id'))
#     tanggal_mulai = Column(Date)
#     tanggal_berakhir = Column(Date)

#     absen = relationship("Absen", back_populates="jadwal_absen")
#     hari = relationship("HariAbsen", back_populates="jadwal",cascade="all,delete-orphan")

#     dudi = relationship("Dudi", back_populates="absen_jadwal")

class HariAbsen(Base):
    __tablename__ = 'hari_absen'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_dudi = Column(Integer, ForeignKey('dudi.id',ondelete="CASCADE"))
    hari = Column(Enum(HariEnum)) 
    batas_absen_masuk = Column(Time)
    batas_absen_pulang = Column(Time)
    min_jam_absen = Column(Integer,nullable=False)
    enable = Column(Boolean,default=True)

    # Tambahkan UniqueConstraint
    __table_args__ = (
        UniqueConstraint('hari', 'id_dudi', name='uq_day_dudi'),
    )

    dudi = relationship("Dudi", back_populates="hari_jadwal")


class Absen(Base):
    __tablename__ = 'absen'

    id = Column(Integer, primary_key=True)
    # id_absen_jadwal = Column(Integer, ForeignKey('absen_jadwal.id'))
    id_siswa = Column(Integer, ForeignKey('siswa.id'))
    tanggal = Column(Date,default=datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    absen_masuk = Column(Time,nullable=True)
    absen_pulang = Column(Time,nullable=True)
    status_absen_masuk = Column(Enum(StatusAbsenMasukKeluarEnum),nullable=True)
    status_absen_pulang = Column(Enum(StatusAbsenMasukKeluarEnum),nullable=True)
    foto_absen_masuk = Column(String(1500),nullable=True)
    foto_absen_pulang = Column(String(1500),nullable=True)
    status = Column(Enum(StatusAbsenEnum),default=StatusAbsenEnum.tidak_hadir.value)

    # jadwal_absen = relationship("AbsenJadwal", back_populates="absen")
    siswa = relationship("Siswa", back_populates="absen")
    keterangan_absen_masuk = relationship("IzinAbsenMasuk", back_populates="absen", uselist=False)
    keterangan_absen_pulang = relationship("IzinAbsenPulang", back_populates="absen", uselist=False)
    dokumenSakit = relationship("DokumenAbsenSakit",back_populates="absen",uselist=False)

class DokumenAbsenSakit(Base) :
    __tablename__ = 'dokumen_absen_sakit'

    id = Column(Integer, primary_key=True)
    id_absen = Column(Integer,ForeignKey("absen.id"),nullable=False)
    dokumen = Column(String,nullable=False)
    note = Column(String(30000))

    absen = relationship("Absen",back_populates="dokumenSakit",uselist=False)

class IzinAbsenMasuk(Base):
    __tablename__ = 'izin_absen_masuk'

    id = Column(Integer, primary_key=True)
    id_absen = Column(Integer, ForeignKey('absen.id'), unique=True)
    note = Column(String(30000))
    inside_radius = Column(Boolean)
    status_izin = Column(Enum(StatusOtherAbsenEnum))

    absen = relationship("Absen", back_populates="keterangan_absen_masuk")

class IzinAbsenPulang(Base):
    __tablename__ = 'izin_absen_pulang'

    id = Column(Integer, primary_key=True)
    id_absen = Column(Integer, ForeignKey('absen.id'), unique=True)
    note = Column(String(30000))
    inside_radius = Column(Boolean)
    status_izin = Column(Enum(StatusOtherAbsenEnum))

    absen = relationship("Absen", back_populates="keterangan_absen_pulang")

class KoordinatAbsen(Base):
    __tablename__ = 'koordinat_absen'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_dudi = Column(Integer, ForeignKey('dudi.id'))
    nama_tempat = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    radius_absen_meter = Column(Float)

    dudi = relationship("Dudi", back_populates="koordinat_absen")