from pydantic import BaseModel

class AddPengajuanPklBody(BaseModel) :
    id_dudi : int

class CancelPengajuanBody(BaseModel) :
    alasan : str