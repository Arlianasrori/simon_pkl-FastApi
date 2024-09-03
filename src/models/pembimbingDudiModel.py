from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..db.db import Base
from .types import JenisKelaminEnum

class PembimbingDudi(Base):
    __tablename__ = 'pembimbing_dudi'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    no_telepon = Column(String(12), unique=True, nullable=False)
    foto_profile = Column(String, nullable=True)
    jenis_kelamin = Column(Enum(JenisKelaminEnum), nullable=False)
    password = Column(String(255), nullable=False)
    token_FCM = Column(String, nullable=True)
    id_dudi = Column(Integer, ForeignKey('dudi.id'), nullable=False)
    id_sekolah = Column(Integer, ForeignKey('sekolah.id'), nullable=False)
    id_tahun = Column(Integer, ForeignKey('tahun_sekolah.id'), nullable=False)

    siswa = relationship("Siswa", back_populates="pembimbing_dudi")
    alamat = relationship("AlamatPembimbingDudi", uselist=False,back_populates="pembimbing_dudi",cascade="all")
    kunjungan_guru_pembimbing = relationship("KunjunganGuruPembimbingPKL", back_populates="pembimbing_dudi")
    notifications = relationship("Notification", back_populates="pembimbing_dudi")
    notification_reads = relationship("NotificationRead", back_populates="pembimbing_dudi")
    kordinat_absen = relationship("KordinatAbsen", back_populates="pembimbing_dudi")
    laporan_pkl = relationship("LaporanPKL", back_populates="pembimbing_dudi")

    dudi = relationship("Dudi", back_populates="pembimbing_dudi")
    sekolah = relationship("Sekolah", back_populates="pembimbing_dudi")
    tahun = relationship("TahunSekolah", back_populates="pembimbing_dudi")

    def __repr__(self):
        return f"<PembimbingDudi(id={self.id}, nama='{self.username}', id_dudi={self.id_dudi})>"

class AlamatPembimbingDudi(Base):
    __tablename__ = 'alamat_pembimbing_dudi'

    id_pembimbing_dudi = Column(Integer, ForeignKey('pembimbing_dudi.id'), primary_key=True)
    detail_tempat = Column(String(255), nullable=False)
    desa = Column(String(255), nullable=False)
    kecamatan = Column(String(255), nullable=False)
    kabupaten = Column(String(255), nullable=False)
    provinsi = Column(String(255), nullable=False)
    negara = Column(String(255), nullable=False)

    pembimbing_dudi = relationship("PembimbingDudi", back_populates="alamat")

    def __repr__(self):
        return f"<AlamatPembimbingDudi(id_pembimbing_dudi={self.id_pembimbing_dudi}')>"