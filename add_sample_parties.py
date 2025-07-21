#!/usr/bin/env python3
"""
Add sample parties for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Party
from datetime import datetime
from sqlalchemy import text

def add_sample_parties():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if parties already exist
            result = db.session.execute(text("SELECT COUNT(*) FROM parties"))
            if result.scalar() > 1:  # More than just Kewal
                print("✅ Sample parties already exist!")
                return
            
            print("Adding sample parties...")
            
            # Sample parties data
            sample_parties = [
                {
                    'party_cd': 'P001',
                    'party_nm': 'ABC Traders',
                    'place': 'Mumbai',
                    'phone': '022-12345678',
                    'address1': '123 Main Street, Mumbai',
                    'gstin': '27ABCDE1234F1Z5'
                },
                {
                    'party_cd': 'P002',
                    'party_nm': 'XYZ Suppliers',
                    'place': 'Delhi',
                    'phone': '011-87654321',
                    'address1': '456 Business Avenue, Delhi',
                    'gstin': '07FGHIJ5678K9L2'
                },
                {
                    'party_cd': 'P003',
                    'party_nm': 'LMN Enterprises',
                    'place': 'Bangalore',
                    'phone': '080-11223344',
                    'address1': '789 Industrial Road, Bangalore',
                    'gstin': '29MNOPQ9012R3S6'
                },
                {
                    'party_cd': 'P004',
                    'party_nm': 'DEF Corporation',
                    'place': 'Chennai',
                    'phone': '044-55667788',
                    'address1': '321 Commercial Street, Chennai',
                    'gstin': '33TUVWX3456Y7Z9'
                },
                {
                    'party_cd': 'P005',
                    'party_nm': 'GHI Limited',
                    'place': 'Kolkata',
                    'phone': '033-99887766',
                    'address1': '654 Trade Center, Kolkata',
                    'gstin': '19ABCDE7890F1G3'
                },
                {
                    'party_cd': 'P006',
                    'party_nm': 'PARMESH BHAI',
                    'place': 'Nagpur',
                    'phone': '0712-1234567',
                    'address1': 'Vijay Nagar, Nagpur',
                    'gstin': '27PARMESH1234F1Z5'
                },
                {
                    'party_cd': 'P007',
                    'party_nm': 'DILIP SAHU',
                    'place': 'Chhindwada',
                    'phone': '07162-123456',
                    'address1': 'Main Road, Chhindwada',
                    'gstin': '23DILIP5678K9L2'
                },
                {
                    'party_cd': 'P008',
                    'party_nm': 'USHA BAI',
                    'place': 'Vijay Nagar',
                    'phone': '0712-9876543',
                    'address1': 'Vijay Nagar Market, Nagpur',
                    'gstin': '27USHA9012R3S6'
                }
            ]
            
            for party_data in sample_parties:
                # Check if party already exists
                existing = db.session.execute(
                    text("SELECT COUNT(*) FROM parties WHERE party_cd = :party_cd"),
                    {'party_cd': party_data['party_cd']}
                ).scalar()
                
                if existing == 0:
                    db.session.execute(text("""
                        INSERT INTO parties (party_cd, party_nm, place, phone, address1, gstin, 
                                           bal_cd, ly_baln, ytd_dr, ytd_cr, opening_bal, closing_bal, created_date)
                        VALUES (:party_cd, :party_nm, :place, :phone, :address1, :gstin, 
                               'D', 0, 0, 0, 0, 0, :created_date)
                    """), {
                        'party_cd': party_data['party_cd'],
                        'party_nm': party_data['party_nm'],
                        'place': party_data['place'],
                        'phone': party_data['phone'],
                        'address1': party_data['address1'],
                        'gstin': party_data['gstin'],
                        'created_date': datetime.utcnow()
                    })
            
            db.session.commit()
            print("✅ Sample parties added successfully!")
            print("   - ABC Traders (Mumbai)")
            print("   - XYZ Suppliers (Delhi)")
            print("   - LMN Enterprises (Bangalore)")
            print("   - DEF Corporation (Chennai)")
            print("   - GHI Limited (Kolkata)")
            print("   - PARMESH BHAI (Nagpur)")
            print("   - DILIP SAHU (Chhindwada)")
            print("   - USHA BAI (Vijay Nagar)")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding sample parties: {e}")

if __name__ == '__main__':
    add_sample_parties() 