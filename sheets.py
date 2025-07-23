import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheets configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1RxLmuqUU5aZEbl0bgU2yHYoEgcitkvO_5O0a3QQgmgY")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "teste-466819-52aba8b77c56.json")

def get_sheets_client():
    """Initialize and return Google Sheets client"""
    try:
        print(f"Using credentials file: {CREDENTIALS_FILE}")
        print(f"Using sheet ID: {SHEET_ID}")
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
        
        print("Attempting to open sheet...")
        sheet = client.open_by_key(SHEET_ID).sheet1
        print("Sheet opened successfully!")
        
        # Check if sheet needs initialization
        try:
            all_values = sheet.get_all_values()
            print(f"All sheet values: {all_values}")
            
            if not all_values or len(all_values) < 2:
                print("Sheet appears empty or has no data rows. Initializing...")
                initialize_sheet()
                # Retry after initialization
                all_values = sheet.get_all_values()
        except Exception as e:
            print(f"Error checking sheet content: {e}")
        
        # Get all records from the sheet
        records = sheet.get_all_records()
        print(f"Retrieved {len(records)} records from sheet")
        print(f"Raw records: {records}")
        
        # Convert to dictionary format
        stages = {}
        for record in records:
            print(f"Processing record: {record}")
            # The sheet has products as columns, so extract them directly
            for product_name in ['chorus', 'cadence', 'kenna', 'duet']:
                if product_name in record:
                    stage_value = record[product_name]
                    if stage_value:  # Only add if not empty
                        stages[product_name] = stage_value
                    print(f"  {product_name}: '{stage_value}'")
            break  # Only process the first record since all data is in one row
        
        print(f"Parsed stages: {stages}")
        return stages
    except Exception as e:
        print(f"Error reading from Google Sheets: {e}")
        print(f"Error type: {type(e).__name__}")
        return {}

def update_product_stage(product_id: str, stage: str):
    """Update a specific product's stage in Google Sheets"""
    try:
        client = get_sheets_client()
        if not client:
            return False
        
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        # Find the column for this product
        try:
            # Get the first row (headers) to find the column
            headers = sheet.row_values(1)
            print(f"Sheet headers: {headers}")
            
            if product_id in headers:
                # Find the column index (1-based)
                col_index = headers.index(product_id) + 1
                # Convert to column letter (A=1, B=2, etc.)
                col_letter = chr(64 + col_index)
                cell_ref = f'{col_letter}2'
                print(f"Updating cell {cell_ref} with value {stage}")
                
                # Update the value in row 2 (first data row)
                sheet.update(cell_ref, [[stage]])  # Pass as 2D array
                print(f"Updated {product_id} to {stage} in column {col_letter}")
                return True
            else:
                print(f"Product {product_id} not found in headers: {headers}")
                return False
                
        except Exception as e:
            print(f"Error finding product column: {e}")
            return False
        
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

# Legacy function for backward compatibility
def get_sheet(sheet_name: str, worksheet_name: str = "Página1"):
    """Legacy function - use get_sheets_client() instead"""
    client = get_sheets_client()
    if client:
        return client.open(sheet_name).worksheet(worksheet_name)
    return None
