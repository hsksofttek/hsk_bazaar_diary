#!/usr/bin/env python3
"""
Add sample purchase data for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Purchase
from datetime import datetime, date
from sqlalchemy import text

def add_sample_purchases():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if purchases already exist
            result = db.session.execute(text("SELECT COUNT(*) FROM purchases"))
            if result.scalar() > 0:
                print("✅ Sample purchases already exist!")
                return
            
            print("Adding sample purchases...")
            
            # Sample purchase data
            sample_purchases = [
                {
                    'bill_no': 1001,
                    'bill_date': date(2025, 7, 19),
                    'party_cd': '1',  # Kewal
                    'it_cd': 'TOMATO',
                    'qty': 870,  # 870 bags
                    'tot_smt': 43500,  # 50kg per bag
                    'rate': 200,  # Rs 200 per kg
                    'sal_amt': 8700000,  # 870 * 50 * 200
                    'tot_amt': 8700000
                },
                {
                    'bill_no': 1002,
                    'bill_date': date(2025, 7, 19),
                    'party_cd': '1',  # Kewal
                    'it_cd': 'TOMATO',
                    'qty': 117,  # 117 bags
                    'tot_smt': 5850,  # 50kg per bag
                    'rate': 200,  # Rs 200 per kg
                    'sal_amt': 1170000,  # 117 * 50 * 200
                    'tot_amt': 1170000
                }
            ]
            
            for purchase_data in sample_purchases:
                purchase = Purchase(**purchase_data)
                db.session.add(purchase)
            
            db.session.commit()
            print("✅ Sample purchases added successfully!")
            print("   - Purchase 1: 870 bags of TOMATO")
            print("   - Purchase 2: 117 bags of TOMATO")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding sample purchases: {e}")

if __name__ == '__main__':
    add_sample_purchases() 
 
 
 