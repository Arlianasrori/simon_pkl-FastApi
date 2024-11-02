from .....error.errorHandling import HttpException
from .absenJadwalModel import AddHariAbsen
from .....models.absenModel import HariAbsen
from python_random_strings import random_strings
from .....utils.timeToFloat import time_to_float

async def cek_hari_absen(id_dudi : int,listHari : list[AddHariAbsen]) :
    listHariReturn = [] ## 
    listForResponse = []
    for i in range(0,len(listHari)) :
        hariMapping = listHari[i].model_dump()
        hariMapping["id_dudi"] = id_dudi
        hariMapping["id"] = random_strings.random_digits(6)
        if i != len(listHari) - 1 :
            if listHari[i].hari == listHari[i + 1].hari:
                raise HttpException(400,"error terdapat hari yang sama")
        
        absenMasukFloat : float = await time_to_float(hariMapping["batas_absen_masuk"])
        absenPulangFloat : float = await time_to_float(hariMapping["batas_absen_pulang"])

        if hariMapping["min_jam_kerja"] > absenPulangFloat - absenMasukFloat :
            raise HttpException(400,"min jam absen tidak boleh lebih besar dari batas absen pulang - batas absen masuk")
            
        listForResponse.append(hariMapping)
        listHariReturn.append(HariAbsen(**hariMapping))
    return {"hari" :listHariReturn,"response" : listForResponse}