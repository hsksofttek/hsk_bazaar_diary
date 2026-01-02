#!/usr/bin/env python3
"""
Advanced Financial Management API Endpoints
Flask Blueprint for comprehensive financial management functionality
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from financial_management import FinancialManagementSystem
from models import Party, Ledger
from database import db
from datetime import datetime, date
import json

# Create Blueprint
financial_management_api = Blueprint('financial_management_api', __name__)

# Initialize Financial Management System
fms = FinancialManagementSystem()

@financial_management_api.route('/api/financial/accounts', methods=['POST'])
@login_required
def create_account():
    """Create a new chart of accounts entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['account_code', 'account_name', 'account_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create account
        result = fms.create_account(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/accounts', methods=['GET'])
@login_required
def get_accounts():
    """Get list of chart of accounts"""
    try:
        account_type = request.args.get('account_type')
        result = fms.get_accounts(current_user.id, account_type)
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/journal-entry', methods=['POST'])
@login_required
def create_journal_entry():
    """Create a journal entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('entry_date') or not data.get('details'):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Create journal entry
        result = fms.create_journal_entry(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/ledger', methods=['GET'])
@login_required
def get_ledger():
    """Get general ledger entries"""
    try:
        account_code = request.args.get('account_code')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        query = Ledger.query.filter(Ledger.user_id == current_user.id)

        if account_code:
            query = query.filter(Ledger.party_cd == account_code)
        if start_date:
            query = query.filter(Ledger.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Ledger.date <= datetime.strptime(end_date, '%Y-%m-%d').date())

        total = query.count()
        entries = query.order_by(Ledger.date.desc(), Ledger.id.desc()).offset(offset).limit(limit).all()

        ledger_entries = []
        for entry in entries:
            ledger_entries.append({
                'entry_date': entry.date.strftime('%Y-%m-%d'),
                'voucher_no': entry.voucher_no,
                'voucher_type': entry.voucher_type,
                'account_code': entry.party_cd,
                'debit_amount': float(entry.dr_amt or 0),
                'credit_amount': float(entry.cr_amt or 0),
                'balance': float(entry.balance or 0),
                'narration': entry.narration,
                'reference_no': entry.reference_no
            })

        return jsonify({
            'success': True,
            'ledger_entries': ledger_entries,
            'count': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/trial-balance', methods=['GET'])
@login_required
def get_trial_balance():
    """Get trial balance"""
    try:
        as_of_date = request.args.get('as_of_date')
        
        result = fms.get_trial_balance(current_user.id, as_of_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/balance-sheet', methods=['GET'])
@login_required
def get_balance_sheet():
    """Get balance sheet"""
    try:
        as_of_date = request.args.get('as_of_date')
        
        result = fms.get_balance_sheet(current_user.id, as_of_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/profit-loss', methods=['GET'])
@login_required
def get_profit_loss():
    """Get profit and loss statement"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'error': 'Start date and end date are required'}), 400
        
        result = fms.get_profit_loss(current_user.id, start_date, end_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/statistics', methods=['GET'])
@login_required
def get_financial_statistics():
    """Get financial statistics for dashboard"""
    try:
        def sum_by_type(code: str) -> float:
            return db.session.query(func.sum(Party.current_balance)).filter(
                Party.user_id == current_user.id,
                Party.ledgtyp == code
            ).scalar() or 0

        total_assets = sum_by_type('ASSET')
        total_liabilities = sum_by_type('LIABILITY')
        total_equity = sum_by_type('EQUITY')
        total_revenue = sum_by_type('REVENUE')
        total_expenses = sum_by_type('EXPENSE')

        recent = Ledger.query.filter_by(user_id=current_user.id).order_by(
            Ledger.date.desc(), Ledger.id.desc()
        ).limit(5).all()

        recent_entries = [{
            'entry_no': entry.id,
            'entry_date': entry.date.strftime('%Y-%m-%d'),
            'narration': entry.narration,
            'amount': float(entry.dr_amt or 0) - float(entry.cr_amt or 0)
        } for entry in recent]

        net_profit = total_revenue - total_expenses

        statistics = {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'recent_entries': recent_entries
        }

        return jsonify({
            'success': True,
            'statistics': statistics
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financial_management_api.route('/api/financial/account-types', methods=['GET'])
@login_required
def get_account_types():
    """Get available account types"""
    try:
        account_types = [
            {'code': 'ASSET', 'name': 'Asset', 'description': 'Resources owned by the business'},
            {'code': 'LIABILITY', 'name': 'Liability', 'description': 'Obligations to others'},
            {'code': 'EQUITY', 'name': 'Equity', 'description': 'Owner\'s investment and retained earnings'},
            {'code': 'REVENUE', 'name': 'Revenue', 'description': 'Income from business activities'},
            {'code': 'EXPENSE', 'name': 'Expense', 'description': 'Costs incurred in business operations'}
        ]
        
        return jsonify({
            'success': True,
            'account_types': account_types
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@financial_management_api.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Financial Management API endpoint not found'}), 404

@financial_management_api.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500 