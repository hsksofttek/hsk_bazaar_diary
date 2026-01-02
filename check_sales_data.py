#!/usr/bin/env python3
"""
Check what sales data actually exists in the database
"""

import sqlite3
import os

def check_sales_data():
    print("=== CHECKING SALES DATA ===")
    
    # Check if database exists
    db_path = "business_web.db"
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"✅ Database found: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if sales table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sale'")
        if not cursor.fetchone():
            print("❌ Sales table not found")
            return
        
        print("✅ Sales table found")
        
        # Get all sales
        cursor.execute("SELECT * FROM sale LIMIT 10")
        sales = cursor.fetchall()
        
        print(f"Found {len(sales)} sales (showing first 10):")
        for sale in sales:
            print(f"  Sale: {sale}")
        
        # Get sales for bill 2002 specifically
        cursor.execute("SELECT * FROM sale WHERE bill_no = 2002")
        bill_2002_sales = cursor.fetchall()
        
        print(f"\nSales for bill 2002: {len(bill_2002_sales)}")
        for sale in bill_2002_sales:
            print(f"  Bill 2002 Sale: {sale}")
        
        # Get sales for bill 2003 specifically
        cursor.execute("SELECT * FROM sale WHERE bill_no = 2003")
        bill_2003_sales = cursor.fetchall()
        
        print(f"\nSales for bill 2003: {len(bill_2003_sales)}")
        for sale in bill_2003_sales:
            print(f"  Bill 2003 Sale: {sale}")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(sale)")
        columns = cursor.fetchall()
        print(f"\nSales table columns:")
        for col in columns:
            print(f"  {col}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sales_data() 