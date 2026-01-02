"""
User Management System for Multi-User Business Management Application
Handles user registration, authentication, and data isolation
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Company, Party, Item, Purchase, Sale, Cashbook, Bankbook
from datetime import datetime
import re

user_bp = Blueprint('user', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        company_name = request.form.get('company_name')
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        
        if not email or not validate_email(email):
            errors.append("Please enter a valid email address")
        
        if not password:
            errors.append("Password is required")
        else:
            is_valid, message = validate_password(password)
            if not is_valid:
                errors.append(message)
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if not company_name:
            errors.append("Company name is required")
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            errors.append("Username already exists")
        
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create new user
        try:
            user = User(
                username=username,
                email=email,
                role='user'
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create company for the user
            company = Company(
                user_id=user.id,
                name=company_name,
                created_date=datetime.utcnow()
            )
            db.session.add(company)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@user_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)

@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        errors = []
        
        # Validate email
        if email and not validate_email(email):
            errors.append("Please enter a valid email address")
        
        # Check if email is already taken by another user
        if email and email != current_user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != current_user.id:
                errors.append("Email already registered by another user")
        
        # Password change validation
        if new_password:
            if not current_password:
                errors.append("Current password is required to change password")
            elif not current_user.check_password(current_password):
                errors.append("Current password is incorrect")
            else:
                is_valid, message = validate_password(new_password)
                if not is_valid:
                    errors.append(message)
                elif new_password != confirm_password:
                    errors.append("New passwords do not match")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('edit_profile.html', user=current_user)
        
        # Update user
        try:
            if email:
                current_user.email = email
            
            if new_password:
                current_user.set_password(new_password)
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Profile update failed. Please try again.', 'error')
            return render_template('edit_profile.html', user=current_user)
    
    return render_template('edit_profile.html', user=current_user)

@user_bp.route('/dashboard')
@login_required
def user_dashboard():
    """User-specific dashboard with their data"""
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
        
        return render_template('user_dashboard.html',
                             user=current_user,
                             company=company,
                             total_parties=total_parties,
                             total_items=total_items,
                             total_purchases=total_purchases,
                             total_sales=total_sales,
                             recent_purchases=recent_purchases,
                             recent_sales=recent_sales)
    except Exception as e:
        flash('Error loading dashboard data', 'error')
        return render_template('user_dashboard.html', user=current_user)

@user_bp.route('/company/setup', methods=['GET', 'POST'])
@login_required
def company_setup():
    """Company setup page for new users"""
    company = Company.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        name = request.form.get('name')
        address1 = request.form.get('address1')
        address2 = request.form.get('address2')
        city = request.form.get('city')
        phone = request.form.get('phone')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        
        if not name:
            flash('Company name is required', 'error')
            return render_template('company_setup.html', company=company)
        
        try:
            if company:
                # Update existing company
                company.name = name
                company.address1 = address1
                company.address2 = address2
                company.city = city
                company.phone = phone
                company.from_date = datetime.strptime(from_date, '%Y-%m-%d').date() if from_date else None
                company.to_date = datetime.strptime(to_date, '%Y-%m-%d').date() if to_date else None
                company.modified_date = datetime.utcnow()
            else:
                # Create new company
                company = Company(
                    user_id=current_user.id,
                    name=name,
                    address1=address1,
                    address2=address2,
                    city=city,
                    phone=phone,
                    from_date=datetime.strptime(from_date, '%Y-%m-%d').date() if from_date else None,
                    to_date=datetime.strptime(to_date, '%Y-%m-%d').date() if to_date else None
                )
                db.session.add(company)
            
            db.session.commit()
            flash('Company information saved successfully!', 'success')
            return redirect(url_for('user.user_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to save company information. Please try again.', 'error')
            return render_template('company_setup.html', company=company)
    
    return render_template('company_setup.html', company=company)

# Helper functions for data isolation
def get_user_parties(user_id):
    """Get parties for specific user"""
    return Party.query.filter_by(user_id=user_id).all()

def get_user_items(user_id):
    """Get items for specific user"""
    return Item.query.filter_by(user_id=user_id).all()

def get_user_purchases(user_id):
    """Get purchases for specific user"""
    return Purchase.query.filter_by(user_id=user_id).all()

def get_user_sales(user_id):
    """Get sales for specific user"""
    return Sale.query.filter_by(user_id=user_id).all()

def get_user_cashbook(user_id):
    """Get cashbook entries for specific user"""
    return Cashbook.query.filter_by(user_id=user_id).all()

def get_user_bankbook(user_id):
    """Get bankbook entries for specific user"""
    return Bankbook.query.filter_by(user_id=user_id).all() 
 
 
 