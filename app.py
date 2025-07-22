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
from forms import LoginForm, RegistrationForm

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
            
            # Get recent transactions for this user
            recent_purchases = Purchase.query.filter_by(user_id=current_user.id)\
                .order_by(Purchase.created_date.desc()).limit(5).all()
            recent_sales = Sale.query.filter_by(user_id=current_user.id)\
                .order_by(Sale.created_date.desc()).limit(5).all()
            
            # Get user's company info
            company = Company.query.filter_by(user_id=current_user.id).first()
            
            return render_template('dashboard.html',
                                 user=current_user,
                                 company=company,
                                 total_parties=total_parties,
                                 total_items=total_items,
                                 total_purchases=total_purchases,
                                 total_sales=total_sales,
                                 recent_purchases=recent_purchases,
                                 recent_sales=recent_sales)
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            flash('Error loading dashboard data', 'error')
            return render_template('dashboard.html')
    
    @app.route('/dashboard-enhanced')
    @login_required
    def dashboard_enhanced():
        """Enhanced dashboard with modern features"""
        try:
            print("DEBUG: Entering dashboard_enhanced function")
            
            # Get user-specific statistics with proper type conversion
            parties_count = Party.query.filter_by(user_id=current_user.id).count()
            items_count = Item.query.filter_by(user_id=current_user.id).count()
            
            print(f"DEBUG: Raw counts - parties: {parties_count} (type: {type(parties_count)}), items: {items_count} (type: {type(items_count)})")
            
            # Ensure proper type conversion and handle None values
            stats = {
                'parties': int(parties_count) if parties_count is not None else 0,
                'items_count': int(items_count) if items_count is not None else 0,
                'monthly_sales': 0.0,
                'monthly_purchases': 0.0
            }
            
            print(f"DEBUG: Processed stats: {stats}")
            
            # Calculate monthly totals
            start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            from sqlalchemy import func
            
            monthly_sales = db.session.query(func.sum(Sale.sal_amt)).filter(
                Sale.user_id == current_user.id,
                Sale.bill_date >= start_of_month
            ).scalar()
            stats['monthly_sales'] = float(monthly_sales) if monthly_sales is not None else 0.0
            
            monthly_purchases = db.session.query(func.sum(Purchase.sal_amt)).filter(
                Purchase.user_id == current_user.id,
                Purchase.bill_date >= start_of_month
            ).scalar()
            stats['monthly_purchases'] = float(monthly_purchases) if monthly_purchases is not None else 0.0
            
            print(f"DEBUG: Monthly totals calculated: sales={stats['monthly_sales']}, purchases={stats['monthly_purchases']}")
            
            # Get user's company info
            company = Company.query.filter_by(user_id=current_user.id).first()
            
            print("DEBUG: About to render dashboard_enhanced.html")
            
            return render_template('dashboard_enhanced.html', 
                                 stats=stats,
                                 company=company,
                                 user=current_user)
        except Exception as e:
            print(f"DEBUG: Error in dashboard_enhanced: {e}")
            logger.error(f"Dashboard enhanced error: {e}")
            # Return with safe default values instead of redirecting
            return render_template('dashboard_enhanced.html', 
                                 stats={'parties': 0, 'items_count': 0, 'monthly_sales': 0.0, 'monthly_purchases': 0.0},
                                 company=None,
                                 user=current_user)
    
    @app.route('/test-enhanced')
    @login_required
    def test_enhanced():
        """Test route for enhanced dashboard"""
        return render_template('dashboard_enhanced.html', 
                             stats={'parties': 3, 'items_count': 5, 'monthly_sales': 1000, 'monthly_purchases': 800},
                             company=None,
                             user=current_user)
    
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
        """Purchases management page (user-specific)"""
        page = request.args.get('page', 1, type=int)
        purchases = Purchase.query.filter_by(user_id=current_user.id)\
            .order_by(Purchase.bill_date.desc()).paginate(
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
        """Sales management page (user-specific)"""
        page = request.args.get('page', 1, type=int)
        sales = Sale.query.filter_by(user_id=current_user.id)\
            .order_by(Sale.bill_date.desc()).paginate(
            page=page, per_page=20, error_out=False)
        return render_template('sales.html', sales=sales)
    
    @app.route('/sales-enhanced')
    @login_required
    def sales_enhanced():
        """Enhanced sales management page"""
        search = request.args.get('search', '')
        return render_template('sales_enhanced.html', search=search)
    
    @app.route('/cashbook')
    @login_required
    def cashbook():
        """Cashbook management page (user-specific)"""
        page = request.args.get('page', 1, type=int)
        cashbook_entries = Cashbook.query.filter_by(user_id=current_user.id)\
            .order_by(Cashbook.date.desc()).paginate(
            page=page, per_page=20, error_out=False)
        return render_template('cashbook.html', cashbook_entries=cashbook_entries)
    
    @app.route('/api/cashbook', methods=['POST'])
    @login_required
    def api_cashbook_create():
        """Create new cashbook entry"""
        try:
            data = request.get_json()
            
            # Determine debit or credit amount
            transaction_type = data.get('transaction_type', 'Payment')
            amount = float(data.get('amount', 0))
            
            if transaction_type == 'Receipt':
                dr_amt = 0
                cr_amt = amount
            else:
                dr_amt = amount
                cr_amt = 0
            
            # Calculate balance (this is a simplified calculation)
            # In a real system, you'd calculate running balance
            balance = cr_amt - dr_amt
            
            cashbook_entry = Cashbook(
                user_id=current_user.id,
                date=datetime.strptime(data.get('transaction_date'), '%Y-%m-%d').date(),
                narration=data.get('narration', ''),
                dr_amt=dr_amt,
                cr_amt=cr_amt,
                balance=balance,
                party_cd=data.get('party_code', ''),
                voucher_type=transaction_type,
                voucher_no=data.get('voucher_no', '')
            )
            
            db.session.add(cashbook_entry)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Cashbook entry created successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    @app.route('/api/cashbook/<int:entry_id>', methods=['DELETE'])
    @login_required
    def api_cashbook_delete(entry_id):
        """Delete cashbook entry"""
        try:
            entry = Cashbook.query.filter_by(id=entry_id, user_id=current_user.id).first()
            if not entry:
                return jsonify({'success': False, 'message': 'Entry not found'})
            
            db.session.delete(entry)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Entry deleted successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    @app.route('/api/parties')
    @login_required
    def api_parties():
        """Get parties for dropdown"""
        try:
            parties = Party.query.filter_by(user_id=current_user.id).all()
            return jsonify({
                'parties': [
                    {
                        'party_cd': party.party_cd,
                        'party_nm': party.party_nm
                    }
                    for party in parties
                ]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/ledger-reports')
    @login_required
    def ledger_reports():
        """Ledger reports page"""
        return render_template('ledger_reports.html')
    
    @app.route('/purchase-sale-entry')
    @login_required
    def purchase_sale_entry():
        """Purchase/Sale Entry page"""
        current_time = datetime.now().strftime('%H:%M:%S')
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
        """Print bill (purchase or sale)"""
        try:
            if bill_type.lower() == 'purchase':
                transactions = Purchase.query.filter_by(bill_no=bill_no).all()
                if not transactions:
                    flash('Purchase bill not found', 'error')
                    return redirect(url_for('purchases'))
                
                # Get party details
                party = Party.query.filter_by(party_cd=transactions[0].party_cd).first()
                
                # Prepare items data
                items = []
                sub_total = 0
                total_discount = 0
                
                for trans in transactions:
                    item = Item.query.filter_by(it_cd=trans.it_cd).first()
                    amount = trans.qty * trans.rate
                    net_amount = amount - trans.discount
                    
                    items.append({
                        'it_cd': trans.it_cd,
                        'it_nm': item.it_nm if item else trans.it_cd,
                        'qty': trans.qty,
                        'rate': trans.rate,
                        'amount': amount,
                        'discount': trans.discount,
                        'net_amount': net_amount
                    })
                    
                    sub_total += amount
                    total_discount += trans.discount
                
                gst_amount = sub_total * 0.18  # 18% GST
                grand_total = sub_total - total_discount + gst_amount
                
                return render_template('print_bill.html',
                                     bill_type='PURCHASE',
                                     bill_no=bill_no,
                                     bill_date=transactions[0].bill_date.strftime('%d/%m/%Y'),
                                     party_cd=transactions[0].party_cd,
                                     party_nm=party.party_nm if party else transactions[0].party_cd,
                                     party_address=f"{party.address1 or ''} {party.address2 or ''} {party.address3 or ''}".strip() if party else '',
                                     party_phone=party.phone or party.mobile or '',
                                     items=items,
                                     sub_total=sub_total,
                                     total_discount=total_discount,
                                     gst_amount=gst_amount,
                                     grand_total=grand_total,
                                     generated_date=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                
            elif bill_type.lower() == 'sale':
                transactions = Sale.query.filter_by(bill_no=bill_no).all()
                if not transactions:
                    flash('Sale bill not found', 'error')
                    return redirect(url_for('sales'))
                
                # Get party details
                party = Party.query.filter_by(party_cd=transactions[0].party_cd).first()
                
                # Prepare items data
                items = []
                sub_total = 0
                total_discount = 0
                
                for trans in transactions:
                    item = Item.query.filter_by(it_cd=trans.it_cd).first()
                    amount = trans.qty * trans.rate
                    net_amount = amount - trans.discount
                    
                    items.append({
                        'it_cd': trans.it_cd,
                        'it_nm': item.it_nm if item else trans.it_cd,
                        'qty': trans.qty,
                        'rate': trans.rate,
                        'amount': amount,
                        'discount': trans.discount,
                        'net_amount': net_amount
                    })
                    
                    sub_total += amount
                    total_discount += trans.discount
                
                gst_amount = sub_total * 0.18  # 18% GST
                grand_total = sub_total - total_discount + gst_amount
                
                return render_template('print_bill.html',
                                     bill_type='SALE',
                                     bill_no=bill_no,
                                     bill_date=transactions[0].bill_date.strftime('%d/%m/%Y'),
                                     party_cd=transactions[0].party_cd,
                                     party_nm=party.party_nm if party else transactions[0].party_cd,
                                     party_address=f"{party.address1 or ''} {party.address2 or ''} {party.address3 or ''}".strip() if party else '',
                                     party_phone=party.phone or party.mobile or '',
                                     items=items,
                                     sub_total=sub_total,
                                     total_discount=total_discount,
                                     gst_amount=gst_amount,
                                     grand_total=grand_total,
                                     generated_date=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            else:
                flash('Invalid bill type', 'error')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            logger.error(f"Print bill error: {e}")
            flash('Error generating bill', 'error')
            return redirect(url_for('dashboard'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

def init_db():
    """Initialize database with sample data"""
    with create_app().app_context():
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@business.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: admin/admin123")

if __name__ == '__main__':
    app = create_app()
    
    # Initialize database
    with app.app_context():
        db.create_all()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000) 