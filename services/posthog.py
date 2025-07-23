import asyncio
import httpx
from datetime import datetime


POSTHOG_API_KEY = "phx_5N4N2VCVs7GluggALQOQi8sssDMj8DDLC1yA1uPv2PZjnh3" 
POSTHOG_PROJECT_ID = "191436"  
POSTHOG_URL = "https://us.posthog.com"  

DATE_FROM = "2024-07-01"
DATE_TO = datetime.now().strftime("%Y-%m-%d")

async def get_active_users():
    url = f"{POSTHOG_URL}/api/projects/{POSTHOG_PROJECT_ID}/query/"
    headers = {
        "Authorization": f"Bearer {POSTHOG_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "query": {
            "kind": "TrendsQuery",
            "series": [
                {
                    "event": "$pageview",
                    "math": "dau"
                }
            ],
            "dateRange": {
                "date_from": DATE_FROM,
                "date_to": DATE_TO
            },
            "interval": "month"
        }
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=data, headers=headers)
        response_data = resp.json()

        print(response_data)
        
        # Extract the user count from the response
        if 'results' in response_data and len(response_data['results']) > 0:
            return int(response_data['results'][0].get('count', 0))
        return 0
    
