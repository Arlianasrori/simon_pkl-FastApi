from .....error.errorHandling import HttpException
from .absenJadwalModel import AddHariAbsen
from .....models.absenModel import HariAbsen
from python_random_strings import random_strings

async def cek_hari_absen(id_jadwal_absen : int,listHari : list[AddHariAbsen]) :
    listHariReturn = []
    listForResponse = []
    for i in range(0,len(listHari)) :
        hariMapping = listHari[i].model_dump()
        hariMapping["id_jadwal"] = id_jadwal_absen
        hariMapping["id"] = random_strings.random_digits(6)
        if i != len(listHari) - 1 :
            if listHari[i].hari == listHari[i + 1].hari:
                raise HttpException(400,"error terdapat hari yang sama")
            
        listForResponse.append(hariMapping)
        listHariReturn.append(HariAbsen(**hariMapping))
    return {"hari" :listHariReturn,"response" : listForResponse}

def get_date_difference_in_days(mulai, berakhir):
    delta = mulai - berakhir
    return abs(delta.days)