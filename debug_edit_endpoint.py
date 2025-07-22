#!/usr/bin/env python3
"""
Debug script to test the sales edit endpoint directly
"""

import requests
import json

def test_edit_endpoint():
    print("=== TESTING EDIT ENDPOINT ===")
    
    # Test the edit endpoint directly
    url = "http://localhost:5000/api/sales/edit/2002"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        
        # Look for key data in the response
        if "window.editSaleData" in response.text:
            print("✅ window.editSaleData found in response")
            
            # Extract the data
            start = response.text.find("window.editSaleData = ") + len("window.editSaleData = ")
            end = response.text.find(";", start)
            if end != -1:
                data_str = response.text[start:end]
                print(f"Data string: {data_str[:200]}...")
                
                try:
                    data = json.loads(data_str)
                    print(f"✅ Parsed data successfully: {len(data)} items")
                    for i, item in enumerate(data):
                        print(f"  Item {i+1}: {item}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse error: {e}")
                    print(f"Raw data: {data_str}")
        else:
            print("❌ window.editSaleData NOT found in response")
            
        # Look for debug messages
        if "=== DEBUG: Data Assignment ===" in response.text:
            print("✅ Debug messages found")
        else:
            print("❌ Debug messages NOT found")
            
        # Show first 1000 characters of response
        print(f"\nFirst 1000 characters of response:")
        print(response.text[:1000])
        
    except Exception as e:
        print(f"Error testing endpoint: {e}")

if __name__ == "__main__":
    test_edit_endpoint() 