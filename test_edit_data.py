#!/usr/bin/env python3
"""
Test script to verify sale data for bill 2002
"""

from app import create_app
from database import db
from models import Sale, Party, Item

def test_sale_data():
    app = create_app()
    
    with app.app_context():
        print("=== TESTING SALE DATA FOR BILL 2002 ===")
        
        # Test 1: Check if sales exist for bill 2002
        sales = Sale.query.filter_by(bill_no=2002).all()
        print(f"Found {len(sales)} sales for bill 2002")
        
        if not sales:
            print("❌ No sales found for bill 2002")
            return
        
        # Test 2: Check user_id
        user_ids = set(sale.user_id for sale in sales)
        print(f"User IDs: {user_ids}")
        
        # Test 3: Show all sale items
        print("\n=== SALE ITEMS ===")
        for i, sale in enumerate(sales):
            print(f"Item {i+1}:")
            print(f"  - it_cd: {sale.it_cd}")
            print(f"  - qty: {sale.qty}")
            print(f"  - rate: {sale.rate}")
            print(f"  - discount: {sale.discount}")
            print(f"  - sal_amt: {sale.sal_amt}")
            print(f"  - user_id: {sale.user_id}")
        
        # Test 4: Prepare the data as the API would
        sale_items_data = []
        for sale in sales:
            item_data = {
                'it_cd': sale.it_cd,
                'qty': float(sale.qty) if sale.qty else 0.0,
                'rate': float(sale.rate) if sale.rate else 0.0,
                'discount': float(sale.discount) if sale.discount else 0.0,
                'amount': float(sale.sal_amt) if sale.sal_amt else 0.0
            }
            sale_items_data.append(item_data)
        
        print(f"\n=== PREPARED DATA ===")
        print(f"Total items: {len(sale_items_data)}")
        print(f"Data: {sale_items_data}")
        
        # Test 5: Check if items exist
        print(f"\n=== ITEM VERIFICATION ===")
        for item_data in sale_items_data:
            item = Item.query.filter_by(it_cd=item_data['it_cd']).first()
            if item:
                print(f"✅ Item {item_data['it_cd']} exists: {item.it_nm}")
            else:
                print(f"❌ Item {item_data['it_cd']} NOT FOUND")

if __name__ == "__main__":
    test_sale_data() 