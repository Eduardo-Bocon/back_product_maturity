import asyncio
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY")
POSTHOG_PROJECT_ID = os.getenv("POSTHOG_PROJECT_ID", "191436")  
POSTHOG_URL = os.getenv("POSTHOG_URL", "https://us.posthog.com")  

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
    resp = requests.post(url, json=data, headers=headers)
    response_data = resp.json()

    print(response_data)
    
    # Extract the user count from the response
    if 'results' in response_data and len(response_data['results']) > 0:
        return int(response_data['results'][0].get('count', 0))
    return 0
    
