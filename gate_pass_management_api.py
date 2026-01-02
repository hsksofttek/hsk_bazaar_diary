#!/usr/bin/env python3
"""
Gate Pass Management API
Flask API endpoints for Gate Pass Management System
"""

from flask import Blueprint, request, jsonify, render_template
from gate_pass_management import GatePassManagementSystem
from database import db
from models import User
from flask_login import login_required, current_user
import json
from datetime import datetime, timedelta

# Create Blueprint
gate_pass_management_bp = Blueprint('gate_pass_management', __name__)

# Initialize Gate Pass Management System
gate_pass_system = GatePassManagementSystem()

@gate_pass_management_bp.route('/gate-pass-management')
@login_required
def gate_pass_management():
    """Gate Pass Management Dashboard"""
    return render_template('gate_pass_management.html')

# Template-compatible endpoints (plural form)
@gate_pass_management_bp.route('/api/gate-passes', methods=['GET'])
@login_required
def get_gate_passes_plural():
    """Get gate passes with pagination (for template compatibility)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Mock data for now - replace with actual database queries
        mock_gate_passes = [
            {
                'id': 1,
                'pass_no': 'GP001',
                'vehicle_no': 'MH12AB1234',
                'driver_name': 'John Doe',
                'pass_type': 'ENTRY',
                'entry_time': '2025-01-30T10:00:00',
                'exit_time': None,
                'status': 'ACTIVE',
                'created_date': '2025-01-30T09:00:00'
            },
            {
                'id': 2,
                'pass_no': 'GP002',
                'vehicle_no': 'MH12CD5678',
                'driver_name': 'Jane Smith',
                'pass_type': 'EXIT',
                'entry_time': '2025-01-30T08:00:00',
                'exit_time': '2025-01-30T16:00:00',
                'status': 'COMPLETED',
                'created_date': '2025-01-30T07:00:00'
            }
        ]
        
        return jsonify({
            'success': True, 
            'gate_passes': mock_gate_passes,
            'total_pages': 1,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-passes/<int:gate_pass_id>', methods=['GET'])
@login_required
def get_gate_pass_by_id_plural(gate_pass_id):
    """Get gate pass by ID (for template compatibility)"""
    try:
        # Mock data for now
        mock_gate_pass = {
            'id': gate_pass_id,
            'pass_no': f'GP{gate_pass_id:03d}',
            'vehicle_no': 'MH12AB1234',
            'driver_name': 'John Doe',
            'pass_type': 'ENTRY',
            'entry_time': '2025-01-30T10:00:00',
            'exit_time': None,
            'status': 'ACTIVE',
            'purpose': 'Delivery',
            'remarks': 'Regular delivery',
            'created_date': '2025-01-30T09:00:00'
        }
        
        return jsonify({'success': True, 'gate_pass': mock_gate_pass}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-passes/<int:gate_pass_id>', methods=['PUT'])
@login_required
def update_gate_pass_plural(gate_pass_id):
    """Update gate pass (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock update - replace with actual database update
        return jsonify({'success': True, 'message': 'Gate pass updated successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-passes/<int:gate_pass_id>', methods=['DELETE'])
@login_required
def delete_gate_pass_plural(gate_pass_id):
    """Delete gate pass (for template compatibility)"""
    try:
        # Mock delete - replace with actual database delete
        return jsonify({'success': True, 'message': 'Gate pass deleted successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-passes', methods=['POST'])
@login_required
def create_gate_pass_plural():
    """Create new gate pass (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock create - replace with actual database create
        return jsonify({'success': True, 'message': 'Gate pass created successfully'}), 201
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Original endpoints (singular form)
@gate_pass_management_bp.route('/api/gate-pass', methods=['POST'])
@login_required
def create_gate_pass():
    """Create new gate pass"""
    try:
        data = request.get_json()
        
        # Validate data
        is_valid, message = gate_pass_system.validate_gate_pass_data(data)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Create gate pass
        success, message = gate_pass_system.create_gate_pass(data)
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/<int:gate_pass_id>', methods=['PUT'])
@login_required
def update_gate_pass(gate_pass_id):
    """Update gate pass"""
    try:
        data = request.get_json()
        
        success, message = gate_pass_system.update_gate_pass(gate_pass_id, data)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/<int:gate_pass_id>', methods=['DELETE'])
@login_required
def delete_gate_pass(gate_pass_id):
    """Delete gate pass"""
    try:
        success, message = gate_pass_system.delete_gate_pass(gate_pass_id)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass', methods=['GET'])
@login_required
def get_gate_passes():
    """Get gate passes with filters"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('party_cd'):
            filters['party_cd'] = request.args.get('party_cd')
        if request.args.get('vehicle_no'):
            filters['vehicle_no'] = request.args.get('vehicle_no')
        if request.args.get('date_from'):
            filters['date_from'] = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d').date()
        if request.args.get('date_to'):
            filters['date_to'] = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d').date()
        
        gate_passes = gate_pass_system.get_gate_passes(filters)
        return jsonify({'success': True, 'data': gate_passes}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/<int:gate_pass_id>', methods=['GET'])
@login_required
def get_gate_pass(gate_pass_id):
    """Get gate pass by ID"""
    try:
        gate_pass = gate_pass_system.get_gate_pass_by_id(gate_pass_id)
        if gate_pass:
            return jsonify({'success': True, 'gate_pass': gate_pass}), 200
        else:
            return jsonify({'success': False, 'message': 'Gate pass not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/number/<int:gate_pass_no>', methods=['GET'])
@login_required
def get_gate_pass_by_number(gate_pass_no):
    """Get gate pass by number"""
    try:
        gate_pass = gate_pass_system.get_gate_pass_by_number(gate_pass_no)
        if gate_pass:
            return jsonify({'success': True, 'gate_pass': gate_pass}), 200
        else:
            return jsonify({'success': False, 'message': 'Gate pass not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/<int:gate_pass_id>/entry', methods=['POST'])
@login_required
def record_entry(gate_pass_id):
    """Record entry time for gate pass"""
    try:
        data = request.get_json()
        entry_time = data.get('entry_time', datetime.now())
        
        success, message = gate_pass_system.record_entry(gate_pass_id, entry_time)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/<int:gate_pass_id>/exit', methods=['POST'])
@login_required
def record_exit(gate_pass_id):
    """Record exit time for gate pass"""
    try:
        data = request.get_json()
        exit_time = data.get('exit_time', datetime.now())
        
        success, message = gate_pass_system.record_exit(gate_pass_id, exit_time)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/statistics', methods=['GET'])
@login_required
def get_gate_pass_statistics():
    """Get gate pass statistics"""
    try:
        stats = gate_pass_system.get_statistics()
        return jsonify({'success': True, 'statistics': stats}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/reports/<report_type>', methods=['GET'])
@login_required
def get_gate_pass_reports(report_type):
    """Get gate pass reports"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        report_data = gate_pass_system.generate_report(report_type, date_from, date_to)
        return jsonify({'success': True, 'report': report_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/next-number', methods=['GET'])
@login_required
def get_next_gate_pass_number():
    """Get next available gate pass number"""
    try:
        next_number = gate_pass_system.get_next_gate_pass_number()
        return jsonify({'success': True, 'next_number': next_number}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Additional routes for UI pages
@gate_pass_management_bp.route('/gate-passes')
@login_required
def gate_passes():
    """Gate Passes List Page"""
    return render_template('gate_pass_management.html')

@gate_pass_management_bp.route('/gate-pass-reports')
@login_required
def gate_pass_reports():
    """Gate Pass Reports Page"""
    return render_template('gate_pass_management.html')

@gate_pass_management_bp.route('/gate-pass-settings')
@login_required
def gate_pass_settings():
    """Gate Pass Settings Page"""
    return render_template('gate_pass_management.html')

@gate_pass_management_bp.route('/api/gate-pass/validate-number/<int:gate_pass_no>', methods=['GET'])
@login_required
def validate_gate_pass_number(gate_pass_no):
    """Validate gate pass number"""
    try:
        is_valid = gate_pass_system.validate_gate_pass_number(gate_pass_no)
        return jsonify({'success': True, 'is_valid': is_valid}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/search', methods=['GET'])
@login_required
def search_gate_passes():
    """Search gate passes"""
    try:
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')
        
        results = gate_pass_system.search_gate_passes(query, search_type)
        return jsonify({'success': True, 'results': results}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/bulk-import', methods=['POST'])
@login_required
def bulk_import_gate_passes():
    """Bulk import gate passes"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if file and file.filename.endswith('.csv'):
            success, message = gate_pass_system.bulk_import_from_csv(file)
            if success:
                return jsonify({'success': True, 'message': message}), 200
            else:
                return jsonify({'success': False, 'message': message}), 400
        else:
            return jsonify({'success': False, 'message': 'Invalid file format. Please upload CSV file.'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/export', methods=['GET'])
@login_required
def export_gate_pass_data():
    """Export gate pass data"""
    try:
        export_type = request.args.get('type', 'csv')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        export_data = gate_pass_system.export_data(export_type, date_from, date_to)
        
        if export_type == 'csv':
            from flask import send_file
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Pass No', 'Vehicle No', 'Driver Name', 'Type', 'Entry Time', 'Exit Time', 'Status'])
            
            # Write data
            for row in export_data:
                writer.writerow(row)
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'gate_passes_{datetime.now().strftime("%Y%m%d")}.csv'
            )
        else:
            return jsonify({'success': True, 'data': export_data}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@gate_pass_management_bp.route('/api/gate-pass/dashboard-data', methods=['GET'])
@login_required
def get_gate_pass_dashboard_data():
    """Get dashboard data for gate pass management"""
    try:
        dashboard_data = gate_pass_system.get_dashboard_data()
        return jsonify({'success': True, 'dashboard_data': dashboard_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500 