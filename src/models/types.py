import enum

class JenisKelaminEnum(enum.Enum):
    laki = "laki"
    perempuan = "perempuan"
    
class UserTypeEnum(enum.Enum):
    SISWA = "siswa"
    GURU = "guru"
    ADMIN = "admin"
    PEMBIMBING_DUDI = "pembimbing_dudi"