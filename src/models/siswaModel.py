from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..db.db import Base
import enum
from .types import JenisKelaminEnum

class StatusPKLEnum(enum.Enum):
    pkl = "pkl"
    belum_pkl = "belum_pkl"
    menunggu = "menunggu"

class Siswa(Base):
    __tablename__ = 'siswa'

    id = Column(Integer, primary_key=True)
    nis = Column(String, unique=True, nullable=False)
    nama = Column(String(255), nullable=False)
    jenis_kelamin = Column(Enum(JenisKelaminEnum), nullable=False)
    no_telepon = Column(String(12), unique=True, nullable=False)
    id_guru_pembimbing = Column(Integer, ForeignKey('guru_pembimbing.id'), nullable=True)
    id_dudi = Column(Integer, ForeignKey('dudi.id'), nullable=True)
    id_pembimbing_dudi = Column(Integer, ForeignKey('pembimbing_dudi.id'), nullable=True)
    password = Column(String(255), nullable=False)
    status = Column(Enum(StatusPKLEnum), default=StatusPKLEnum.belum_pkl.value, nullable=False)
    token_FCM = Column(String, nullable=True)
    foto_profile = Column(String, nullable=True)
    id_jurusan = Column(Integer, ForeignKey('jurusan.id'), nullable=False)
    id_kelas = Column(Integer, ForeignKey('kelas.id'), nullable=False)
    id_sekolah = Column(Integer, ForeignKey('sekolah.id'), nullable=False)
    id_tahun = Column(Integer, ForeignKey('tahun_sekolah.id'), nullable=False)

    jurusan = relationship("Jurusan", back_populates="siswa")
    kelas = relationship("Kelas", back_populates="siswa")
    alamat = relationship("AlamatSiswa", uselist=False, back_populates="siswa",cascade="all")
    pengajuan_pkl = relationship("PengajuanPKL", back_populates="siswa")
    laporan_pkl = relationship("LaporanPKL", back_populates="siswa")
    laporans_siswa_pkl = relationship("LaporanSiswaPKL", back_populates="siswa")
    pengajuan_cancel_pkl = relationship("PengajuanCancelPKL", back_populates="siswa")
    notifications = relationship("Notification", back_populates="siswa")
    notification_reads = relationship("NotificationRead", back_populates="siswa")
    absen = relationship("Absen", back_populates="siswa")


    sekolah = relationship("Sekolah", back_populates="siswa")
    guru_pembimbing = relationship("GuruPembimbing", back_populates="siswa")
    dudi = relationship("Dudi", back_populates="siswa")
    pembimbing_dudi = relationship("PembimbingDudi", back_populates="siswa")
    tahun = relationship("TahunSekolah", back_populates="siswa")

    def __repr__(self):
        return f"<Siswa(id={self.id}, nis='{self.nis}', nama='{self.nama}')>"

# Model-model terkait lainnya (contoh singkat)
class Jurusan(Base):
    __tablename__ = 'jurusan'
    id = Column(Integer, primary_key=True)
    nama = Column(String(255), nullable=False)
    id_sekolah = Column(Integer, ForeignKey('sekolah.id'), nullable=False)
    id_tahun = Column(Integer, ForeignKey('tahun_sekolah.id'), nullable=False)

    siswa = relationship("Siswa", back_populates="jurusan")
    kelas = relationship("Kelas", back_populates="jurusan")
    sekolah = relationship("Sekolah", back_populates="jurusan")
    tahun = relationship("TahunSekolah", back_populates="jurusan")

class Kelas(Base):
    __tablename__ = 'kelas'
    id = Column(Integer, primary_key=True)
    nama = Column(String(255), nullable=False)
    tahun = Column(String, nullable=False)
    id_jurusan = Column(Integer, ForeignKey('jurusan.id'), nullable=False)

    siswa = relationship("Siswa", back_populates="kelas")
    jurusan = relationship("Jurusan", back_populates="kelas")

class AlamatSiswa(Base):
    __tablename__ = 'alamat_siswa'
    id_siswa = Column(Integer, ForeignKey('siswa.id'), primary_key=True)
    detail_tempat = Column(String(255), nullable=False)
    desa = Column(String(255), nullable=False)
    kecamatan = Column(String(255), nullable=False)
    kabupaten = Column(String(255), nullable=False)
    provinsi = Column(String(255), nullable=False)
    negara = Column(String(255), nullable=False)

    siswa = relationship("Siswa", back_populates="alamat")

    def __repr__(self):
        return f"<AlamatSiswa(id_siswa={self.id_siswa}, desa='{self.desa}', kecamatan='{self.kecamatan}')>"