async def get_date_difference_in_days(mulai, berakhir):
    delta = mulai - berakhir
    return abs(delta.days)