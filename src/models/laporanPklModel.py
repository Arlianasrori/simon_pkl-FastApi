from sqlalchemy import Column, Integer, String, ForeignKey,Date
from sqlalchemy.orm import relationship
from ..db.db import Base

class LaporanPKL(Base):
    __tablename__ = 'laporan_pkl'

    id = Column(Integer, primary_key=True)
    id_siswa = Column(Integer, ForeignKey('siswa.id'))
    id_dudi = Column(Integer, ForeignKey('dudi.id'))
    id_pembimbing_dudi = Column(Integer, ForeignKey('pembimbing_dudi.id'))
    tanggal = Column(Date)
    keterangan = Column(String(1500))
    file_laporan = Column(String(1500),nullable=True)

    siswa = relationship("Siswa", back_populates="laporan_pkl")
    dudi = relationship("Dudi", back_populates="laporan_pkl")
    pembimbing_dudi = relationship("PembimbingDudi", back_populates="laporan_pkl")

class LaporanSiswaPKL(Base):
    __tablename__ = 'laporan_siswa_pkl'

    id = Column(Integer, primary_key=True)
    id_siswa = Column(Integer, ForeignKey('siswa.id'))
    id_dudi = Column(Integer, ForeignKey('dudi.id'))
    tanggal = Column(Date)
    topik_pekerjaan = Column(String(255))
    rujukan_kompetensi_dasar = Column(String(255))
    dokumentasi = Column(String(1500),nullable=True)

    siswa = relationship("Siswa", back_populates="laporans_siswa_pkl")
    dudi = relationship("Dudi", back_populates="laporans_siswa_pkl")