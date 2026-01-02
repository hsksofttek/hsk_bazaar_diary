#!/usr/bin/env python3
"""
Packing Management API
Flask API endpoints for Packing Management System
"""

from flask import Blueprint, request, jsonify, render_template
from packing_management import PackingManagementSystem
from database import db
from models import User
from flask_login import login_required, current_user
import json
from datetime import datetime, timedelta

# Create Blueprint
packing_management_bp = Blueprint('packing_management', __name__)

# Initialize Packing Management System
packing_system = PackingManagementSystem()

@packing_management_bp.route('/packing-management')
@login_required
def packing_management():
    """Packing Management Dashboard"""
    return render_template('packing_management.html')

@packing_management_bp.route('/api/packing/entry', methods=['POST'])
@login_required
def create_packing_entry():
    """Create new packing entry"""
    try:
        data = request.get_json()
        
        # Validate data
        is_valid, message = packing_system.validate_packing_data(data)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Create entry
        success, message = packing_system.create_packing_entry(data)
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/entry/<int:packing_id>', methods=['PUT'])
@login_required
def update_packing_entry(packing_id):
    """Update packing entry"""
    try:
        data = request.get_json()
        
        success, message = packing_system.update_packing_entry(packing_id, data)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/entry/<int:packing_id>', methods=['DELETE'])
@login_required
def delete_packing_entry(packing_id):
    """Delete packing entry"""
    try:
        success, message = packing_system.delete_packing_entry(packing_id)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/entries', methods=['GET'])
@login_required
def get_packing_entries():
    """Get packing entries with filters"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('bill_no'):
            filters['bill_no'] = int(request.args.get('bill_no'))
        if request.args.get('it_cd'):
            filters['it_cd'] = request.args.get('it_cd')
        if request.args.get('cat_cd'):
            filters['cat_cd'] = request.args.get('cat_cd')
        if request.args.get('date_from'):
            filters['date_from'] = request.args.get('date_from')
        if request.args.get('date_to'):
            filters['date_to'] = request.args.get('date_to')
        
        entries = packing_system.get_packing_entries(filters)
        return jsonify({'success': True, 'data': entries}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/entry/<int:packing_id>', methods=['GET'])
@login_required
def get_packing_entry(packing_id):
    """Get packing entry by ID"""
    try:
        entry = packing_system.get_packing_by_id(packing_id)
        if entry:
            return jsonify({'success': True, 'data': entry}), 200
        else:
            return jsonify({'success': False, 'message': 'Packing entry not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/bill/<int:bill_no>', methods=['GET'])
@login_required
def get_packing_by_bill(bill_no):
    """Get packing entries by bill number"""
    try:
        entries = packing_system.get_packing_by_bill(bill_no)
        return jsonify({'success': True, 'data': entries}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/item/<it_cd>', methods=['GET'])
@login_required
def get_packing_by_item(it_cd):
    """Get packing entries by item code"""
    try:
        entries = packing_system.get_packing_by_item(it_cd)
        return jsonify({'success': True, 'data': entries}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/calculate-charges', methods=['POST'])
@login_required
def calculate_packing_charges():
    """Calculate packing charges"""
    try:
        data = request.get_json()
        charges = packing_system.calculate_packing_charges(data)
        return jsonify({'success': True, 'data': charges}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/statistics', methods=['GET'])
@login_required
def get_packing_statistics():
    """Get packing statistics"""
    try:
        stats = packing_system.get_packing_statistics()
        return jsonify({'success': True, 'data': stats}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/reports/<report_type>', methods=['GET'])
@login_required
def get_packing_reports(report_type):
    """Get packing reports"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('bill_no'):
            filters['bill_no'] = int(request.args.get('bill_no'))
        if request.args.get('it_cd'):
            filters['it_cd'] = request.args.get('it_cd')
        if request.args.get('cat_cd'):
            filters['cat_cd'] = request.args.get('cat_cd')
        if request.args.get('date_from'):
            filters['date_from'] = request.args.get('date_from')
        if request.args.get('date_to'):
            filters['date_to'] = request.args.get('date_to')
        
        reports = packing_system.get_packing_reports(report_type, filters)
        return jsonify({'success': True, 'data': reports}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/types', methods=['GET'])
@login_required
def get_packing_types():
    """Get available packing types"""
    try:
        types = packing_system.get_packing_types()
        return jsonify({'success': True, 'data': types}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/categories', methods=['GET'])
@login_required
def get_packing_categories():
    """Get available packing categories"""
    try:
        categories = packing_system.get_packing_categories()
        return jsonify({'success': True, 'data': categories}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# UI Routes
@packing_management_bp.route('/packing-entries')
@login_required
def packing_entries():
    """Packing Entries Page"""
    return render_template('packing_entries.html')

@packing_management_bp.route('/packing-reports')
@login_required
def packing_reports():
    """Packing Reports Page"""
    return render_template('packing_reports.html')

@packing_management_bp.route('/packing-settings')
@login_required
def packing_settings():
    """Packing Settings Page"""
    return render_template('packing_settings.html')

# Utility Routes
@packing_management_bp.route('/api/packing/validate-item/<it_cd>', methods=['GET'])
@login_required
def validate_item(it_cd):
    """Validate item code"""
    try:
        from models import Items
        item = Items.query.filter_by(it_cd=it_cd).first()
        if item:
            return jsonify({'success': True, 'data': {'it_cd': item.it_cd, 'it_nm': item.it_nm}}), 200
        else:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/validate-bill/<int:bill_no>', methods=['GET'])
@login_required
def validate_bill(bill_no):
    """Validate bill number"""
    try:
        from models import Purchase, Sale
        purchase = Purchase.query.filter_by(bill_no=bill_no).first()
        sale = Sale.query.filter_by(bill_no=bill_no).first()
        
        if purchase:
            return jsonify({'success': True, 'data': {'bill_no': bill_no, 'type': 'purchase'}}), 200
        elif sale:
            return jsonify({'success': True, 'data': {'bill_no': bill_no, 'type': 'sale'}}), 200
        else:
            return jsonify({'success': False, 'message': 'Bill not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Bulk Operations
@packing_management_bp.route('/api/packing/bulk-import', methods=['POST'])
@login_required
def bulk_import_packing():
    """Bulk import packing entries"""
    try:
        data = request.get_json()
        entries = data.get('entries', [])
        
        results = []
        success_count = 0
        error_count = 0
        
        for entry in entries:
            is_valid, message = packing_system.validate_packing_data(entry)
            if is_valid:
                success, msg = packing_system.create_packing_entry(entry)
                if success:
                    success_count += 1
                    results.append({'entry': entry, 'status': 'success', 'message': msg})
                else:
                    error_count += 1
                    results.append({'entry': entry, 'status': 'error', 'message': msg})
            else:
                error_count += 1
                results.append({'entry': entry, 'status': 'error', 'message': message})
        
        return jsonify({
            'success': True,
            'data': {
                'total': len(entries),
                'success_count': success_count,
                'error_count': error_count,
                'results': results
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@packing_management_bp.route('/api/packing/export', methods=['GET'])
@login_required
def export_packing_data():
    """Export packing data"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('bill_no'):
            filters['bill_no'] = int(request.args.get('bill_no'))
        if request.args.get('it_cd'):
            filters['it_cd'] = request.args.get('it_cd')
        if request.args.get('cat_cd'):
            filters['cat_cd'] = request.args.get('cat_cd')
        if request.args.get('date_from'):
            filters['date_from'] = request.args.get('date_from')
        if request.args.get('date_to'):
            filters['date_to'] = request.args.get('date_to')
        
        entries = packing_system.get_packing_entries(filters)
        
        # Format for export
        export_data = []
        for entry in entries:
            export_data.append({
                'Bill No': entry.get('bill_no'),
                'Item Code': entry.get('it_cd'),
                'Packing Description': entry.get('packing_desc'),
                'Quantity': entry.get('qty'),
                'MRP': entry.get('mrp'),
                'Sale Price': entry.get('sprc'),
                'Package': entry.get('pkt'),
                'Category': entry.get('cat_cd'),
                'Max Rate': entry.get('maxrt'),
                'Min Rate': entry.get('minrt'),
                'Tax %': entry.get('taxpr'),
                'Hamali Rate': entry.get('hamrt'),
                'Item Weight': entry.get('itwt'),
                'CESS': entry.get('ccess'),
                'Created Date': entry.get('created_date')
            })
        
        return jsonify({'success': True, 'data': export_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Dashboard Data
@packing_management_bp.route('/api/packing/dashboard-data', methods=['GET'])
@login_required
def get_packing_dashboard_data():
    """Get dashboard data for packing management"""
    try:
        # Get statistics
        stats = packing_system.get_packing_statistics()
        
        # Get recent entries
        recent_entries = packing_system.get_packing_entries()
        recent_entries = recent_entries[:10]  # Limit to 10 recent entries
        
        # Get top items
        top_items = stats.get('top_items', [])[:5]
        
        # Get top categories
        top_categories = stats.get('top_categories', [])[:5]
        
        return jsonify({
            'success': True,
            'data': {
                'statistics': stats,
                'recent_entries': recent_entries,
                'top_items': top_items,
                'top_categories': top_categories
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500 