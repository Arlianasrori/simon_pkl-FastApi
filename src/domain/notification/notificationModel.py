from pydantic import BaseModel

class AddNotificationModel(BaseModel):
    id : int
    id_siswa : int | None = None
    id_dudi : int | None = None
    id_pembimbing_dudi : int | None = None
    id_guru_pembimbing : int | None = None
    title : str
    body : str
