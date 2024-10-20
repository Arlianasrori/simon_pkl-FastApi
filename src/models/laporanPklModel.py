from sqlalchemy import Column, Integer, String, ForeignKey,Date
from sqlalchemy.orm import relationship
from ..db.db import Base

class LaporanPKL(Base):
    __tablename__ = 'laporan_pkl'

    id = Column(Integer, primary_key=True)
    id_dudi = Column(Integer, ForeignKey('dudi.id',ondelete='CASCADE',onupdate='CASCADE'))
    id_pembimbing_dudi = Column(Integer, ForeignKey('pembimbing_dudi.id',ondelete='CASCADE',onupdate='CASCADE'))
    tanggal = Column(Date)
    # keterangan = Column(String(1500))
    topik_pekerjaan = Column(String(255))
    rujukan_kompetensi_dasar = Column(String(255))
    file_laporan = Column(String(1500),nullable=True)

    dudi = relationship("Dudi", back_populates="laporan_pkl")
    pembimbing_dudi = relationship("PembimbingDudi", back_populates="laporan_pkl")

class LaporanSiswaPKL(Base):
    __tablename__ = 'laporan_siswa_pkl'

    id = Column(Integer, primary_key=True)
    id_siswa = Column(Integer, ForeignKey('siswa.id',ondelete='CASCADE',onupdate='CASCADE'))
    id_dudi = Column(Integer, ForeignKey('dudi.id',ondelete='CASCADE',onupdate='CASCADE'))
    tanggal = Column(Date)
    topik_pekerjaan = Column(String(255))
    rujukan_kompetensi_dasar = Column(String(255))
    dokumentasi = Column(String(1500),nullable=True)

    siswa = relationship("Siswa", back_populates="laporans_siswa_pkl")
    dudi = relationship("Dudi", back_populates="laporans_siswa_pkl")

class LaporanKendalaSiswa(Base):
    __tablename__ = 'laporan_kendala'

    id = Column(Integer, primary_key=True)
    id_siswa = Column(Integer, ForeignKey('siswa.id',ondelete='CASCADE',onupdate='CASCADE'))
    tanggal = Column(Date)
    kendala = Column(String(1500))
    file_laporan = Column(String(1500),nullable=True)
    deskripsi = Column(String(1500))

    siswa = relationship("Siswa", back_populates="laporan_kendala")

class LaporanKendalaDudi(Base):
    __tablename__ = 'laporan_kendala_dudi'

    id = Column(Integer, primary_key=True)
    id_siswa = Column(Integer, ForeignKey('siswa.id',ondelete='CASCADE',onupdate='CASCADE'))
    id_pembimbing_dudi = Column(Integer, ForeignKey('pembimbing_dudi.id',ondelete='CASCADE',onupdate='CASCADE'))
    tanggal = Column(Date)
    kendala = Column(String(1500))
    file_laporan = Column(String(1500),nullable=True)
    deskripsi = Column(String(1500))

    siswa = relationship("Siswa", back_populates="laporan_kendala_dudi")
    pembimbingDudi = relationship("PembimbingDudi", back_populates="laporan_kendala_dudi")