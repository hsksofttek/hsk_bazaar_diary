#!/usr/bin/env python3
"""
Simple test script to check if the API endpoints are working
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoints():
    """Test the API endpoints"""
    
    print("Testing API endpoints...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running. Please start the server first.")
        return
    
    # Test 2: Test parties search endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/parties/search?q=test")
        print(f"✓ Parties search endpoint accessible (Status: {response.status_code})")
        if response.status_code == 200:
            data = response.json()
            print(f"  - Search returned {len(data)} results")
    except Exception as e:
        print(f"✗ Parties search endpoint error: {e}")
    
    # Test 3: Test parties add form endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/parties/add-form")
        print(f"✓ Parties add form endpoint accessible (Status: {response.status_code})")
        if response.status_code == 200:
            print(f"  - Form content length: {len(response.text)} characters")
    except Exception as e:
        print(f"✗ Parties add form endpoint error: {e}")
    
    # Test 4: Test parties table endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/parties/table")
        print(f"✓ Parties table endpoint accessible (Status: {response.status_code})")
        if response.status_code == 200:
            print(f"  - Table content length: {len(response.text)} characters")
    except Exception as e:
        print(f"✗ Parties table endpoint error: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_endpoints() 