from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from services.staging import check_staging_alive
from services.posthog import get_active_users
from services.jira import get_open_p1_bugs, get_open_bugs_by_priority, get_open_all_bugs
from services.uptime_robot import get_product_uptime, get_product_response_times, get_all_products_data
from services.security import check_product_security

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

class ProductCreate(BaseModel):
    id: str
    name: str
    description: str = None

STAGES_FILE = "product_stages.json"
PRODUCTS_FILE = "products.json"

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

def load_products():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r') as f:
            return json.load(f)
    # Default products if file doesn't exist
    default_products = {
        "chorus": {"name": "Chorus", "description": "Main product"},
        "cadence": {"name": "Cadence", "description": "Cadence product"},
        "kenna": {"name": "Kenna", "description": "Kenna product"},
        "duet": {"name": "Duet", "description": "Duet product"},
        "nest": {"name": "Nest", "description": "Nest product"}
    }
    save_products(default_products)
    return default_products

def save_products(products):
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(products, f, indent=2)

def get_valid_product_ids():
    products = load_products()
    return list(products.keys())

@app.get("/")
@app.head("/")
async def root():
    return {"message": "Product Maturity API", "status": "running"}

@app.get("/products")
async def list_products():
    """List all available products"""
    products = load_products()
    return {"products": products}

@app.post("/products")
async def create_product(product: ProductCreate):
    """Create a new product"""
    products = load_products()
    
    # Validate product ID format (alphanumeric, lowercase, no spaces)
    if not product.id.isalnum() or not product.id.islower():
        raise HTTPException(
            status_code=400, 
            detail="Product ID must be alphanumeric and lowercase"
        )
    
    # Check if product already exists
    if product.id in products:
        raise HTTPException(status_code=409, detail="Product already exists")
    
    # Add new product
    products[product.id] = {
        "name": product.name,
        "description": product.description
    }
    save_products(products)
    
    return {
        "success": True,
        "product": products[product.id],
        "message": f"Product '{product.id}' created successfully"
    }

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete a product"""
    products = load_products()
    
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Remove from products
    deleted_product = products.pop(product_id)
    save_products(products)
    
    # Also remove from stages if exists
    stages = load_stages()
    if product_id in stages:
        stages.pop(product_id)
        save_stages(stages)
    
    return {
        "success": True,
        "deleted_product": deleted_product,
        "message": f"Product '{product_id}' deleted successfully"
    }

@app.get("/maturity/products")
async def get_all_products():
    product_ids = get_valid_product_ids()
    
    # Pre-fetch all UptimeRobot data in a single API call
    uptime_data = await get_all_products_data(product_ids)
    
    products = []
    for product_id in product_ids:
        product_data = await evaluate_single_product(product_id, uptime_data.get(product_id))
        products.append(product_data)
    
    return {"products": products}

@app.get("/maturity/products/{product_id}")
async def evaluate_product(product_id: str):
    return await evaluate_single_product(product_id)

@app.patch("/maturity/products/{product_id}/stage")
async def update_product_stage(product_id: str, stage_update: StageUpdate):
    valid_product_ids = get_valid_product_ids()
    
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
    valid_product_ids = get_valid_product_ids()
    
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

async def evaluate_single_product(product_id: str, uptime_data: dict = None):
    
    staging_url = f"https://{product_id}-staging.dooor.ai"

    staging = await check_staging_alive(staging_url)
    bugs_critical = await get_open_bugs_by_priority(product_id.upper(), ['Highest', 'High'])
    bugs_medium_plus = await get_open_bugs_by_priority(product_id.upper(), ['Highest', 'High', 'Medium'])
    bugs_all = await get_open_all_bugs(product_id.upper())
    
    # Use pre-fetched uptime data if available, otherwise fetch individually
    if uptime_data:
        uptime = uptime_data.get('uptime')
        response_times = uptime_data.get('response_times')
    else:
        uptime = await get_product_uptime(product_id)
        response_times = await get_product_response_times(product_id)
    security_headers = await check_product_security(product_id)
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
        "latency_avg_500": response_times is not None and response_times.get('average_ms', float('inf')) < 500,
        "latency_avg_1000": response_times is not None and response_times.get('average_ms', float('inf')) < 1000,
        "latency_p95": response_times is not None and response_times.get('p95_ms', float('inf')) < 1000,
        "security_headers": security_headers,
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
    
    # Load product details
    products = load_products()
    product_info = products.get(product_id, {})
    product_name = product_info.get("name", product_id)
    product_description = product_info.get("description")
    
    return {
        "id": product_id,
        "name": product_name,
        "stage": current_stage,
        "targetStage": None,
        "description": product_description,
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




