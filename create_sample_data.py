#!/usr/bin/env python3
"""
Create sample data for the business management system
Creates multiple users with their own data for testing multi-user functionality
"""

import os
import sys
from datetime import datetime, date, timedelta
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Company, Party, Item, Purchase, Sale, Cashbook, Bankbook
from werkzeug.security import generate_password_hash

def create_sample_data():
    """Create sample data for multiple users"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Creating sample data for multiple users...")
        
        # Create multiple users
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'role': 'admin',
                'company_name': 'Admin Business'
            },
            {
                'username': 'user1',
                'email': 'user1@example.com',
                'password': 'user123',
                'role': 'user',
                'company_name': 'ABC Traders'
            },
            {
                'username': 'user2',
                'email': 'user2@example.com',
                'password': 'user123',
                'role': 'user',
                'company_name': 'XYZ Suppliers'
            },
            {
                'username': 'user3',
                'email': 'user3@example.com',
                'password': 'user123',
                'role': 'user',
                'company_name': 'MNO Enterprises'
            }
        ]
        
        created_users = []
        
        for user_data in users_data:
            # Check if user already exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if existing_user:
                print(f"✅ User {user_data['username']} already exists")
                created_users.append(existing_user)
                continue
            
            # Create user
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                role=user_data['role'],
                is_active=True
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Create company for user
            company = Company(
                user_id=user.id,
                name=user_data['company_name'],
                address1='Sample Address',
                city='Sample City',
                phone='9876543210',
                created_date=datetime.now()
            )
            db.session.add(company)
            
            created_users.append(user)
            print(f"✅ Created user: {user_data['username']} ({user_data['company_name']})")
        
        db.session.commit()
        
        # Sample party names for each user
        party_names = {
            'user1': ['ABC Traders', 'PQR Suppliers', 'STU Limited', 'VWX Corporation', 'YZA Enterprises'],
            'user2': ['XYZ Suppliers', 'DEF Traders', 'GHI Limited', 'JKL Corporation', 'MNO Enterprises'],
            'user3': ['MNO Enterprises', 'PQR Traders', 'STU Suppliers', 'VWX Limited', 'YZA Corporation']
        }
        
        # Sample item names
        item_names = ['Rice', 'Wheat', 'Sugar', 'Oil', 'Pulses', 'Flour', 'Salt', 'Tea', 'Coffee', 'Spices']
        
        # Create sample data for each user
        for user in created_users[1:]:  # Skip admin user
            print(f"\n📊 Creating sample data for {user.username}...")
            
            # Create parties for this user
            user_parties = []
            for i, party_name in enumerate(party_names.get(user.username, ['Sample Party'])):
                party = Party(
                    user_id=user.id,
                    party_cd=f'P{user.id:02d}{i+1:02d}',
                    party_nm=party_name,
                    party_nm_hindi=party_name,
                    place='Sample City',
                    phone=f'98765{user.id:02d}{i+1:02d}',
                    bal_cd='A',
                    ly_baln=random.randint(1000, 10000),
                    ytd_dr=random.randint(5000, 50000),
                    ytd_cr=random.randint(5000, 50000),
                    address1=f'Address {i+1}',
                    address2='Sample Address',
                    address3='Sample City',
                    po='Sample PO',
                    dist='Sample District',
                    contact='Sample Contact',
                    state='Sample State',
                    pin='123456',
                    phone1=f'98765{user.id:02d}{i+1:02d}',
                    phone2=f'98765{user.id:02d}{i+2:02d}',
                    phone3=f'98765{user.id:02d}{i+3:02d}',
                    cst_no=f'CST{user.id:02d}{i+1:02d}',
                    cst_dt=date.today(),
                    trate=random.randint(5, 18),
                    agent_cd='AG001',
                    cat='Regular',
                    lpperc=random.randint(5, 15),
                    limit=random.randint(10000, 100000),
                    ledgtyp='Regular',
                    dis=random.randint(0, 10),
                    trans_cd='TR001',
                    pgno=1,
                    agent_nm='Sample Agent',
                    p_bal=random.randint(1000, 10000),
                    phone4=f'98765{user.id:02d}{i+4:02d}',
                    phone5=f'98765{user.id:02d}{i+5:02d}',
                    phone6=f'98765{user.id:02d}{i+6:02d}',
                    phone7=f'98765{user.id:02d}{i+7:02d}',
                    phone8=f'98765{user.id:02d}{i+8:02d}',
                    bst_no=f'BST{user.id:02d}{i+1:02d}',
                    bst_dt=date.today(),
                    vat_no=f'VAT{user.id:02d}{i+1:02d}',
                    acode='AC001',
                    area='Sample Area',
                    ly_cd='LY001',
                    cr_dr='DR',
                    amount=random.randint(1000, 10000),
                    page_no=1,
                    group_cd='GR001',
                    group_nm='Sample Group',
                    gstin=f'GSTIN{user.id:02d}{i+1:02d}',
                    pan=f'PAN{user.id:02d}{i+1:02d}',
                    email=f'party{i+1}@{user.username}.com',
                    fax=f'FAX{user.id:02d}{i+1:02d}',
                    mobile=f'98765{user.id:02d}{i+1:02d}',
                    opening_bal=random.randint(1000, 10000),
                    closing_bal=random.randint(1000, 10000),
                    created_date=datetime.now(),
                    modified_date=datetime.now()
                )
                db.session.add(party)
                user_parties.append(party)
            
            # Create items for this user
            user_items = []
            for i, item_name in enumerate(item_names[:5]):  # Create 5 items per user
                item = Item(
                    user_id=user.id,
                    it_cd=f'I{user.id:02d}{i+1:02d}',
                    it_nm=item_name,
                    unit='KG',
                    rate=random.randint(50, 200),
                    category='General',
                    hsn=f'HSN{user.id:02d}{i+1:02d}',
                    gst=random.randint(5, 18),
                    mrp=random.randint(60, 250),
                    sprc=random.randint(60, 250),
                    reorder_level=100,
                    opening_stock=random.randint(100, 1000),
                    closing_stock=random.randint(100, 1000),
                    created_date=datetime.now(),
                    modified_date=datetime.now()
                )
                db.session.add(item)
                user_items.append(item)
            
            # Create purchases for this user
            for i in range(10):  # Create 10 purchases per user
                purchase_date = date.today() - timedelta(days=random.randint(1, 30))
                party = random.choice(user_parties) if user_parties else None
                item = random.choice(user_items) if user_items else None
                
                purchase = Purchase(
                    user_id=user.id,
                    bill_no=1000 + i,
                    bill_date=purchase_date,
                    party_cd=party.party_cd if party else None,
                    it_cd=item.it_cd if item else None,
                    qty=random.randint(10, 100),
                    rate=random.randint(50, 200),
                    sal_amt=random.randint(5000, 25000),
                    created_date=datetime.now(),
                    modified_date=datetime.now()
                )
                db.session.add(purchase)
            
            # Create sales for this user
            for i in range(15):  # Create 15 sales per user
                sale_date = date.today() - timedelta(days=random.randint(1, 30))
                party = random.choice(user_parties) if user_parties else None
                item = random.choice(user_items) if user_items else None
                
                sale = Sale(
                    user_id=user.id,
                    bill_no=2000 + i,
                    bill_date=sale_date,
                    party_cd=party.party_cd if party else None,
                    it_cd=item.it_cd if item else None,
                    qty=random.randint(5, 50),
                    rate=random.randint(60, 250),
                    sal_amt=random.randint(3000, 20000),
                    created_date=datetime.now(),
                    modified_date=datetime.now()
                )
                db.session.add(sale)
            
            # Create cashbook entries for this user
            for i in range(20):  # Create 20 cashbook entries per user
                entry_date = date.today() - timedelta(days=random.randint(1, 30))
                
                cashbook_entry = Cashbook(
                    user_id=user.id,
                    date=entry_date,
                    narration=f'Sample cashbook entry {i+1}',
                    dr_amt=random.randint(1000, 10000) if random.choice([True, False]) else 0,
                    cr_amt=random.randint(1000, 10000) if random.choice([True, False]) else 0,
                    balance=random.randint(-50000, 50000),
                    created_date=datetime.now(),
                    modified_date=datetime.now()
                )
                db.session.add(cashbook_entry)
            
            print(f"✅ Created for {user.username}:")
            print(f"   - {len(user_parties)} parties")
            print(f"   - {len(user_items)} items")
            print(f"   - 10 purchases")
            print(f"   - 15 sales")
            print(f"   - 20 cashbook entries")
        
        # Commit all changes
        db.session.commit()
        
        print("\n🎉 Sample data creation completed!")
        print("\n📋 Login Credentials:")
        print("=" * 50)
        for user_data in users_data:
            print(f"Username: {user_data['username']}")
            print(f"Password: {user_data['password']}")
            print(f"Company: {user_data['company_name']}")
            print("-" * 30)
        
        print("\n🚀 You can now start the server and test the multi-user system!")
        print("   Each user will see only their own data.")

if __name__ == '__main__':
    create_sample_data() 
 
 
 