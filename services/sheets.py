import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheets configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "your_sheet_id_here")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

def get_sheets_client():
    """Initialize and return Google Sheets client"""
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Error initializing Google Sheets client: {e}")
        return None

def get_product_stages():
    """Get all product stages from Google Sheets"""
    try:
        client = get_sheets_client()
        if not client:
            return {}
        
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        # Get all records from the sheet
        records = sheet.get_all_records()
        
        # Convert to dictionary format
        stages = {}
        for record in records:
            product_id = record.get('product_id', '')
            stage = record.get('stage', None)
            if product_id:
                stages[product_id] = stage
        
        return stages
    except Exception as e:
        print(f"Error reading from Google Sheets: {e}")
        return {}

def update_product_stage(product_id: str, stage: str):
    """Update a specific product's stage in Google Sheets"""
    try:
        client = get_sheets_client()
        if not client:
            return False
        
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        # Try to find existing row for this product
        try:
            cell = sheet.find(product_id)
            # Update the stage in the same row, column B (assuming A=product_id, B=stage)
            sheet.update(f'B{cell.row}', stage)
        except gspread.CellNotFound:
            # Product not found, add new row
            sheet.append_row([product_id, stage])
        
        return True
    except Exception as e:
        print(f"Error updating Google Sheets: {e}")
        return False

def initialize_sheet():
    """Initialize the sheet with headers if it's empty"""
    try:
        client = get_sheets_client()
        if not client:
            return False
        
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        # Check if sheet is empty or has no headers
        try:
            headers = sheet.row_values(1)
            if not headers or headers[0] != 'product_id':
                # Set headers
                sheet.update('A1:B1', [['product_id', 'stage']])
                
                # Initialize with default products
                default_products = ['chorus', 'cadence', 'kenna', 'duet']
                for i, product in enumerate(default_products, start=2):
                    sheet.update(f'A{i}:B{i}', [[product, None]])
        except Exception:
            # Sheet might be completely empty
            sheet.update('A1:B1', [['product_id', 'stage']])
            default_products = ['chorus', 'cadence', 'kenna', 'duet']
            for i, product in enumerate(default_products, start=2):
                sheet.update(f'A{i}:B{i}', [[product, None]])
        
        return True
    except Exception as e:
        print(f"Error initializing sheet: {e}")
        return False