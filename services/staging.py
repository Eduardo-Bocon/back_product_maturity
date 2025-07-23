import httpx


async def check_staging_alive(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(url)
            print(res)
            return res.status_code == 200 or res.status_code == 307
    except Exception:
        return False
