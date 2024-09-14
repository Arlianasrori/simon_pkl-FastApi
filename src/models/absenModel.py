from sqlalchemy import Column, Integer, String, Enum, ForeignKey,Time,Date,Float
from sqlalchemy.orm import relationship
from ..db.db import Base
import enum
import datetime


class StatusAbsenMasukKeluarEnum(enum.Enum):
    hadir = "hadir"
    telat = "telat"
    tidak_hadir = "tidak_hadir"
    izin = "izin"
    diluar_radius = "diluar_radius"

class StatusAbsenEnum(enum.Enum):
    hadir = "hadir"
    tidak_hadir = "tidak_hadir"
    diluar_radius = "diluar_radius"

class StatusOtherAbsenEnum(enum.Enum):
    izin = "izin"
    telat = "telat"

class HariEnum(enum.Enum):
    senin = "senin"
    selasa = "selasa"
    rabu = "rabu"
    kamis = "kamis"
    jumat = "jumat"
    sabtu = "sabtu"
    minggu = "minggu"

class AbsenJadwal(Base):
    __tablename__ = 'absen_jadwal'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_dudi = Column(Integer, ForeignKey('dudi.id'))
    tanggal_mulai = Column(Date)
    tanggal_berakhir = Column(Date)
    selisih_tanggal_day = Column(Integer)

    absen = relationship("Absen", back_populates="jadwal_absen")
    hari = relationship("HariAbsen", back_populates="jadwal",cascade="all,delete-orphan")

    dudi = relationship("Dudi", back_populates="absen_jadwal")

class HariAbsen(Base):
    __tablename__ = 'hari_absen'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_jadwal = Column(Integer, ForeignKey('absen_jadwal.id',ondelete="CASCADE"))

    hari = Column(Enum(HariEnum)) 
    batas_absen_masuk = Column(Time)
    batas_absen_pulang = Column(Time)

    jadwal = relationship("AbsenJadwal", back_populates="hari")


class Absen(Base):
    __tablename__ = 'absen'

    id = Column(Integer, primary_key=True)
    id_absen_jadwal = Column(Integer, ForeignKey('absen_jadwal.id'))
    id_siswa = Column(Integer, ForeignKey('siswa.id'))
    tanggal = Column(Date,default=datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    absen_masuk = Column(Time,default=datetime.datetime.utcnow().strftime("%H:%M"))
    absen_pulang = Column(Time,default=datetime.datetime.utcnow().strftime("%H:%M"))
    status_absen_masuk = Column(Enum(StatusAbsenMasukKeluarEnum))
    status_absen_pulang = Column(Enum(StatusAbsenMasukKeluarEnum))
    foto_absen_masuk = Column(String(1500))
    foto_absen_keluar = Column(String(1500))
    status = Column(Enum(StatusAbsenEnum),default=StatusAbsenEnum.tidak_hadir.value)

    jadwal_absen = relationship("AbsenJadwal", back_populates="absen")
    siswa = relationship("Siswa", back_populates="absen")
    keterangan_absen_masuk = relationship("IzinAbsenMasuk", back_populates="absen", uselist=False)
    keterangan_absen_pulang = relationship("IzinAbsenPulang", back_populates="absen", uselist=False)

class IzinAbsenMasuk(Base):
    __tablename__ = 'izin_absen_masuk'

    id = Column(Integer, primary_key=True)
    id_absen = Column(Integer, ForeignKey('absen.id'), unique=True)
    note = Column(String(30000))
    status_izin = Column(Enum(StatusOtherAbsenEnum))

    absen = relationship("Absen", back_populates="keterangan_absen_masuk")

class IzinAbsenPulang(Base):
    __tablename__ = 'izin_absen_pulang'

    id = Column(Integer, primary_key=True)
    id_absen = Column(Integer, ForeignKey('absen.id'), unique=True)
    note = Column(String(30000))
    status_izin = Column(Enum(StatusOtherAbsenEnum))

    absen = relationship("Absen", back_populates="keterangan_absen_pulang")

class KordinatAbsen(Base):
    __tablename__ = 'kordinat_absen'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_dudi = Column(Integer, ForeignKey('dudi.id'))
    nama_tempat = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    radius_absen_meter = Column(Float)

    dudi = relationship("Dudi", back_populates="kordinat_absen")