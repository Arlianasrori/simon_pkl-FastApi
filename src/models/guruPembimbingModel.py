from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from ..db.db import Base
from .types import JenisKelaminEnum
from .types import UserTypeEnum
from .userBaseModel import User

class GuruPembimbing(User):
    __tablename__ = 'guru_pembimbing'

    id = Column(Integer, ForeignKey('user.id') ,primary_key=True)
    nip = Column(String, unique=True, nullable=False)
    nama = Column(String(255), nullable=False)
    no_telepon = Column(String(12), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    jenis_kelamin = Column(Enum(JenisKelaminEnum), nullable=False)
    tempat_lahir = Column(String(255), nullable=False)
    tanggal_lahir = Column(String, nullable=False)
    agama = Column(String(255), nullable=False)
    foto_profile = Column(String, nullable=True)
    token_FCM = Column(String, nullable=True)
    password = Column(String(255), nullable=False)
    id_sekolah = Column(Integer, ForeignKey('sekolah.id'), nullable=False)
    id_tahun = Column(Integer, ForeignKey('tahun_sekolah.id'), nullable=False)
    OTP_code = Column(Integer, nullable=True)
    is_online = Column(Boolean, default=False, nullable=False)

    # Relasi yang sudah ada
    siswa = relationship("Siswa",foreign_keys="[Siswa.id_guru_pembimbing]", back_populates="guru_pembimbing")
    alamat = relationship("AlamatGuruPembimbing", uselist=False, back_populates="guru_pembimbing", cascade="all")
    kunjungan_guru_pembimbing = relationship("KunjunganGuruPembimbingPKL", back_populates="guru_pembimbing")
    notifications = relationship("Notification", back_populates="guru_pembimbing")
    notification_reads = relationship("NotificationRead", back_populates="guru_pembimbing")
    sekolah = relationship("Sekolah", back_populates="guru_pembimbing")
    tahun = relationship("TahunSekolah", back_populates="guru_pembimbing")

    __mapper_args__ = {
        'polymorphic_identity': UserTypeEnum.GURU,
    }
    
    def __repr__(self):
        return f"<GuruPembimbing(id={self.id}, nip='{self.nip}', nama='{self.nama}')>"


class AlamatGuruPembimbing(Base):
    __tablename__ = 'alamat_guru_pembimbing'

    id_guru_pembimbing = Column(Integer, ForeignKey('guru_pembimbing.id'), primary_key=True)
    detail_tempat = Column(String(255), nullable=False)
    desa = Column(String(255), nullable=False)
    kecamatan = Column(String(255), nullable=False)
    kabupaten = Column(String(255), nullable=False)
    provinsi = Column(String(255), nullable=False)
    negara = Column(String(255), nullable=False)

    guru_pembimbing = relationship("GuruPembimbing", back_populates="alamat")

    def __repr__(self):
        return f"<AlamatGuruPembimbing(id={self.id_guru_pembimbing})>"
    
class KunjunganGuruPembimbingPKL(Base):
    __tablename__ = 'kunjungan_guru_pembimbing_pkl'

    id = Column(Integer, primary_key=True)
    id_guru_pembimbing = Column(Integer, ForeignKey('guru_pembimbing.id'), nullable=False)
    id_dudi = Column(Integer, ForeignKey('dudi.id'), nullable=False)
    tanggal_kunjungan = Column(DateTime, nullable=False)
    catatan = Column(String(1500), nullable=False)

    dudi = relationship("Dudi", back_populates="kunjungan_guru_pembimbing")
    guru_pembimbing = relationship("GuruPembimbing", back_populates="kunjungan_guru_pembimbing")

    def __repr__(self):
        return f"<KunjunganGuruPembimbingPKL(id={self.id}, tanggal_kunjungan='{self.tanggal_kunjungan}')>"