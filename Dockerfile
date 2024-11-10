FROM python:3.12.0-alpine

ENV DATABASE_URL="postgresql+asyncpg://postgres:habil123@localhost:5432/simon_pkl"
ENV FCM_PATH_KEY="simon-pkl-2a7c6-firebase-adminsdk-zvkwd-08e150fa34 (2).json"
ENV EMAIL_PASSWORD="ilfz mfhx ahkx jnyo"
ENV EMAIL_USER="arlianasrori@gmail.com"
ENV DEVELOPER_SECRET_ACCESS_TOKEN="jdhfjdfjdfhdj"
ENV DEVELOPER_SECRET_REFRESH_TOKEN="jdhfjdfjdfhdj"
ENV ADMIN_SECRET_ACCESS_TOKEN="jdhfjdfjdfhdj"
ENV ADMIN_SECRET_REFRESH_TOKEN="jdhfjdfjdfhdj"
ENV SISWA_SECRET_ACCESS_TOKEN="dvdvdvdvdvd"
ENV SISWA_SECRET_REFRESH_TOKEN="dvdvdvdvdv"
ENV GURU_PEMBIMBING_SECRET_ACCESS_TOKEN="dvdvdvdvdv"
ENV GURU_PEMBIMBING_SECRET_REFRESH_TOKEN="dvdvdvdvdv"
ENV PEMBIMBING_DUDI_SECRET_ACCESS_TOKEN="dvdvdvdvdv"
ENV PEMBIMBING_DUDI_SECRET_REFRESH_TOKEN="dvdvdvdvdv"
ENV DEV_LOGO_SEKOLAH_STORE="src/public/sekolah_logo/"
ENV DEV_LOGO_SEKOLAH_BASE_URL="http://localhost:2008/logo_sekolah"
ENV DEV_FOTO_PROFILE_GURU_PEMBIMBING_STORE="src/public/guru_pembimbing_profile/"
ENV DEV_FOTO_PROFILE_GURU_PEMBIMBING_BASE_URL="http://localhost:2008/public/guru_pembimbing_profile"
ENV DEV_FOTO_PROFILE_SISWA_STORE="src/public/siswa_profile/"
ENV DEV_FOTO_PROFILE_SISWA_BASE_URL="http://localhost:2008/public/siswa_profile"
ENV DEV_FOTO_PROFILE_PEMBIMBING_DUDI_STORE="src/public/pembimbing_dudi_profile/"
ENV DEV_FOTO_PROFILE_PEMBIMBING_DUDI_BASE_URL="http://localhost:2008/public/pembimbing_dudi_profile"
ENV DEV_LAPORAN_PKL_DUDI="src/public/laporan_pkl/"
ENV DEV_LAPORAN_PKL_DUDI_BASE_URL="http://localhost:2008/public/laporan_pkl"
ENV DEV_LAPORAN_PKL_SISWA="src/public/laporan_pkl_siswa/"
ENV DEV_LAPORAN_PKL_SISWA_BASE_URL="http://localhost:2008/public/laporan_pkl_siswa"
ENV DEV_LAPORAN_KENDALA_SISWA="src/public/laporan_kendala/"
ENV DEV_LAPORAN_KENDALA_SISWA_BASE_URL="http://localhost:2008/public/laporan_kendala"
ENV DEV_LAPORAN_KENDALA_DUDI="src/public/laporan_kendala_dudi/"
ENV DEV_LAPORAN_KENDALA_DUDI_BASE_URL="http://localhost:2008/public/laporan_kendala_dudi"
ENV DEV_IMAGE_ABSEN_STORE="src/public/image_absen/"
ENV DEV_IMAGE_ABSEN_BASE_URL="http://localhost:2008/public/image_absen"
ENV DEV_CHATTING_FILE_STORE="src/public/chat/"
ENV DEV_CHATTING_FILE_BASE_URL="http://localhost:2008/public/chat"
ENV DEV_DOKUMEN_ABSEN_STORE="src/public/dokumen_absen/"
ENV DEV_DOKUMEN_ABSEN_BASE_URL="http://localhost:2008/public/dokumen_absen"

RUN apk update && pip install poetry 

WORKDIR /app

COPY . /app

RUN  poetry config virtualenvs.create false && poetry lock --no-update && poetry install

ENTRYPOINT ["/bin/sh"]
