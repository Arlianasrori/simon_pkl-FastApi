from datetime import time
async def time_to_float(t: time) -> float:
    return t.hour + t.minute / 60 + t.second / 3600