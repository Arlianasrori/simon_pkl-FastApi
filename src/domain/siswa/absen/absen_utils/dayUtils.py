from ....models_domain.absen_model import dayCodeSet
from datetime import datetime
from .....models.absenModel import HariEnum


async def get_day() -> HariEnum:
    # Mendapatkan hari ini (1-7, di mana 1 adalah Senin)
    day_code = (datetime.now().isoweekday()) - 1
    return dayCodeSet[day_code]