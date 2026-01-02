#!/usr/bin/env python3
"""
Crate Management API
Flask API endpoints for Crate Management System
"""

from flask import Blueprint, request, jsonify, render_template
from crate_management import CrateManagementSystem
from database import db
from models import User
from flask_login import login_required, current_user
import json
from datetime import datetime, timedelta

# Create Blueprint
crate_management_bp = Blueprint('crate_management', __name__)

# Initialize Crate Management System
crate_system = CrateManagementSystem()

# ==================== CRATE MANAGEMENT ROUTES ====================

@crate_management_bp.route('/crate-management')
@login_required
def crate_management_dashboard():
    """Crate Management Dashboard"""
    try:
        # Get statistics
        stats = crate_system.get_crate_statistics(current_user.id)
        
        # Get all party balances
        all_balances = crate_system.get_all_party_crate_balances(current_user.id)
        
        # Get outstanding crates
        outstanding = crate_system.get_outstanding_crates_report(current_user.id)
        
        return render_template('crate_management.html',
                             stats=stats.get('statistics', {}),
                             all_balances=all_balances.get('all_balances', []),
                             outstanding=outstanding.get('outstanding_report', {}))
    except Exception as e:
        return render_template('crate_management.html', error=str(e))

# ==================== CRATE TRANSACTION API ENDPOINTS ====================

@crate_management_bp.route('/api/crate/transaction', methods=['POST'])
@login_required
def create_crate_transaction():
    """Create new crate transaction"""
    try:
        data = request.get_json()
        
        result = crate_system.create_crate_transaction(
            user_id=current_user.id,
            party_id=data.get('party_id'),
            transaction_type=data.get('transaction_type'),
            quantity=int(data.get('quantity', 0)),
            crate_type=data.get('crate_type'),
            item_code=data.get('item_code'),
            bill_no=data.get('bill_no'),
            bill_date=data.get('bill_date'),
            remarks=data.get('remarks', ''),
            rental_rate=float(data.get('rental_rate', 0)) if data.get('rental_rate') else None
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crate_management_bp.route('/api/crate/transactions', methods=['GET'])
@login_required
def get_crate_transactions():
    """Get crate transactions with filtering"""
    try:
        party_id = request.args.get('party_id')
        crate_type = request.args.get('crate_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        transaction_type = request.args.get('transaction_type')
        
        result = crate_system.get_crate_transactions(
            user_id=current_user.id,
            party_id=party_id,
            crate_type=crate_type,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== CRATE BALANCE API ENDPOINTS ====================

@crate_management_bp.route('/api/crate/balance/<party_id>', methods=['GET'])
@login_required
def get_party_crate_balance(party_id):
    """Get crate balance for specific party"""
    try:
        crate_type = request.args.get('crate_type')
        
        result = crate_system.get_party_crate_balance(
            user_id=current_user.id,
            party_id=party_id,
            crate_type=crate_type
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crate_management_bp.route('/api/crate/balances', methods=['GET'])
@login_required
def get_all_crate_balances():
    """Get crate balances for all parties"""
    try:
        result = crate_system.get_all_party_crate_balances(current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crate_management_bp.route('/api/crate/reconcile', methods=['POST'])
@login_required
def reconcile_crate_balances():
    """Reconcile crate balances"""
    try:
        data = request.get_json()
        party_id = data.get('party_id') if data else None
        
        result = crate_system.reconcile_crate_balances(
            user_id=current_user.id,
            party_id=party_id
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== CRATE RENTAL & CHARGES API ENDPOINTS ====================

@crate_management_bp.route('/api/crate/rental/calculate', methods=['POST'])
@login_required
def calculate_rental_charges():
    """Calculate crate rental charges"""
    try:
        data = request.get_json()
        
        result = crate_system.calculate_crate_rental_charges(
            party_id=data.get('party_id'),
            crate_type=data.get('crate_type'),
            days=int(data.get('days', 0)),
            quantity=int(data.get('quantity', 0)) if data.get('quantity') else None
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crate_management_bp.route('/api/crate/freight/calculate', methods=['POST'])
@login_required
def calculate_freight_charges():
    """Calculate freight charges for crates"""
    try:
        data = request.get_json()
        
        result = crate_system.calculate_freight_charges(
            crate_type=data.get('crate_type'),
            quantity=int(data.get('quantity', 0)),
            distance_km=float(data.get('distance_km', 0)),
            rate_per_km=float(data.get('rate_per_km', 1.5))
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== CRATE REPORTS API ENDPOINTS ====================

@crate_management_bp.route('/api/crate/reports/summary', methods=['GET'])
@login_required
def get_crate_summary_report():
    """Get crate summary report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        result = crate_system.get_crate_summary_report(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crate_management_bp.route('/api/crate/reports/movement', methods=['GET'])
@login_required
def get_crate_movement_report():
    """Get crate movement report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        party_id = request.args.get('party_id')
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'error': 'Start date and end date are required'})
        
        result = crate_system.get_crate_movement_report(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            party_id=party_id
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crate_management_bp.route('/api/crate/reports/outstanding', methods=['GET'])
@login_required
def get_outstanding_crates_report():
    """Get outstanding crates report"""
    try:
        result = crate_system.get_outstanding_crates_report(current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== CRATE TYPE MANAGEMENT API ENDPOINTS ====================

@crate_management_bp.route('/api/crate/types', methods=['GET'])
@login_required
def get_crate_types():
    """Get available crate types"""
    try:
        result = crate_system.get_crate_types()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crate_management_bp.route('/api/crate/types', methods=['POST'])
@login_required
def add_crate_type():
    """Add new crate type"""
    try:
        data = request.get_json()
        
        result = crate_system.add_crate_type(
            crate_code=data.get('crate_code'),
            crate_name=data.get('crate_name'),
            capacity=float(data.get('capacity', 0)),
            base_rate=float(data.get('base_rate', 0))
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crate_management_bp.route('/api/crate/types/<crate_code>', methods=['PUT'])
@login_required
def update_crate_type(crate_code):
    """Update crate type"""
    try:
        data = request.get_json()
        
        result = crate_system.update_crate_type(
            crate_code=crate_code,
            updates=data
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== CRATE STATISTICS API ENDPOINTS ====================

@crate_management_bp.route('/api/crate/statistics', methods=['GET'])
@login_required
def get_crate_statistics():
    """Get crate management statistics"""
    try:
        result = crate_system.get_crate_statistics(current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== CRATE MANAGEMENT PAGES ====================

@crate_management_bp.route('/crate-transactions')
@login_required
def crate_transactions_page():
    """Crate Transactions Page"""
    return render_template('crate_transactions.html')

@crate_management_bp.route('/crate-balances')
@login_required
def crate_balances_page():
    """Crate Balances Page"""
    return render_template('crate_balances.html')

@crate_management_bp.route('/crate-reports')
@login_required
def crate_reports_page():
    """Crate Reports Page"""
    return render_template('crate_reports.html')

@crate_management_bp.route('/crate-settings')
@login_required
def crate_settings_page():
    """Crate Settings Page"""
    return render_template('crate_settings.html')

# ==================== CRATE MANAGEMENT UTILITY ENDPOINTS ====================

@crate_management_bp.route('/api/crate/validate-party/<party_id>', methods=['GET'])
@login_required
def validate_party(party_id):
    """Validate if party exists"""
    try:
        from models import Party
        party = Party.query.filter_by(party_cd=party_id, user_id=current_user.id).first()
        
        if party:
            return jsonify({
                'success': True,
                'party': {
                    'party_code': party.party_cd,
                    'party_name': party.party_nm,
                    'address': f"{party.address1 or ''} {party.address2 or ''}".strip(),
                    'phone': party.phone
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Party not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crate_management_bp.route('/api/crate/validate-crate-type/<crate_type>', methods=['GET'])
@login_required
def validate_crate_type(crate_type):
    """Validate if crate type exists"""
    try:
        crate_types = crate_system.get_crate_types()
        
        if crate_type in crate_types.get('crate_types', {}):
            return jsonify({
                'success': True,
                'crate_type': crate_types['crate_types'][crate_type]
            })
        else:
            return jsonify({'success': False, 'error': 'Crate type not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== CRATE MANAGEMENT BULK OPERATIONS ====================

@crate_management_bp.route('/api/crate/bulk-transaction', methods=['POST'])
@login_required
def bulk_crate_transaction():
    """Create multiple crate transactions"""
    try:
        data = request.get_json()
        transactions = data.get('transactions', [])
        
        results = []
        success_count = 0
        error_count = 0
        
        for transaction in transactions:
            result = crate_system.create_crate_transaction(
                user_id=current_user.id,
                party_id=transaction.get('party_id'),
                transaction_type=transaction.get('transaction_type'),
                quantity=int(transaction.get('quantity', 0)),
                crate_type=transaction.get('crate_type'),
                item_code=transaction.get('item_code'),
                bill_no=transaction.get('bill_no'),
                bill_date=transaction.get('bill_date'),
                remarks=transaction.get('remarks', ''),
                rental_rate=float(transaction.get('rental_rate', 0)) if transaction.get('rental_rate') else None
            )
            
            results.append(result)
            if result['success']:
                success_count += 1
            else:
                error_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Bulk operation completed: {success_count} successful, {error_count} failed',
            'results': results,
            'success_count': success_count,
            'error_count': error_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crate_management_bp.route('/api/crate/export-balances', methods=['GET'])
@login_required
def export_crate_balances():
    """Export crate balances to CSV/Excel"""
    try:
        # Get all balances
        result = crate_system.get_all_party_crate_balances(current_user.id)
        
        if not result['success']:
            return jsonify(result)
        
        # Format data for export
        export_data = []
        for party_balance in result['all_balances']:
            party_code = party_balance['party_code']
            party_name = party_balance['party_name']
            
            for crate_type, balance_info in party_balance['crate_balances'].items():
                export_data.append({
                    'party_code': party_code,
                    'party_name': party_name,
                    'crate_type': crate_type,
                    'crate_name': balance_info['crate_name'],
                    'balance': balance_info['balance'],
                    'total_received': balance_info['total_received'],
                    'total_given': balance_info['total_given'],
                    'total_returned': balance_info['total_returned']
                })
        
        return jsonify({
            'success': True,
            'export_data': export_data,
            'filename': f'crate_balances_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== CRATE MANAGEMENT DASHBOARD DATA ====================

@crate_management_bp.route('/api/crate/dashboard-data', methods=['GET'])
@login_required
def get_crate_dashboard_data():
    """Get data for crate management dashboard"""
    try:
        # Get statistics
        stats = crate_system.get_crate_statistics(current_user.id)
        
        # Get outstanding crates
        outstanding = crate_system.get_outstanding_crates_report(current_user.id)
        
        # Get recent transactions (last 10)
        recent_transactions = crate_system.get_crate_transactions(
            user_id=current_user.id,
            start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        )
        
        return jsonify({
            'success': True,
            'dashboard_data': {
                'statistics': stats.get('statistics', {}),
                'outstanding': outstanding.get('outstanding_report', {}),
                'recent_transactions': recent_transactions.get('transactions', [])[:10]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}) 