#!/usr/bin/env python3
"""
Bank Management API
Flask API endpoints for Bank Management System
"""

from flask import Blueprint, request, jsonify, render_template
from bank_management import BankManagementSystem
from database import db
from models import User
from flask_login import login_required, current_user
import json
from datetime import datetime, timedelta

# Create Blueprint
bank_management_bp = Blueprint('bank_management', __name__)

# Initialize Bank Management System
bank_system = BankManagementSystem()

@bank_management_bp.route('/bank-management')
@login_required
def bank_management():
    """Bank Management Dashboard"""
    return render_template('bank_management.html')

# Template-compatible endpoints (plural form)
@bank_management_bp.route('/api/bank-accounts', methods=['GET'])
@login_required
def get_bank_accounts_plural():
    """Get bank accounts (for template compatibility)"""
    try:
        # Mock data for now - replace with actual database queries
        mock_accounts = [
            {
                'id': 1,
                'account_name': 'Main Business Account',
                'bank_name': 'HDFC Bank',
                'account_number': '1234567890',
                'account_type': 'CURRENT',
                'balance': 50000.00,
                'status': 'ACTIVE',
                'created_date': '2024-01-15T09:00:00'
            },
            {
                'id': 2,
                'account_name': 'Savings Account',
                'bank_name': 'SBI Bank',
                'account_number': '0987654321',
                'account_type': 'SAVINGS',
                'balance': 25000.00,
                'status': 'ACTIVE',
                'created_date': '2024-01-15T09:00:00'
            }
        ]
        
        return jsonify({
            'success': True, 
            'accounts': mock_accounts
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-transactions', methods=['GET'])
@login_required
def get_bank_transactions_plural():
    """Get bank transactions (for template compatibility)"""
    try:
        # Mock data for now - replace with actual database queries
        mock_transactions = [
            {
                'id': 1,
                'transaction_date': '2025-01-30',
                'account_name': 'Main Business Account',
                'transaction_type': 'CREDIT',
                'amount': 10000.00,
                'description': 'Payment received',
                'reference_number': 'TXN001',
                'created_date': '2025-01-30T10:00:00'
            },
            {
                'id': 2,
                'transaction_date': '2025-01-29',
                'account_name': 'Main Business Account',
                'transaction_type': 'DEBIT',
                'amount': 5000.00,
                'description': 'Payment made',
                'reference_number': 'TXN002',
                'created_date': '2025-01-29T14:00:00'
            }
        ]
        
        return jsonify({
            'success': True, 
            'transactions': mock_transactions
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-accounts/<int:account_id>', methods=['GET'])
@login_required
def get_bank_account_by_id_plural(account_id):
    """Get bank account by ID (for template compatibility)"""
    try:
        # Mock data for now
        mock_account = {
            'id': account_id,
            'account_name': 'Main Business Account',
            'bank_name': 'HDFC Bank',
            'account_number': '1234567890',
            'ifsc_code': 'HDFC0001234',
            'account_type': 'CURRENT',
            'opening_balance': 10000.00,
            'current_balance': 50000.00,
            'branch_name': 'Main Branch',
            'status': 'ACTIVE',
            'description': 'Primary business account',
            'created_date': '2024-01-15T09:00:00'
        }
        
        return jsonify({'success': True, 'account': mock_account}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-accounts/<int:account_id>', methods=['PUT'])
@login_required
def update_bank_account_plural(account_id):
    """Update bank account (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock update - replace with actual database update
        return jsonify({'success': True, 'message': 'Bank account updated successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-accounts/<int:account_id>', methods=['DELETE'])
@login_required
def delete_bank_account_plural(account_id):
    """Delete bank account (for template compatibility)"""
    try:
        # Mock delete - replace with actual database delete
        return jsonify({'success': True, 'message': 'Bank account deleted successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-accounts', methods=['POST'])
@login_required
def create_bank_account_plural():
    """Create new bank account (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock create - replace with actual database create
        return jsonify({'success': True, 'message': 'Bank account created successfully'}), 201
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-transactions', methods=['POST'])
@login_required
def create_bank_transaction_plural():
    """Create new bank transaction (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock create - replace with actual database create
        return jsonify({'success': True, 'message': 'Bank transaction created successfully'}), 201
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Original endpoints (singular form)
@bank_management_bp.route('/api/bank-account', methods=['POST'])
@login_required
def create_bank_account():
    """Create new bank account"""
    try:
        data = request.get_json()
        
        # Validate data
        is_valid, message = bank_system.validate_account_data(data)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Create account
        success, message = bank_system.create_account(data)
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-account/<int:account_id>', methods=['PUT'])
@login_required
def update_bank_account(account_id):
    """Update bank account"""
    try:
        data = request.get_json()
        
        success, message = bank_system.update_account(account_id, data)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-account/<int:account_id>', methods=['DELETE'])
@login_required
def delete_bank_account(account_id):
    """Delete bank account"""
    try:
        success, message = bank_system.delete_account(account_id)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-account', methods=['GET'])
@login_required
def get_bank_accounts():
    """Get bank accounts with filters"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('account_type'):
            filters['account_type'] = request.args.get('account_type')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('bank_name'):
            filters['bank_name'] = request.args.get('bank_name')
        
        accounts = bank_system.get_accounts(filters)
        return jsonify({'success': True, 'data': accounts}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-account/<int:account_id>', methods=['GET'])
@login_required
def get_bank_account(account_id):
    """Get bank account by ID"""
    try:
        account = bank_system.get_account_by_id(account_id)
        if account:
            return jsonify({'success': True, 'account': account}), 200
        else:
            return jsonify({'success': False, 'message': 'Bank account not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-transaction', methods=['POST'])
@login_required
def create_bank_transaction():
    """Create new bank transaction"""
    try:
        data = request.get_json()
        
        # Validate data
        is_valid, message = bank_system.validate_transaction_data(data)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Create transaction
        success, message = bank_system.create_transaction(data)
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-transaction/<int:transaction_id>', methods=['PUT'])
@login_required
def update_bank_transaction(transaction_id):
    """Update bank transaction"""
    try:
        data = request.get_json()
        
        success, message = bank_system.update_transaction(transaction_id, data)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-transaction/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_bank_transaction(transaction_id):
    """Delete bank transaction"""
    try:
        success, message = bank_system.delete_transaction(transaction_id)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-transaction', methods=['GET'])
@login_required
def get_bank_transactions():
    """Get bank transactions with filters"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('account_id'):
            filters['account_id'] = request.args.get('account_id')
        if request.args.get('transaction_type'):
            filters['transaction_type'] = request.args.get('transaction_type')
        if request.args.get('date_from'):
            filters['date_from'] = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d').date()
        if request.args.get('date_to'):
            filters['date_to'] = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d').date()
        
        transactions = bank_system.get_transactions(filters)
        return jsonify({'success': True, 'data': transactions}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-transaction/<int:transaction_id>', methods=['GET'])
@login_required
def get_bank_transaction(transaction_id):
    """Get bank transaction by ID"""
    try:
        transaction = bank_system.get_transaction_by_id(transaction_id)
        if transaction:
            return jsonify({'success': True, 'transaction': transaction}), 200
        else:
            return jsonify({'success': False, 'message': 'Bank transaction not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-reconciliation/<int:account_id>', methods=['POST'])
@login_required
def reconcile_account(account_id):
    """Reconcile bank account"""
    try:
        data = request.get_json()
        
        success, message = bank_system.reconcile_account(account_id, data)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-statistics', methods=['GET'])
@login_required
def get_bank_statistics():
    """Get bank statistics"""
    try:
        stats = bank_system.get_statistics()
        return jsonify({'success': True, 'statistics': stats}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-reports/<report_type>', methods=['GET'])
@login_required
def get_bank_reports(report_type):
    """Get bank reports"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        report_data = bank_system.generate_report(report_type, date_from, date_to)
        return jsonify({'success': True, 'report': report_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@bank_management_bp.route('/api/bank-export', methods=['GET'])
@login_required
def export_bank_data():
    """Export bank data"""
    try:
        export_type = request.args.get('type', 'csv')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        export_data = bank_system.export_data(export_type, date_from, date_to)
        
        if export_type == 'csv':
            from flask import send_file
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Date', 'Account', 'Type', 'Amount', 'Description', 'Reference'])
            
            # Write data
            for row in export_data:
                writer.writerow(row)
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'bank_data_{datetime.now().strftime("%Y%m%d")}.csv'
            )
        else:
            return jsonify({'success': True, 'data': export_data}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500 