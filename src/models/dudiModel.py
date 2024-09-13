from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..db.db import Base

class Dudi(Base):
    __tablename__ = 'dudi'

    id = Column(Integer, primary_key=True)
    nama_instansi_perusahaan = Column(String(255), nullable=False)
    bidang_usaha = Column(String(255), nullable=False)
    no_telepon = Column(String(12), unique=True, nullable=False)
    deskripsi = Column(String(255), nullable=False)
    id_sekolah = Column(Integer, ForeignKey('sekolah.id'), nullable=False)
    id_tahun = Column(Integer, ForeignKey('tahun_sekolah.id'), nullable=False)
    tersedia = Column(Boolean, default=False, nullable=False)

    alamat = relationship("AlamatDudi", uselist=False, back_populates="dudi",cascade="all")
    kouta = relationship("KoutaSiswa", uselist=False, back_populates="dudi",cascade="all")
    siswa = relationship("Siswa", back_populates="dudi")
    pembimbing_dudi = relationship("PembimbingDudi", back_populates="dudi",cascade="all")
    kunjungan_guru_pembimbing = relationship("KunjunganGuruPembimbingPKL", back_populates="dudi")
    pengajuan_pkl = relationship("PengajuanPKL", back_populates="dudi")
    pengajuan_cancel_pkl = relationship("PengajuanCancelPKL", back_populates="dudi")
    notifications = relationship("Notification", back_populates="dudi")
    absen_jadwal = relationship("AbsenJadwal", back_populates="dudi")
    kordinat_absen = relationship("KordinatAbsen", back_populates="dudi")
    laporan_pkl = relationship("LaporanPKL", back_populates="dudi")
    laporans_siswa_pkl = relationship("LaporanSiswaPKL", back_populates="dudi")

    sekolah = relationship("Sekolah", back_populates="dudi")
    tahun = relationship("TahunSekolah", back_populates="dudi")

    def __repr__(self):
        return f"<Dudi(id={self.id}, nama='{self.nama_instansi_perusahaan}', bidang_usaha='{self.bidang_usaha}')>"

class AlamatDudi(Base):
    __tablename__ = 'alamat_dudi'

    id_dudi = Column(Integer, ForeignKey('dudi.id'), primary_key=True)
    detail_tempat = Column(String(255), nullable=False)
    desa = Column(String(255), nullable=False)
    kecamatan = Column(String(255), nullable=False)
    kabupaten = Column(String(255), nullable=False)
    provinsi = Column(String(255), nullable=False)
    negara = Column(String(255), nullable=False)

    dudi = relationship("Dudi", back_populates="alamat")

    def __repr__(self):
        return f"<AlamatDudi(id={self.id_dudi}')>"


class KoutaSiswa(Base):
    __tablename__ = 'kouta_siswa'

    id = Column(Integer,primary_key=True, nullable=False)
    id_dudi = Column(Integer, ForeignKey('dudi.id'), unique=True, nullable=False)
    jumlah_pria = Column(Integer, nullable=False)
    jumlah_wanita = Column(Integer, nullable=False)

    dudi = relationship("Dudi", back_populates="kouta")
    kouta_jurusan = relationship("KoutaSiswaByJurusan",backref="kouta_siswa",cascade="all")

    def __repr__(self):
        return f"<KoutaSiswa(id={self.id_dudi}, id_dudi={self.id_dudi})>"
    
class KoutaSiswaByJurusan(Base):
    __tablename__ = 'kouta_siswa_jurusan'

    id = Column(Integer,primary_key=True, nullable=False)
    id_kouta = Column(Integer, ForeignKey('kouta_siswa.id',ondelete="CASCADE"), nullable=False)
    id_jurusan = Column(Integer, ForeignKey('jurusan.id',ondelete="CASCADE"), nullable=False)
    jumlah_pria = Column(Integer, nullable=False)
    jumlah_wanita = Column(Integer, nullable=False)
    
    jurusan = relationship("Jurusan", back_populates="kouta_jurusan")