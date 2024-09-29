from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# models 
from .radiusAbsenModel import CekRadiusAbsenBody,ResponseCekRadius
from .....models.absenModel import KoordinatAbsen
from ....models_domain.absen_model import koordinatAbsenBase

# common
from .....error.errorHandling import HttpException
from .radiusAbsenUtils import calculate_radius

async def getAllkoordinatAbsen(id_dudi : int,session : AsyncSession) -> list[koordinatAbsenBase] :
    if not id_dudi :
        raise HttpException(400,"id dudi tidak boleh kosong")

    koordinatAbsen = (await session.execute(select(KoordinatAbsen).where(KoordinatAbsen.id_dudi == id_dudi))).scalars().all()

    return {
        "msg" : "success",
        "data" : koordinatAbsen
    }

async def cekRadiusAbsen(id_dudi : int,koordinat : CekRadiusAbsenBody,session : AsyncSession) -> ResponseCekRadius :
    if not id_dudi :
        raise HttpException(400,"id dudi tidak boleh kosong")
    
    findKoordinatDudi = (await session.execute(select(KoordinatAbsen).where(KoordinatAbsen.id_dudi == id_dudi))).scalars().all()

    if len(findKoordinatDudi) == 0 :
        raise HttpException(404,"Dudi belum menambahkan koordinat untuk absen")
    
    radius_terdekat = 0
    for koordinatDudi in findKoordinatDudi :
        if koordinatDudi.latitude and koordinatDudi.longitude :
            # cek radius
            radius = await calculate_radius(koordinat.latitude,koordinat.longitude,koordinatDudi.latitude,koordinatDudi.longitude)
            print(radius)
            print(koordinatDudi.radius_absen_meter)

            if radius <= koordinatDudi.radius_absen_meter :
                return {
                    "msg" : "success",
                    "data" : {
                        "inside_radius" : True,
                        "distance" : radius
                    }
                }
            else :
                if radius == 0 :
                    radius_terdekat = radius
                else :
                    if radius < radius_terdekat :
                        radius_terdekat = radius
            
    return {
        "msg" : "success",
        "data" : {
            "inside_radius" : False,
            "distance" : radius
        }
    }