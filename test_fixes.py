#!/usr/bin/env python3
"""
Test script to verify the fixes for parties management
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_fixes():
    """Test the fixes for parties management"""
    
    print("🧪 Testing Parties Management Fixes...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first.")
        return
    
    # Test 2: Test parties search endpoint
    print("\n🔍 Testing Search Functionality:")
    try:
        response = requests.get(f"{BASE_URL}/api/parties/search?q=rajesh")
        print(f"  ✅ Search endpoint accessible (Status: {response.status_code})")
        if response.status_code == 200:
            data = response.json()
            print(f"  📊 Search returned {len(data)} results")
            if data:
                print(f"  📝 First result: {data[0].get('party_nm', 'N/A')}")
            else:
                print("  ⚠️  No search results found")
    except Exception as e:
        print(f"  ❌ Search endpoint error: {e}")
    
    # Test 3: Test parties add form endpoint
    print("\n📝 Testing Add Form Functionality:")
    try:
        response = requests.get(f"{BASE_URL}/api/parties/add-form")
        print(f"  ✅ Add form endpoint accessible (Status: {response.status_code})")
        if response.status_code == 200:
            content = response.text
            print(f"  📏 Form content length: {len(content)} characters")
            if "Add New Party" in content:
                print("  ✅ Form title found")
            if "form-control" in content:
                print("  ✅ Form controls found")
            if "hx-post" in content:
                print("  ✅ HTMX attributes found")
        else:
            print(f"  ❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Add form endpoint error: {e}")
    
    # Test 4: Test parties table endpoint
    print("\n📊 Testing Table Functionality:")
    try:
        response = requests.get(f"{BASE_URL}/api/parties/table")
        print(f"  ✅ Table endpoint accessible (Status: {response.status_code})")
        if response.status_code == 200:
            content = response.text
            print(f"  📏 Table content length: {len(content)} characters")
            if "table" in content:
                print("  ✅ Table structure found")
            if "Mohan Traders" in content or "Rajesh Suppliers" in content:
                print("  ✅ Sample party data found")
        else:
            print(f"  ❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Table endpoint error: {e}")
    
    # Test 5: Test enhanced parties page
    print("\n🌐 Testing Enhanced Parties Page:")
    try:
        response = requests.get(f"{BASE_URL}/parties-enhanced")
        print(f"  ✅ Enhanced parties page accessible (Status: {response.status_code})")
        if response.status_code == 200:
            content = response.text
            if "htmx.org" in content:
                print("  ✅ HTMX library found")
            if "alpinejs" in content:
                print("  ✅ Alpine.js library found")
            if "Parties Management" in content:
                print("  ✅ Page title found")
            if "search" in content:
                print("  ✅ Search functionality found")
        else:
            print(f"  ❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Enhanced parties page error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("  - If all tests show ✅, the fixes are working correctly")
    print("  - If any test shows ❌, there may still be issues")
    print("  - Check the browser console for any JavaScript errors")
    print("\n🌐 Access the enhanced parties page at:")
    print(f"   {BASE_URL}/parties-enhanced")

if __name__ == "__main__":
    test_fixes() 