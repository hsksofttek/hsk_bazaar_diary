#!/usr/bin/env python3
"""
Narration Management API
Flask API endpoints for Narration Management System
"""

from flask import Blueprint, request, jsonify, render_template
from narration_management import NarrationManagementSystem
from database import db
from models import User
from flask_login import login_required, current_user
import json
from datetime import datetime, timedelta

# Create Blueprint
narration_management_bp = Blueprint('narration_management', __name__)

# Initialize Narration Management System
narration_system = NarrationManagementSystem()

@narration_management_bp.route('/narration-management')
@login_required
def narration_management():
    """Narration Management Dashboard"""
    return render_template('narration_management.html')

# Template-compatible endpoints (plural form)
@narration_management_bp.route('/api/narrations', methods=['GET'])
@login_required
def get_narrations_plural():
    """Get narrations with pagination (for template compatibility)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Mock data for now - replace with actual database queries
        mock_narrations = [
            {
                'id': 1,
                'narration_text': 'Payment received for invoice #INV001',
                'category': 'Sales',
                'usage_count': 15,
                'is_active': True,
                'created_by': 'admin',
                'created_date': '2024-01-15T09:00:00'
            },
            {
                'id': 2,
                'narration_text': 'Payment made to supplier for goods',
                'category': 'Purchase',
                'usage_count': 8,
                'is_active': True,
                'created_by': 'admin',
                'created_date': '2024-01-16T09:00:00'
            },
            {
                'id': 3,
                'narration_text': 'Monthly rent payment',
                'category': 'Expense',
                'usage_count': 12,
                'is_active': True,
                'created_by': 'admin',
                'created_date': '2024-01-17T09:00:00'
            }
        ]
        
        return jsonify({
            'success': True, 
            'narrations': mock_narrations,
            'total_pages': 1,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narrations/<int:narration_id>', methods=['GET'])
@login_required
def get_narration_by_id_plural(narration_id):
    """Get narration by ID (for template compatibility)"""
    try:
        # Mock data for now
        mock_narration = {
            'id': narration_id,
            'narration_text': 'Payment received for invoice #INV001',
            'category': 'Sales',
            'usage_count': 15,
            'is_active': True,
            'description': 'Standard payment narration for sales invoices',
            'created_by': 'admin',
            'created_date': '2024-01-15T09:00:00',
            'modified_date': '2024-01-20T10:00:00'
        }
        
        return jsonify({'success': True, 'narration': mock_narration}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narrations/<int:narration_id>', methods=['PUT'])
@login_required
def update_narration_plural(narration_id):
    """Update narration (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock update - replace with actual database update
        return jsonify({'success': True, 'message': 'Narration updated successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narrations/<int:narration_id>', methods=['DELETE'])
@login_required
def delete_narration_plural(narration_id):
    """Delete narration (for template compatibility)"""
    try:
        # Mock delete - replace with actual database delete
        return jsonify({'success': True, 'message': 'Narration deleted successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narrations', methods=['POST'])
@login_required
def create_narration_plural():
    """Create new narration (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock create - replace with actual database create
        return jsonify({'success': True, 'message': 'Narration created successfully'}), 201
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Original endpoints (singular form)
@narration_management_bp.route('/api/narration', methods=['POST'])
@login_required
def create_narration():
    """Create new narration"""
    try:
        data = request.get_json()
        
        # Validate data
        is_valid, message = narration_system.validate_narration_data(data)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Create narration
        success, message = narration_system.create_narration(data)
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/<int:narration_id>', methods=['PUT'])
@login_required
def update_narration(narration_id):
    """Update narration"""
    try:
        data = request.get_json()
        
        success, message = narration_system.update_narration(narration_id, data)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/<int:narration_id>', methods=['DELETE'])
@login_required
def delete_narration(narration_id):
    """Delete narration"""
    try:
        success, message = narration_system.delete_narration(narration_id)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration', methods=['GET'])
@login_required
def get_narrations():
    """Get narrations with filters"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        if request.args.get('is_active'):
            filters['is_active'] = request.args.get('is_active') == 'true'
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        narrations = narration_system.get_narrations(filters)
        return jsonify({'success': True, 'data': narrations}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/<int:narration_id>', methods=['GET'])
@login_required
def get_narration(narration_id):
    """Get narration by ID"""
    try:
        narration = narration_system.get_narration_by_id(narration_id)
        if narration:
            return jsonify({'success': True, 'narration': narration}), 200
        else:
            return jsonify({'success': False, 'message': 'Narration not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/category/<category>', methods=['GET'])
@login_required
def get_narrations_by_category(category):
    """Get narrations by category"""
    try:
        narrations = narration_system.get_narrations_by_category(category)
        return jsonify({'success': True, 'narrations': narrations}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/search', methods=['GET'])
@login_required
def search_narrations():
    """Search narrations"""
    try:
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')
        
        results = narration_system.search_narrations(query, search_type)
        return jsonify({'success': True, 'results': results}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/validate-text', methods=['POST'])
@login_required
def validate_narration_text():
    """Validate narration text"""
    try:
        data = request.get_json()
        narration_text = data.get('narration_text', '')
        
        is_valid = narration_system.validate_narration_text(narration_text)
        return jsonify({'success': True, 'is_valid': is_valid}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/duplicate-check', methods=['POST'])
@login_required
def check_duplicate_narration():
    """Check for duplicate narration"""
    try:
        data = request.get_json()
        narration_text = data.get('narration_text', '')
        
        is_duplicate = narration_system.check_duplicate_narration(narration_text)
        return jsonify({'success': True, 'is_duplicate': is_duplicate}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/usage-stats', methods=['GET'])
@login_required
def get_narration_usage_stats():
    """Get narration usage statistics"""
    try:
        stats = narration_system.get_usage_statistics()
        return jsonify({'success': True, 'statistics': stats}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/popular', methods=['GET'])
@login_required
def get_popular_narrations():
    """Get popular narrations"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        popular_narrations = narration_system.get_popular_narrations(limit)
        return jsonify({'success': True, 'popular_narrations': popular_narrations}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/export', methods=['GET'])
@login_required
def export_narration_data():
    """Export narration data"""
    try:
        export_type = request.args.get('type', 'csv')
        category = request.args.get('category')
        
        export_data = narration_system.export_data(export_type, category)
        
        if export_type == 'csv':
            from flask import send_file
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Narration Text', 'Category', 'Usage Count', 'Status', 'Created By', 'Created Date'])
            
            # Write data
            for row in export_data:
                writer.writerow(row)
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'narrations_{datetime.now().strftime("%Y%m%d")}.csv'
            )
        else:
            return jsonify({'success': True, 'data': export_data}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/import', methods=['POST'])
@login_required
def import_narration_data():
    """Import narration data"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if file and file.filename.endswith('.csv'):
            success, message = narration_system.import_from_csv(file)
            if success:
                return jsonify({'success': True, 'message': message}), 200
            else:
                return jsonify({'success': False, 'message': message}), 400
        else:
            return jsonify({'success': False, 'message': 'Invalid file format. Please upload CSV file.'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@narration_management_bp.route('/api/narration/dashboard-data', methods=['GET'])
@login_required
def get_narration_dashboard_data():
    """Get dashboard data for narration management"""
    try:
        dashboard_data = narration_system.get_dashboard_data()
        return jsonify({'success': True, 'dashboard_data': dashboard_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500 