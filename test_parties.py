#!/usr/bin/env python3
"""
Test script to check and add sample parties to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Party
from datetime import datetime

def test_parties():
    app = create_app()
    
    with app.app_context():
        # Check existing parties
        parties = Party.query.all()
        print(f"Found {len(parties)} parties in database")
        
        if len(parties) == 0:
            print("No parties found. Adding sample parties...")
            
            # Add sample parties
            sample_parties = [
                {
                    'party_cd': 'P001',
                    'party_nm': 'ABC Traders',
                    'place': 'Mumbai',
                    'phone': '022-12345678',
                    'address1': '123 Main Street',
                    'gstin': '27ABCDE1234F1Z5'
                },
                {
                    'party_cd': 'P002',
                    'party_nm': 'XYZ Suppliers',
                    'place': 'Delhi',
                    'phone': '011-87654321',
                    'address1': '456 Business Avenue',
                    'gstin': '07FGHIJ5678K9L2'
                },
                {
                    'party_cd': 'P003',
                    'party_nm': 'LMN Enterprises',
                    'place': 'Bangalore',
                    'phone': '080-11223344',
                    'address1': '789 Industrial Road',
                    'gstin': '29MNOPQ9012R3S6'
                },
                {
                    'party_cd': 'P004',
                    'party_nm': 'DEF Corporation',
                    'place': 'Chennai',
                    'phone': '044-55667788',
                    'address1': '321 Commercial Street',
                    'gstin': '33TUVWX3456Y7Z9'
                },
                {
                    'party_cd': 'P005',
                    'party_nm': 'GHI Limited',
                    'place': 'Kolkata',
                    'phone': '033-99887766',
                    'address1': '654 Trade Center',
                    'gstin': '19ABCDE7890F1G3'
                }
            ]
            
            for party_data in sample_parties:
                party = Party(
                    party_cd=party_data['party_cd'],
                    party_nm=party_data['party_nm'],
                    place=party_data['place'],
                    phone=party_data['phone'],
                    address1=party_data['address1'],
                    gstin=party_data['gstin'],
                    bal_cd='D',
                    ly_baln=0,
                    ytd_dr=0,
                    ytd_cr=0,
                    opening_bal=0,
                    closing_bal=0,
                    created_date=datetime.utcnow()
                )
                db.session.add(party)
            
            try:
                db.session.commit()
                print("Successfully added 5 sample parties!")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding parties: {e}")
        else:
            print("Existing parties:")
            for party in parties[:5]:  # Show first 5
                print(f"  {party.party_cd}: {party.party_nm} ({party.place})")

if __name__ == '__main__':
    test_parties() 