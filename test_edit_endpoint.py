#!/usr/bin/env python3
"""
Test script to directly test the sales edit endpoint
"""

import requests
import json

def test_edit_endpoint():
    # Test the edit endpoint directly
    url = "http://localhost:5000/api/sales/edit/2002"
    
    # You'll need to add your session cookie here
    # First, let's just test if the endpoint responds
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        print(f"First 500 characters: {response.text[:500]}")
        
        # Look for the JavaScript data
        if "window.editSaleData" in response.text:
            print("✅ window.editSaleData found in response")
        else:
            print("❌ window.editSaleData NOT found in response")
            
        if "saleItems: 6" in response.text or "saleItems: 0" in response.text:
            print("✅ saleItems count found in response")
        else:
            print("❌ saleItems count NOT found in response")
            
    except Exception as e:
        print(f"Error testing endpoint: {e}")

if __name__ == "__main__":
    test_edit_endpoint() 