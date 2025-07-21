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
from models import db, User, Company, Party, Item, Purchase, Sale, Cashbook, Bankbook
from auth import auth_bp
from api import api_bp
from forms import LoginForm, RegistrationForm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///business_web.db')
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
    
    # Main routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard with business overview"""
        try:
            # Get basic statistics
            total_parties = Party.query.count()
            total_items = Item.query.count()
            total_purchases = Purchase.query.count()
            total_sales = Sale.query.count()
            
            # Get recent transactions
            recent_purchases = Purchase.query.order_by(Purchase.created_date.desc()).limit(5).all()
            recent_sales = Sale.query.order_by(Sale.created_date.desc()).limit(5).all()
            
            return render_template('dashboard.html',
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
    
    @app.route('/parties')
    @login_required
    def parties():
        """Parties management page"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        query = Party.query
        if search:
            query = query.filter(Party.party_nm.contains(search) | Party.party_cd.contains(search))
        
        parties = query.paginate(page=page, per_page=20, error_out=False)
        return render_template('parties.html', parties=parties, search=search)
    
    @app.route('/items')
    @login_required
    def items():
        """Items management page"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        query = Item.query
        if search:
            query = query.filter(Item.it_nm.contains(search) | Item.it_cd.contains(search))
        
        items = query.paginate(page=page, per_page=20, error_out=False)
        return render_template('items.html', items=items, search=search)
    
    @app.route('/purchases')
    @login_required
    def purchases():
        """Purchases management page"""
        page = request.args.get('page', 1, type=int)
        purchases = Purchase.query.order_by(Purchase.bill_date.desc()).paginate(
            page=page, per_page=20, error_out=False)
        return render_template('purchases.html', purchases=purchases)
    
    @app.route('/sales')
    @login_required
    def sales():
        """Sales management page"""
        page = request.args.get('page', 1, type=int)
        sales = Sale.query.order_by(Sale.bill_date.desc()).paginate(
            page=page, per_page=20, error_out=False)
        return render_template('sales.html', sales=sales)
    
    @app.route('/cashbook')
    @login_required
    def cashbook():
        """Cashbook management page"""
        page = request.args.get('page', 1, type=int)
        cashbook_entries = Cashbook.query.order_by(Cashbook.date.desc()).paginate(
            page=page, per_page=20, error_out=False)
        return render_template('cashbook.html', cashbook_entries=cashbook_entries)
    
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