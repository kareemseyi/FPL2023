from api.FPL import FPL
import aiohttp
import asyncio

async def fpl_login():
    session = aiohttp.ClientSession(trust_env=True)
    fpl = FPL(session)
    await fpl.login()
    await session.close()


asyncio.run(fpl_login())


