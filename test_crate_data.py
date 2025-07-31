#!/usr/bin/env python3
"""
Test script to verify crate data generation
"""

from app import create_app
from models import Party
import random

def test_crate_data():
    app = create_app()
    with app.app_context():
        try:
            # Get parties
            parties = Party.query.limit(5).all()
            print(f"Found {len(parties)} parties")
            
            # Sample crate types
            crate_types = [
                {'crate_type_id': 'JUTE_BAG_50KG', 'crate_name': 'Jute Bags - 50 KG'},
                {'crate_type_id': 'PLASTIC_CRATE_20KG', 'crate_name': 'Plastic Crates - 20 KG'},
                {'crate_type_id': 'GUNNY_BAG_40KG', 'crate_name': 'Gunny Bags - 40 KG'}
            ]
            
            # Generate sample data
            crate_balances = []
            for i, party in enumerate(parties):
                for j, crate_type in enumerate(crate_types):
                    issued_qty = 100 + (i * 10) + (j * 5)
                    returned_qty = 50 + (i * 5) + (j * 3)
                    balance_qty = issued_qty - returned_qty
                    outstanding_qty = 20 + (i * 2) + j
                    total_outstanding = outstanding_qty * 15
                    
                    balance_data = {
                        'party_id': str(party.party_cd),
                        'party_code': str(party.party_cd),
                        'party_name': str(party.party_nm),
                        'crate_name': str(crate_type['crate_name']),
                        'issued_qty': int(issued_qty),
                        'returned_qty': int(returned_qty),
                        'balance_qty': int(balance_qty),
                        'outstanding_qty': int(outstanding_qty),
                        'total_outstanding': int(total_outstanding)
                    }
                    
                    crate_balances.append(balance_data)
            
            print(f"Generated {len(crate_balances)} crate balances")
            if crate_balances:
                print("Sample balance:", crate_balances[0])
            
            # Calculate stats
            stats = {
                'total_parties': len(parties),
                'total_crate_types': len(crate_types),
                'total_outstanding_crates': sum(b['outstanding_qty'] for b in crate_balances),
                'parties_with_outstanding': len(set(b['party_id'] for b in crate_balances if b['outstanding_qty'] > 0))
            }
            
            print("Stats:", stats)
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_crate_data()
    print(f"Test {'PASSED' if success else 'FAILED'}") 