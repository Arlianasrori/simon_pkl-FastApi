from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..db.db import Base


class Sekolah(Base):
    __tablename__ = 'sekolah'

    id = Column(Integer, primary_key=True)
    npsn = Column(String, unique=True, nullable=False)
    nama = Column(String(255), nullable=False)
    logo = Column(String, nullable=True)

    admin = relationship("Admin", back_populates="sekolah",cascade="all")
    alamat = relationship("AlamatSekolah", back_populates="sekolah",uselist=False,cascade="all")
    kepala_sekolah = relationship("KepalaSekolah", back_populates="sekolah",uselist=False,cascade="all")
    tahun = relationship("TahunSekolah", back_populates="sekolah",cascade="all")
    guru_pembimbing = relationship("GuruPembimbing", back_populates="sekolah",cascade="all")
    siswa = relationship("Siswa", back_populates="sekolah",cascade="all")
    dudi = relationship("Dudi", back_populates="sekolah",cascade="all")
    pembimbing_dudi = relationship("PembimbingDudi", back_populates="sekolah",cascade="all")
    jurusan = relationship("Jurusan", back_populates="sekolah",cascade="all")

    def __repr__(self):
        return f"<Sekolah(id={self.id}, npsn='{self.npsn}', nama='{self.nama}')>"

class AlamatSekolah(Base):
    __tablename__ = 'alamat_sekolah'

    id_sekolah = Column(Integer, ForeignKey('sekolah.id'), primary_key=True)
    detail_tempat = Column(String(255), nullable=False)
    desa = Column(String(255), nullable=False)
    kecamatan = Column(String(255), nullable=False)
    kabupaten = Column(String(255), nullable=False)
    provinsi = Column(String(255), nullable=False)
    negara = Column(String(255), nullable=False)

    sekolah = relationship("Sekolah", back_populates="alamat")

class KepalaSekolah(Base):
    __tablename__ = 'kepala_sekolah'

    id_sekolah = Column(Integer, ForeignKey('sekolah.id'), primary_key=True)
    nama = Column(String, nullable=False)
    nip = Column(String, nullable=False)

    sekolah = relationship("Sekolah", back_populates="kepala_sekolah")


class TahunSekolah(Base):
    __tablename__ = 'tahun_sekolah'

    id = Column(Integer, primary_key=True)
    id_sekolah = Column(Integer, ForeignKey('sekolah.id'))
    tahun = Column(String, nullable=False)

    sekolah = relationship("Sekolah", back_populates="tahun")
    siswa = relationship("Siswa", back_populates="tahun")
    jurusan = relationship("Jurusan", back_populates="tahun")
    pembimbing_dudi = relationship("PembimbingDudi", back_populates="tahun")
    dudi = relationship("Dudi", back_populates="tahun")
    guru_pembimbing = relationship("GuruPembimbing", back_populates="tahun")

    def __repr__(self):
        return f"<Tahun(id={self.id}, tahun='{self.tahun}'')>"

class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True)
    id_sekolah = Column(Integer, ForeignKey('sekolah.id'))
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    no_telepon = Column(String(255),unique=True,nullable=False)
    email = Column(String(255),unique=True,nullable=False)
    OTP_code = Column(Integer, nullable=True)

    sekolah = relationship("Sekolah", back_populates="admin")

    def __repr__(self):
        return f"<Admin(id={self.id}, username='{self.username}', id_sekolah={self.id_sekolah})>"

