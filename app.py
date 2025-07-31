#!/usr/bin/env python3
"""
Modern Business Management System - Web Application
Main Flask application entry point
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps
import logging
import random

# Import models and routes
from database import db
from models import User, Company, Party, Item, Purchase, Sale, Cashbook, Bankbook
from auth import auth_bp
from api import api_bp
from user_management import user_bp
from reports_module import reports_bp
from inventory_module import inventory_bp
from demo_routes import demo
from dashboard_api import dashboard_api
from parties_api import parties_api
from items_api import items_api
from sales_api import sales_api
from purchases_api import purchases_api
from enhanced_api import enhanced_api
from forms import LoginForm, RegistrationForm

# Import new management systems
from purchase_management import PurchaseManagementSystem
from sales_management import SalesManagementSystem
from inventory_management import InventoryManagementSystem
from financial_management import FinancialManagementSystem
from crate_management import CrateManagementSystem
from packing_management import PackingManagementSystem
from transport_management import TransportManagementSystem
from gate_pass_management import GatePassManagementSystem
from agent_management import AgentManagementSystem
from bank_management import BankManagementSystem
from schedule_management import ScheduleManagementSystem
from narration_management import NarrationManagementSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration - Support both SQLite and PostgreSQL
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Database configuration - Force SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///business_web.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(demo, url_prefix='')
    app.register_blueprint(dashboard_api, url_prefix='')
    app.register_blueprint(parties_api, url_prefix='')
    app.register_blueprint(items_api, url_prefix='')
    app.register_blueprint(sales_api, url_prefix='')
    app.register_blueprint(purchases_api, url_prefix='')
    app.register_blueprint(enhanced_api, url_prefix='/api/enhanced')
    
    # Register new management system API blueprints
    from purchase_management_api import purchase_management_api
    from sales_management_api import sales_management_api
    from inventory_management_api import inventory_management_api
    from financial_management_api import financial_management_api
    from crate_management_api import crate_management_bp
    from packing_management_api import packing_management_bp
    from transport_management_api import transport_management_bp
    from gate_pass_management_api import gate_pass_management_bp
    from agent_management_api import agent_management_bp
    from bank_management_api import bank_management_bp
    from schedule_management_api import schedule_management_bp
    from narration_management_api import narration_management_bp
    
    app.register_blueprint(purchase_management_api, url_prefix='')
    app.register_blueprint(sales_management_api, url_prefix='')
    app.register_blueprint(inventory_management_api, url_prefix='')
    app.register_blueprint(packing_management_bp, url_prefix='')
    app.register_blueprint(financial_management_api, url_prefix='')
    app.register_blueprint(crate_management_bp, url_prefix='')
    app.register_blueprint(transport_management_bp, url_prefix='')
    app.register_blueprint(gate_pass_management_bp, url_prefix='')
    app.register_blueprint(agent_management_bp, url_prefix='')
    app.register_blueprint(bank_management_bp, url_prefix='')
    app.register_blueprint(schedule_management_bp, url_prefix='')
    app.register_blueprint(narration_management_bp, url_prefix='')
    
    # Main routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard with business overview (user-specific)"""
        try:
            # Get user-specific statistics
            total_parties = Party.query.filter_by(user_id=current_user.id).count()
            total_items = Item.query.filter_by(user_id=current_user.id).count()
            total_purchases = Purchase.query.filter_by(user_id=current_user.id).count()
            total_sales = Sale.query.filter_by(user_id=current_user.id).count()
            
            # Get recent purchases and sales
            recent_purchases = Purchase.query.filter_by(user_id=current_user.id).order_by(Purchase.bill_date.desc()).limit(5).all()
            recent_sales = Sale.query.filter_by(user_id=current_user.id).order_by(Sale.bill_date.desc()).limit(5).all()
            
            stats = {
                'parties': total_parties,
                'items_count': total_items,
                'purchases': total_purchases,
                'sales': total_sales
            }
            
            return render_template('dashboard.html', 
                                stats=stats,
                                recent_purchases=recent_purchases,
                                recent_sales=recent_sales)
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            flash('Error loading dashboard data', 'error')
            return render_template('dashboard.html', stats={}, recent_purchases=[], recent_sales=[])
    
    @app.route('/dashboard-enhanced')
    @login_required
    def dashboard_enhanced():
        """Enhanced dashboard with modern features"""
        try:
            # Get user-specific statistics
            total_parties = Party.query.filter_by(user_id=current_user.id).count()
            total_items = Item.query.filter_by(user_id=current_user.id).count()
            
            # Calculate monthly totals
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            monthly_sales = db.session.query(db.func.sum(Sale.sal_amt)).filter(
                Sale.user_id == current_user.id,
                db.func.extract('month', Sale.bill_date) == current_month,
                db.func.extract('year', Sale.bill_date) == current_year
            ).scalar() or 0
            
            monthly_purchases = db.session.query(db.func.sum(Purchase.sal_amt)).filter(
                Purchase.user_id == current_user.id,
                db.func.extract('month', Purchase.bill_date) == current_month,
                db.func.extract('year', Purchase.bill_date) == current_year
            ).scalar() or 0
            
            stats = {
                'parties': total_parties,
                'items_count': total_items,
                'monthly_sales': monthly_sales,
                'monthly_purchases': monthly_purchases
            }
            
            return render_template('dashboard_enhanced.html', stats=stats)
        except Exception as e:
            logger.error(f"Enhanced dashboard error: {e}")
            flash('Error loading enhanced dashboard data', 'error')
            return render_template('dashboard_enhanced.html', stats={})
    
    @app.route('/test-enhanced')
    @login_required
    def test_enhanced():
        """Test route for enhanced features"""
        return render_template('dashboard_enhanced.html', stats={})
    
    @app.route('/parties')
    @login_required
    def parties():
        """Parties management page (user-specific)"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        query = Party.query.filter_by(user_id=current_user.id)
        if search:
            query = query.filter(Party.party_nm.contains(search) | Party.party_cd.contains(search))
        
        parties = query.paginate(page=page, per_page=20, error_out=False)
        return render_template('parties.html', parties=parties, search=search)
    
    @app.route('/parties-enhanced')
    @login_required
    def parties_enhanced():
        """Enhanced parties management page with modern features"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        query = Party.query.filter_by(user_id=current_user.id)
        if search:
            query = query.filter(Party.party_nm.contains(search) | Party.party_cd.contains(search))
        
        parties = query.paginate(page=page, per_page=20, error_out=False)
        return render_template('parties_enhanced.html', parties=parties, search=search)
    
    @app.route('/items')
    @login_required
    def items():
        """Items management page (user-specific)"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        query = Item.query.filter_by(user_id=current_user.id)
        if search:
            query = query.filter(Item.it_nm.contains(search) | Item.it_cd.contains(search))
        
        items = query.paginate(page=page, per_page=20, error_out=False)
        return render_template('items.html', items=items, search=search)
    
    @app.route('/items-enhanced')
    @login_required
    def items_enhanced():
        """Enhanced items management page"""
        search = request.args.get('search', '')
        print("DEBUG: items_enhanced route called")
        print("DEBUG: Rendering items_enhanced.html template")
        return render_template('items_enhanced.html', search=search)
    
    @app.route('/debug-items')
    @login_required
    def debug_items():
        """Debug route to test template rendering"""
        return """
        <html>
        <head><title>Debug Items</title></head>
        <body>
        <h1>Debug Items Route</h1>
        <p>This confirms the server is running and routes are working.</p>
        <a href="/items-enhanced">Go to Items Enhanced</a>
        </body>
        </html>
        """
    
    @app.route('/purchases')
    @login_required
    def purchases():
        """Purchases management page"""
        page = request.args.get('page', 1, type=int)
        purchases = Purchase.query.filter_by(user_id=current_user.id).order_by(Purchase.bill_date.desc()).paginate(
            page=page, per_page=20, error_out=False)
        return render_template('purchases.html', purchases=purchases)
    
    @app.route('/purchases-enhanced')
    @login_required
    def purchases_enhanced():
        """Enhanced purchases management page"""
        search = request.args.get('search', '')
        return render_template('purchases_enhanced.html', search=search)
    
    @app.route('/sales')
    @login_required
    def sales():
        """Sales management page"""
        page = request.args.get('page', 1, type=int)
        sales = Sale.query.filter_by(user_id=current_user.id).order_by(Sale.bill_date.desc()).paginate(
            page=page, per_page=20, error_out=False)
        return render_template('sales.html', sales=sales)
    
    @app.route('/sales-enhanced')
    @login_required
    def sales_enhanced():
        """Enhanced sales management page"""
        search = request.args.get('search', '')
        return render_template('sales_enhanced.html', search=search)
    
    # New Management System Routes
    @app.route('/purchase-management')
    @login_required
    def purchase_management():
        """Advanced Purchase Management page"""
        return render_template('purchase_management.html')
    
    @app.route('/sales-management')
    @login_required
    def sales_management():
        """Advanced Sales Management page"""
        return render_template('sales_management.html')
    
    @app.route('/inventory-management')
    @login_required
    def inventory_management():
        """Advanced Inventory Management page"""
        return render_template('inventory_management.html')
    
    @app.route('/financial-management')
    @login_required
    def financial_management():
        """Advanced Financial Management page"""
        return render_template('financial_management.html')
    
    @app.route('/crate-management')
    @login_required
    def crate_management():
        """Crate Management System"""
        try:
            # Get sample data for demonstration
            from models import Party
            
            # Get parties for the current user - TEMPORARILY REMOVE USER FILTER
            parties = Party.query.limit(10).all()  # Removed user_id filter temporarily
            print(f"DEBUG: Found {len(parties)} parties for user {current_user.id}")
            
            # Sample crate types
            crate_types = [
                {'crate_type_id': 'JUTE_BAG_50KG', 'crate_name': 'Jute Bags - 50 KG'},
                {'crate_type_id': 'PLASTIC_CRATE_20KG', 'crate_name': 'Plastic Crates - 20 KG'},
                {'crate_type_id': 'GUNNY_BAG_40KG', 'crate_name': 'Gunny Bags - 40 KG'},
                {'crate_type_id': 'CARDBOARD_BOX_10KG', 'crate_name': 'Cardboard Boxes - 10 KG'},
                {'crate_type_id': 'MESH_BAG_25KG', 'crate_name': 'Mesh Bags - 25 KG'}
            ]
            
            # Sample crate balances data - SIMPLIFIED APPROACH
            crate_balances = []
            
            # Generate data for each party and crate type
            for i, party in enumerate(parties):
                for j, crate_type in enumerate(crate_types):
                    # Generate sample data with fixed values for testing
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
            
            print(f"DEBUG: Generated {len(crate_balances)} crate balances")
            if crate_balances:
                print(f"DEBUG: Sample balance: {crate_balances[0]}")
            
            # Calculate statistics
            stats = {
                'total_parties': len(parties),
                'total_crate_types': len(crate_types),
                'total_outstanding_crates': sum(b['outstanding_qty'] for b in crate_balances),
                'parties_with_outstanding': len(set(b['party_id'] for b in crate_balances if b['outstanding_qty'] > 0))
            }
            
            print(f"DEBUG: Stats: {stats}")
            
            return render_template('crate_management.html', 
                                 parties=parties,
                                 crate_types=crate_types,
                                 crate_balances=crate_balances,
                                 stats=stats)
        except Exception as e:
            print(f"DEBUG: Error in crate_management route: {e}")
            import traceback
            traceback.print_exc()
            # Fallback with empty data
            return render_template('crate_management.html', 
                                 parties=[],
                                 crate_types=[],
                                 crate_balances=[],
                                 stats={'total_parties': 0, 'total_crate_types': 0, 'total_outstanding_crates': 0, 'parties_with_outstanding': 0})
    
    @app.route('/packing-management')
    @login_required
    def packing_management():
        """Packing Management System"""
        return render_template('packing_management.html')
    
    @app.route('/transport-management')
    @login_required
    def transport_management():
        """Transport & Logistics Management System"""
        return render_template('transport_management.html')
    
    @app.route('/gate-pass-management')
    @login_required
    def gate_pass_management():
        """Gate Pass Management System"""
        return render_template('gate_pass_management.html')
    
    @app.route('/agent-management')
    @login_required
    def agent_management():
        """Agent Management System"""
        return render_template('agent_management.html')

    @app.route('/bank-management')
    @login_required
    def bank_management():
        """Bank Management System"""
        return render_template('bank_management.html')

    @app.route('/schedule-management')
    @login_required
    def schedule_management():
        """Schedule Management System"""
        return render_template('schedule_management.html')

    @app.route('/narration-management')
    @login_required
    def narration_management():
        """Narration Management System"""
        return render_template('narration_management.html')
    
    @app.route('/cashbook')
    @login_required
    def cashbook():
        """Cashbook management page"""
        page = request.args.get('page', 1, type=int)
        cashbook_entries = Cashbook.query.filter_by(user_id=current_user.id).order_by(Cashbook.date.desc()).paginate(
            page=page, per_page=20, error_out=False)
        return render_template('cashbook.html', cashbook_entries=cashbook_entries)
    
    # API Routes
    @app.route('/api/cashbook', methods=['POST'])
    @login_required
    def api_cashbook_create():
        """Create new cashbook entry"""
        try:
            data = request.get_json()
            
            new_entry = Cashbook(
                user_id=current_user.id,
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                description=data['description'],
                amount=data['amount'],
                type=data['type'],
                category=data.get('category', ''),
                reference_no=data.get('reference_no', ''),
                notes=data.get('notes', '')
            )
            
            db.session.add(new_entry)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Cashbook entry created successfully',
                'entry': {
                    'id': new_entry.id,
                    'date': new_entry.date.strftime('%Y-%m-%d'),
                    'description': new_entry.description,
                    'amount': new_entry.amount,
                    'type': new_entry.type,
                    'category': new_entry.category,
                    'reference_no': new_entry.reference_no,
                    'notes': new_entry.notes
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/cashbook/<int:entry_id>', methods=['DELETE'])
    @login_required
    def api_cashbook_delete(entry_id):
        """Delete cashbook entry"""
        try:
            entry = Cashbook.query.filter_by(id=entry_id, user_id=current_user.id).first()
            if not entry:
                return jsonify({'error': 'Entry not found'}), 404
            
            db.session.delete(entry)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Entry deleted successfully'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/parties')
    @login_required
    def api_parties():
        """Get parties for API"""
        try:
            parties = Party.query.filter_by(user_id=current_user.id).all()
            return jsonify({
                'success': True,
                'parties': [{
                    'id': party.id,
                    'party_cd': party.party_cd,
                    'party_nm': party.party_nm,
                    'address': party.address,
                    'phone': party.phone,
                    'email': party.email,
                    'balance': party.balance
                } for party in parties]
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/ledger-reports')
    @login_required
    def ledger_reports():
        """Ledger reports page"""
        return render_template('ledger_reports.html')
    
    @app.route('/purchase-sale-entry')
    @login_required
    def purchase_sale_entry():
        """Purchase/Sale entry page"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return render_template('purchase_sale_entry.html', current_time=current_time)
    
    @app.route('/reports')
    @login_required
    def reports():
        """Reports page"""
        return render_template('reports.html')
    
    @app.route('/settings')
    @login_required
    def settings():
        """Settings page"""
        return render_template('settings.html')
    
    @app.route('/print/<bill_type>/<int:bill_no>')
    @login_required
    def print_bill(bill_type, bill_no):
        """Print bill page"""
        try:
            if bill_type == 'purchase':
                bill = Purchase.query.filter_by(bill_no=bill_no, user_id=current_user.id).first()
                if not bill:
                    flash('Purchase bill not found', 'error')
                    return redirect(url_for('purchases'))
                
                # Get party details
                party = Party.query.filter_by(id=bill.party_id, user_id=current_user.id).first()
                
                return render_template('print_bill.html', 
                                    bill=bill, 
                                    party=party, 
                                    bill_type='Purchase',
                                    items=bill.items if hasattr(bill, 'items') else [])
            
            elif bill_type == 'sale':
                bill = Sale.query.filter_by(bill_no=bill_no, user_id=current_user.id).first()
                if not bill:
                    flash('Sale bill not found', 'error')
                    return redirect(url_for('sales'))
                
                # Get party details
                party = Party.query.filter_by(id=bill.party_id, user_id=current_user.id).first()
                
                return render_template('print_bill.html', 
                                    bill=bill, 
                                    party=party, 
                                    bill_type='Sale',
                                    items=bill.items if hasattr(bill, 'items') else [])
            
            else:
                flash('Invalid bill type', 'error')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            logger.error(f"Print bill error: {e}")
            flash('Error printing bill', 'error')
            return redirect(url_for('dashboard'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.route('/test-crate-data')
    def test_crate_data():
        """Test route to debug crate data without authentication"""
        try:
            from models import Party
            
            # Get all parties (not filtered by user)
            parties = Party.query.limit(5).all()
            print(f"TEST: Found {len(parties)} parties total")
            
            # Sample crate types
            crate_types = [
                {'crate_type_id': 'JUTE_BAG_50KG', 'crate_name': 'Jute Bags - 50 KG'},
                {'crate_type_id': 'PLASTIC_CRATE_20KG', 'crate_name': 'Plastic Crates - 20 KG'}
            ]
            
            # Sample crate balances data
            crate_balances = []
            for party in parties:
                for crate_type in crate_types:
                    # Generate sample data
                    issued_qty = random.randint(50, 200)
                    returned_qty = random.randint(20, issued_qty - 10)
                    balance_qty = issued_qty - returned_qty
                    outstanding_qty = random.randint(0, balance_qty)
                    
                    crate_balances.append({
                        'party_id': party.party_cd,
                        'party_code': party.party_cd,
                        'party_name': party.party_nm,
                        'crate_name': crate_type['crate_name'],
                        'issued_qty': issued_qty,
                        'returned_qty': returned_qty,
                        'balance_qty': balance_qty,
                        'outstanding_qty': outstanding_qty,
                        'total_outstanding': outstanding_qty * random.randint(5, 15)
                    })
            
            print(f"TEST: Generated {len(crate_balances)} crate balances")
            
            return jsonify({
                'success': True,
                'parties_count': len(parties),
                'crate_balances_count': len(crate_balances),
                'sample_balance': crate_balances[0] if crate_balances else None,
                'parties': [{'code': p.party_cd, 'name': p.party_nm} for p in parties]
            })
            
        except Exception as e:
            print(f"TEST: Error: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")
    app.run(debug=True, host='0.0.0.0', port=5000) 