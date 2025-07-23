from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from services.staging import check_staging_alive
#from services.staging import check_staging_alive
from services.posthog import get_active_users
#from services.jira import get_open_p1_bugs

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://dooor-product-maturity-dashboard.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StageUpdate(BaseModel):
    stage: str

STAGES_FILE = "product_stages.json"

def load_stages():
    if os.path.exists(STAGES_FILE):
        with open(STAGES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_stages(stages):
    with open(STAGES_FILE, 'w') as f:
        json.dump(stages, f, indent=2)

@app.get("/")
@app.head("/")
async def root():
    return {"message": "Product Maturity API", "status": "running"}

@app.get("/maturity/products")
async def get_all_products():
    product_ids = ["chorus", "cadence", "kenna", "duet"]
    products = []
    
    for product_id in product_ids:
        product_data = await evaluate_single_product(product_id)
        products.append(product_data)
    
    return {"products": products}

@app.get("/maturity/products/{product_id}")
async def evaluate_product(product_id: str):
    return await evaluate_single_product(product_id)

@app.patch("/maturity/products/{product_id}/stage")
async def update_product_stage(product_id: str, stage_update: StageUpdate):
    valid_product_ids = ["chorus", "cadence", "kenna", "duet"]
    
    if product_id not in valid_product_ids:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Load current stages, update the specific product, and save
    stages = load_stages()
    stages[product_id] = stage_update.stage
    save_stages(stages)
    
    return {
        "success": True,
        "product_id": product_id,
        "stage": stage_update.stage,
        "message": f"Stage updated to {stage_update.stage} for product {product_id}"
    }

async def evaluate_single_product(product_id: str):
    
    staging_url = f"https://{product_id}-staging.dooor.ai"

    staging = await check_staging_alive(staging_url)
    #bugs_p1 = get_open_p1_bugs(product_id)
    if product_id == "chorus":
        users = await get_active_users()
    else:
        users = 0
    #flow = await get_flow_completion_rate(product_id)

    criterios = {
        "staging": "✅" if staging else "❌",
        #"bugs_p1": "✅" if bugs_p1 == 0 else "❌",
        "active_users": "✅" if users >= 3 else "❌",
        #"flow_completion": "✅" if flow >= 70 else "❌"
    }

    peso = {"✅": 1, "⚠️": 0.5, "❌": 0}
    score = sum(peso[v] for v in criterios.values()) / len(criterios) * 100

    if all(v == "✅" for v in criterios.values()):
        status = "READY"
    elif any(v == "❌" for v in criterios.values()):
        status = "BLOCKED"
    else:
        status = "ATTENTION"

    # Map status to the expected format
    status_mapping = {
        "READY": "ready",
        "BLOCKED": "blocked", 
        "ATTENTION": "in-progress"
    }
    
    # Convert criteria from emojis to boolean values
    criteria_boolean = {}
    for key, value in criterios.items():
        criteria_boolean[key] = value == "✅"
    
    # Load current stage from JSON file
    stages = load_stages()
    current_stage = stages.get(product_id)
    
    return {
        "id": product_id,
        "name": product_id,  # Using product_id as name for now
        "stage": current_stage,
        "targetStage": None,
        "description": None,
        "daysInStage": None,
        "status": status_mapping.get(status, "in-progress"),
        "readinessScore": score,
        "url": staging_url,
        "criteria": criteria_boolean,
        "metrics": {},
        "blockers": [],
        "nextAction": None,
        "kickoffDate": None
    }




