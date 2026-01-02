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
from config import config as config_options

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
    
    # Load config (development by default, override with FLASK_CONFIG)
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    config_class = config_options.get(config_name, config_options['default'])
    app.config.from_object(config_class)

    # Harden secrets: warn and set minimal defaults if not provided
    secret_key = app.config.get('SECRET_KEY')
    if not secret_key or secret_key == 'your-secret-key-change-in-production':
        logger.warning("SECRET_KEY not set. Set SECRET_KEY in the environment for production.")
        app.config['SECRET_KEY'] = secret_key or 'change-me'

    jwt_secret = os.environ.get('JWT_SECRET_KEY') or app.config.get('JWT_SECRET_KEY')
    if not jwt_secret or jwt_secret == 'jwt-secret-key-change-in-production':
        logger.warning("JWT_SECRET_KEY not set. Set JWT_SECRET_KEY in the environment for production.")
        jwt_secret = jwt_secret or 'change-me-jwt'
    app.config['JWT_SECRET_KEY'] = jwt_secret
    app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))
    
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
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(dashboard_api, url_prefix='')

    # Data/API blueprints are always registered so new management screens can load data
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(parties_api, url_prefix='')
    app.register_blueprint(items_api, url_prefix='')
    app.register_blueprint(sales_api, url_prefix='')
    app.register_blueprint(purchases_api, url_prefix='')
    app.register_blueprint(enhanced_api, url_prefix='/api/enhanced')

    # Optionally include legacy UI/demo routes (kept off by default)
    enable_legacy_routes = os.environ.get('ENABLE_LEGACY_ROUTES', 'false').lower() == 'true'
    app.config['ENABLE_LEGACY_ROUTES'] = enable_legacy_routes
    app.jinja_env.globals['enable_legacy_routes'] = enable_legacy_routes
    if enable_legacy_routes:
        app.register_blueprint(demo, url_prefix='')
        logger.info("Legacy UI routes enabled")
    else:
        logger.info("Legacy UI routes disabled (set ENABLE_LEGACY_ROUTES=true to enable)")
    
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
        # Send authenticated users straight to the modern dashboard
        if current_user.is_authenticated:
            return redirect(url_for('dashboard_enhanced'))
        return render_template('index.html')

    # ... (rest of your routes unchanged) ...

    return app


if __name__ == '__main__':
    app = create_app()

    initialize_db = os.environ.get('INITIALIZE_DB', 'false').lower() == 'true'
    if initialize_db:
        with app.app_context():
            db.create_all()
            print("Database initialized successfully.")

    # Render sets PORT and expects binding on 0.0.0.0.
    # Keep your existing FLASK_RUN_HOST/FLASK_RUN_PORT for local dev.
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('PORT') or os.environ.get('FLASK_RUN_PORT', '5000'))

    # If running on Render (PORT is set), force host to 0.0.0.0
    if os.environ.get('PORT'):
        host = '0.0.0.0'

    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(debug=debug, host=host, port=port)
