import requests


async def check_staging_alive(url: str) -> bool:
    try:
        res = requests.get(url, timeout=3.0)
        print(res)
        return res.status_code == 200 or res.status_code == 307
    except Exception:
        return False
