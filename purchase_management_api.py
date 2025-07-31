#!/usr/bin/env python3
"""
Advanced Purchase Management API Endpoints
Flask Blueprint for comprehensive purchase management functionality
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from purchase_management import PurchaseManagementSystem
from datetime import datetime, date
import json

purchase_management_api = Blueprint('purchase_management_api', __name__)
pms = PurchaseManagementSystem()

@purchase_management_api.route('/api/purchase/entry', methods=['POST'])
@login_required
def create_purchase_entry():
    """Create a new purchase entry"""
    try:
        data = request.get_json()
        result = pms.create_purchase_entry(
            user_id=current_user.id,
            party_id=data.get('party_id'),
            items=data.get('items', []),
            total_amount=data.get('total_amount', 0),
            tax_amount=data.get('tax_amount', 0),
            discount_amount=data.get('discount_amount', 0),
            transport_charges=data.get('transport_charges', 0),
            payment_terms=data.get('payment_terms', ''),
            delivery_date=data.get('delivery_date'),
            notes=data.get('notes', '')
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_management_api.route('/api/purchase/<int:bill_no>', methods=['GET'])
@login_required
def get_purchase_entry(bill_no):
    """Get purchase entry by bill number"""
    try:
        result = pms.get_purchase_entry(bill_no, current_user.id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@purchase_management_api.route('/api/purchase/summary', methods=['GET'])
@login_required
def get_purchase_summary():
    """Get purchase summary statistics"""
    try:
        result = pms.get_purchase_summary(current_user.id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_management_api.route('/api/purchase/order', methods=['POST'])
@login_required
def create_purchase_order():
    """Create a new purchase order"""
    try:
        data = request.get_json()
        result = pms.create_purchase_order(
            user_id=current_user.id,
            party_id=data.get('party_id'),
            items=data.get('items', []),
            total_amount=data.get('total_amount', 0),
            expected_delivery=data.get('expected_delivery'),
            terms_conditions=data.get('terms_conditions', ''),
            notes=data.get('notes', '')
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_management_api.route('/api/purchase/return', methods=['POST'])
@login_required
def create_purchase_return():
    """Create a purchase return"""
    try:
        data = request.get_json()
        result = pms.create_purchase_return(
            user_id=current_user.id,
            original_bill_no=data.get('original_bill_no'),
            items=data.get('items', []),
            return_reason=data.get('return_reason', ''),
            notes=data.get('notes', '')
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_management_api.route('/api/purchase/payment', methods=['POST'])
@login_required
def record_purchase_payment():
    """Record a purchase payment"""
    try:
        data = request.get_json()
        result = pms.record_purchase_payment(
            user_id=current_user.id,
            bill_no=data.get('bill_no'),
            payment_amount=data.get('payment_amount'),
            payment_method=data.get('payment_method', 'cash'),
            payment_date=data.get('payment_date'),
            reference_no=data.get('reference_no', ''),
            notes=data.get('notes', '')
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_management_api.route('/api/purchase/reports/<report_type>', methods=['GET'])
@login_required
def get_purchase_reports(report_type):
    """Get purchase reports by type"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        party_id = request.args.get('party_id')
        
        result = pms.get_purchase_reports(
            user_id=current_user.id,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            party_id=party_id
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_management_api.route('/api/purchase/list', methods=['GET'])
@login_required
def get_purchase_list():
    """Get list of purchases with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        party_id = request.args.get('party_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        result = pms.get_purchase_list(
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            search=search,
            party_id=party_id,
            start_date=start_date,
            end_date=end_date
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_management_api.route('/api/purchase/pending-payments', methods=['GET'])
@login_required
def get_pending_payments():
    """Get pending purchase payments"""
    try:
        result = pms.get_pending_payments(current_user.id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@purchase_management_api.route('/api/purchase/statistics', methods=['GET'])
@login_required
def get_purchase_statistics():
    """Get purchase statistics"""
    try:
        period = request.args.get('period', 'month')
        result = pms.get_purchase_statistics(current_user.id, period)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Error handlers
@purchase_management_api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@purchase_management_api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500 