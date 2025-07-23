#!/usr/bin/env python3

"""
Test script to diagnose Google Sheets connection issues
"""

import os
from sheets import get_sheets_client, get_product_stages, update_product_stage

def test_sheets_connection():
    print("=== Google Sheets Connection Test ===")
    
    # Test 1: Check if credentials file exists
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "teste-466819-52aba8b77c56.json")
    print(f"1. Checking credentials file: {creds_file}")
    if os.path.exists(creds_file):
        print("   ✅ Credentials file found")
    else:
        print("   ❌ Credentials file not found")
        return
    
    # Test 2: Initialize client
    print("2. Initializing Google Sheets client...")
    client = get_sheets_client()
    if client:
        print("   ✅ Client initialized successfully")
    else:
        print("   ❌ Failed to initialize client")
        return
    
    # Test 3: List available sheets (to verify access)
    print("3. Testing sheet access...")
    try:
        # Try to list all sheets the service account has access to
        sheets = client.openall()
        print(f"   ✅ Service account has access to {len(sheets)} sheets:")
        for sheet in sheets[:5]:  # Show first 5 sheets
            print(f"      - {sheet.title} (ID: {sheet.id})")
        if len(sheets) > 5:
            print(f"      ... and {len(sheets) - 5} more")
    except Exception as e:
        print(f"   ❌ Error listing sheets: {e}")
    
    # Test 4: Try to open specific sheet
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "1mNx8nECvI07fLbUYBcNkJPU_hm5wpV0PQGF0k6c6Mzg")
    print(f"4. Testing access to target sheet (ID: {sheet_id})...")
    try:
        sheet = client.open_by_key(sheet_id)
        print(f"   ✅ Successfully opened sheet: {sheet.title}")
        
        # Test worksheet access
        worksheet = sheet.sheet1
        print(f"   ✅ Successfully accessed first worksheet")
        
        # Try to read some data
        try:
            values = worksheet.get_all_values()
            print(f"   ✅ Successfully read {len(values)} rows from sheet")
            if values:
                print(f"   📊 First row: {values[0]}")
        except Exception as e:
            print(f"   ⚠️  Could not read data: {e}")
            
    except Exception as e:
        print(f"   ❌ Error opening target sheet: {e}")
        print("   💡 Make sure the sheet ID is correct and the service account has access")
        return
    
    # Test 5: Try the actual functions
    print("5. Testing application functions...")
    try:
        stages = get_product_stages()
        print(f"   ✅ get_product_stages() returned: {stages}")
    except Exception as e:
        print(f"   ❌ get_product_stages() failed: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_sheets_connection()