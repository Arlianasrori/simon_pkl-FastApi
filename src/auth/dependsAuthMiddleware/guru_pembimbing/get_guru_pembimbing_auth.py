from fastapi import Request

async def getGuruPembimbingAuth(req : Request) :
    print(req.guruPembimbing)
    return req.guruPembimbing