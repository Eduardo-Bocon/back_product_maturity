from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from services.staging import check_staging_alive
from services.posthog import get_active_users
from services.jira import get_open_p1_bugs, get_open_bugs_by_priority, get_open_all_bugs
from services.uptime_robot import get_product_uptime

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

class ObservationsUpdate(BaseModel):
    observations: str

STAGES_FILE = "product_stages.json"

def load_stages():
    if os.path.exists(STAGES_FILE):
        with open(STAGES_FILE, 'r') as f:
            data = json.load(f)
            # Handle backward compatibility - convert old format to new format
            if data and isinstance(list(data.values())[0], str):
                # Old format: {"product": "stage"}
                # Convert to new format: {"product": {"stage": "stage"}}
                converted_data = {}
                for product_id, stage in data.items():
                    converted_data[product_id] = {"stage": stage}
                save_stages(converted_data)  # Save in new format
                return converted_data
            return data
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
    product_ids = ["chorus", "cadence", "kenna", "duet", "nest"]
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
    valid_product_ids = ["chorus", "cadence", "kenna", "duet", "nest"]
    
    if product_id not in valid_product_ids:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Load current stages, update the specific product, and save
    stages = load_stages()
    if product_id not in stages:
        stages[product_id] = {}
    stages[product_id]["stage"] = stage_update.stage
    save_stages(stages)
    
    return {
        "success": True,
        "product_id": product_id,
        "stage": stage_update.stage,
        "message": f"Stage updated to {stage_update.stage} for product {product_id}"
    }

@app.patch("/maturity/products/{product_id}")
async def update_product_observations(product_id: str, observations_update: ObservationsUpdate):
    valid_product_ids = ["chorus", "cadence", "kenna", "duet", "nest"]
    
    if product_id not in valid_product_ids:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Load current data, update observations, and save
    stages = load_stages()
    if product_id not in stages:
        stages[product_id] = {}
    stages[product_id]["observations"] = observations_update.observations
    save_stages(stages)
    
    return {
        "success": True,
        "product_id": product_id,
        "observations": observations_update.observations,
        "message": f"Observations updated for product {product_id}"
    }

async def evaluate_single_product(product_id: str):
    
    staging_url = f"https://{product_id}-staging.dooor.ai"

    staging = await check_staging_alive(staging_url)
    bugs_critical = await get_open_bugs_by_priority(product_id.upper(), ['Highest', 'High'])
    bugs_medium_plus = await get_open_bugs_by_priority(product_id.upper(), ['Highest', 'High', 'Medium'])
    bugs_all = await get_open_all_bugs(product_id.upper())
    uptime = await get_product_uptime(product_id)
    if product_id == "chorus":
        users = await get_active_users()
    else:
        users = 0
    #flow = await get_flow_completion_rate(product_id)

    criterios = {
        "staging": staging,
        "bugs_critical": bugs_critical == 0,
        "bugs_medium_plus": bugs_medium_plus == 0,
        "bugs_all": bugs_all == 0,
        "uptime_99": uptime is not None and uptime >= 99.0,
        "uptime_95": uptime is not None and uptime >= 95.0,
        "active_users_1": users > 3,
        "active_users_2": users > 10,
        "active_users_3": users > 50,  
    }

    peso = {True: 1, False: 0}
    score = sum(peso[v] for v in criterios.values()) / len(criterios) * 100

    if all(v for v in criterios.values()):
        status = "READY"
    elif any(not v for v in criterios.values()):
        status = "BLOCKED"
    else:
        status = "ATTENTION"

    # Map status to the expected format
    status_mapping = {
        "READY": "ready",
        "BLOCKED": "blocked", 
        "ATTENTION": "in-progress"
    }
    
    # Criteria are already boolean values
    criteria_boolean = criterios
    
    # Load current stage and observations from JSON file
    stages = load_stages()
    product_data = stages.get(product_id, {})
    current_stage = product_data.get("stage")
    observations = product_data.get("observations")
    
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
        "observations": observations,
        "kickoffDate": None
    }




