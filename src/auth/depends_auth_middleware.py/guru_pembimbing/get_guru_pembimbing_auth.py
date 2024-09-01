from fastapi import Request

async def getGuruPembimbingAuth(req : Request) :
    return req.guruPembimbing