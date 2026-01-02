#!/usr/bin/env python3
"""
Advanced Inventory Management API Endpoints
Flask Blueprint for comprehensive inventory management functionality
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from inventory_management import InventoryManagementSystem
from datetime import datetime, date
import json

# Create Blueprint
inventory_management_api = Blueprint('inventory_management_api', __name__)

# Initialize Inventory Management System
ims = InventoryManagementSystem()

@inventory_management_api.route('/api/inventory/item', methods=['POST'])
@login_required
def add_inventory_item():
    """Add a new inventory item"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('it_cd'):
            return jsonify({'success': False, 'error': 'Item code is required'}), 400
        
        # Add inventory item
        result = ims.add_inventory_item(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_management_api.route('/api/inventory/stock', methods=['POST'])
@login_required
def update_stock():
    """Update stock for purchase/sales/adjustment"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['it_cd', 'movement_type', 'qty', 'rate']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Update stock
        result = ims.update_stock(current_user.id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_management_api.route('/api/inventory/summary', methods=['GET'])
@login_required
def get_inventory_summary():
    """Get inventory summary statistics"""
    try:
        result = ims.get_inventory_summary(current_user.id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_management_api.route('/api/inventory/alerts', methods=['GET'])
@login_required
def get_low_stock_alerts():
    """Get low stock alerts"""
    try:
        result = ims.get_low_stock_alerts(current_user.id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_management_api.route('/api/inventory/movements', methods=['GET'])
@login_required
def get_stock_movements():
    """Get stock movement report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        it_cd = request.args.get('it_cd')
        
        result = ims.get_stock_movement_report(current_user.id, start_date, end_date, it_cd)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_management_api.route('/api/inventory/list', methods=['GET'])
@login_required
def get_inventory_list():
    """Get list of inventory items with filters"""
    try:
        category = request.args.get('category')
        _status = request.args.get('status')
        search = request.args.get('search') or request.args.get('item')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        page = (offset // limit) + 1 if limit else 1

        result = ims.get_inventory_list(
            user_id=current_user.id,
            page=page,
            per_page=limit,
            search=search,
            category=category
        )

        if not result.get('success'):
            return jsonify(result), 400

        items = []
        for entry in result.get('inventory', []):
            items.append({
                'it_cd': entry.get('item_code'),
                'it_nm': entry.get('item_name'),
                'category': entry.get('category'),
                'current_qty': float(entry.get('current_stock', 0)),
                'current_rate': float(entry.get('rate', 0)),
                'current_value': float(entry.get('stock_value', 0)),
                'min_stock': float(entry.get('reorder_level', 0)),
                'status': 'ACTIVE' if entry.get('current_stock', 0) > 0 else 'INACTIVE'
            })

        pagination = result.get('pagination', {})
        total_count = pagination.get('total', len(items))

        return jsonify({
            'success': True,
            'items': items,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count if limit else False
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_management_api.route('/api/inventory/categories', methods=['GET'])
@login_required
def get_categories():
    """Get list of inventory categories"""
    try:
        result = ims.get_categories(current_user.id)
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_management_api.route('/api/inventory/statistics', methods=['GET'])
@login_required
def get_inventory_statistics():
    """Get inventory statistics for dashboard"""
    try:
        # Get inventory summary
        summary_result = ims.get_inventory_summary(current_user.id)
        
        if not summary_result['success']:
            return jsonify(summary_result), 400
        
        # Get low stock alerts
        alerts_result = ims.get_low_stock_alerts(current_user.id)
        
        if not alerts_result['success']:
            return jsonify(alerts_result), 400
        
        # Get recent movements
        import sqlite3
        conn = sqlite3.connect(ims.db_path)
        cursor = conn.cursor()
        
        # Get today's movements
        today = date.today()
        cursor.execute('''
            SELECT COUNT(*) as today_movements
            FROM stock_movement 
            WHERE user_id = ? AND movement_date = ?
        ''', (current_user.id, today))
        
        today_movements = cursor.fetchone()[0] or 0
        
        # Get top items by value
        cursor.execute('''
            SELECT it_cd, it_nm, current_value
            FROM inventory 
            WHERE user_id = ? AND status = 'ACTIVE'
            ORDER BY current_value DESC
            LIMIT 5
        ''', (current_user.id,))
        
        top_items = []
        for row in cursor.fetchall():
            top_items.append({
                'it_cd': row[0],
                'it_nm': row[1],
                'current_value': float(row[2] or 0)
            })
        
        conn.close()
        
        statistics = {
            'summary': summary_result['summary'],
            'low_stock_alerts': alerts_result['count'],
            'today_movements': today_movements,
            'top_items': top_items
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@inventory_management_api.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Inventory Management API endpoint not found'}), 404

@inventory_management_api.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500 