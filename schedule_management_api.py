#!/usr/bin/env python3
"""
Schedule Management API
Flask API endpoints for Schedule Management System
"""

from flask import Blueprint, request, jsonify, render_template
from schedule_management import ScheduleManagementSystem
from database import db
from models import User
from flask_login import login_required, current_user
import json
from datetime import datetime, timedelta

# Create Blueprint
schedule_management_bp = Blueprint('schedule_management', __name__)

# Initialize Schedule Management System
schedule_system = ScheduleManagementSystem()

@schedule_management_bp.route('/schedule-management')
@login_required
def schedule_management():
    """Schedule Management Dashboard"""
    return render_template('schedule_management.html')

# Template-compatible endpoints (plural form)
@schedule_management_bp.route('/api/schedules', methods=['GET'])
@login_required
def get_schedules_plural():
    """Get schedules with pagination (for template compatibility)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Mock data for now - replace with actual database queries
        mock_schedules = [
            {
                'id': 1,
                'schedule_type': 'PAYMENT',
                'party_nm': 'ABC Company',
                'due_date': '2025-02-15',
                'amount': 50000.00,
                'priority': 'HIGH',
                'status': 'PENDING',
                'reference_no': 'REF001',
                'created_date': '2025-01-30T09:00:00'
            },
            {
                'id': 2,
                'schedule_type': 'DELIVERY',
                'party_nm': 'XYZ Suppliers',
                'due_date': '2025-02-10',
                'amount': 25000.00,
                'priority': 'MEDIUM',
                'status': 'COMPLETED',
                'reference_no': 'REF002',
                'created_date': '2025-01-29T09:00:00'
            }
        ]
        
        return jsonify({
            'success': True, 
            'schedules': mock_schedules,
            'total_pages': 1,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedules/<int:schedule_id>', methods=['GET'])
@login_required
def get_schedule_by_id_plural(schedule_id):
    """Get schedule by ID (for template compatibility)"""
    try:
        # Mock data for now
        mock_schedule = {
            'id': schedule_id,
            'schedule_type': 'PAYMENT',
            'party_cd': 'P001',
            'party_nm': 'ABC Company',
            'due_date': '2025-02-15',
            'amount': 50000.00,
            'priority': 'HIGH',
            'status': 'PENDING',
            'reference_no': 'REF001',
            'reminder_days': 7,
            'description': 'Monthly payment due',
            'remarks': 'Important payment',
            'created_date': '2025-01-30T09:00:00'
        }
        
        return jsonify({'success': True, 'schedule': mock_schedule}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
@login_required
def update_schedule_plural(schedule_id):
    """Update schedule (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock update - replace with actual database update
        return jsonify({'success': True, 'message': 'Schedule updated successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_schedule_plural(schedule_id):
    """Delete schedule (for template compatibility)"""
    try:
        # Mock delete - replace with actual database delete
        return jsonify({'success': True, 'message': 'Schedule deleted successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedules', methods=['POST'])
@login_required
def create_schedule_plural():
    """Create new schedule (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock create - replace with actual database create
        return jsonify({'success': True, 'message': 'Schedule created successfully'}), 201
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Original endpoints (singular form)
@schedule_management_bp.route('/api/schedule', methods=['POST'])
@login_required
def create_schedule():
    """Create new schedule"""
    try:
        data = request.get_json()
        
        # Validate data
        is_valid, message = schedule_system.validate_schedule_data(data)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Create schedule
        success, message = schedule_system.create_schedule(data)
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/<int:schedule_id>', methods=['PUT'])
@login_required
def update_schedule(schedule_id):
    """Update schedule"""
    try:
        data = request.get_json()
        
        success, message = schedule_system.update_schedule(schedule_id, data)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_schedule(schedule_id):
    """Delete schedule"""
    try:
        success, message = schedule_system.delete_schedule(schedule_id)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule', methods=['GET'])
@login_required
def get_schedules():
    """Get schedules with filters"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('schedule_type'):
            filters['schedule_type'] = request.args.get('schedule_type')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('priority'):
            filters['priority'] = request.args.get('priority')
        if request.args.get('party_cd'):
            filters['party_cd'] = request.args.get('party_cd')
        if request.args.get('date_from'):
            filters['date_from'] = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d').date()
        if request.args.get('date_to'):
            filters['date_to'] = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d').date()
        
        schedules = schedule_system.get_schedules(filters)
        return jsonify({'success': True, 'data': schedules}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/<int:schedule_id>', methods=['GET'])
@login_required
def get_schedule(schedule_id):
    """Get schedule by ID"""
    try:
        schedule = schedule_system.get_schedule_by_id(schedule_id)
        if schedule:
            return jsonify({'success': True, 'schedule': schedule}), 200
        else:
            return jsonify({'success': False, 'message': 'Schedule not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/complete/<int:schedule_id>', methods=['POST'])
@login_required
def complete_schedule(schedule_id):
    """Mark schedule as completed"""
    try:
        data = request.get_json()
        completion_date = data.get('completion_date', datetime.now())
        
        success, message = schedule_system.complete_schedule(schedule_id, completion_date)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/reminders', methods=['GET'])
@login_required
def get_schedule_reminders():
    """Get schedule reminders"""
    try:
        days_ahead = request.args.get('days', 7, type=int)
        
        reminders = schedule_system.get_reminders(days_ahead)
        return jsonify({'success': True, 'reminders': reminders}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/overdue', methods=['GET'])
@login_required
def get_overdue_schedules():
    """Get overdue schedules"""
    try:
        overdue_schedules = schedule_system.get_overdue_schedules()
        return jsonify({'success': True, 'overdue_schedules': overdue_schedules}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/statistics', methods=['GET'])
@login_required
def get_schedule_statistics():
    """Get schedule statistics"""
    try:
        stats = schedule_system.get_statistics()
        return jsonify({'success': True, 'statistics': stats}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/reports/<report_type>', methods=['GET'])
@login_required
def get_schedule_reports(report_type):
    """Get schedule reports"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        report_data = schedule_system.generate_report(report_type, date_from, date_to)
        return jsonify({'success': True, 'report': report_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/validate-date', methods=['GET'])
@login_required
def validate_schedule_date():
    """Validate schedule date"""
    try:
        due_date = request.args.get('due_date')
        if due_date:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        
        is_valid = schedule_system.validate_schedule_date(due_date)
        return jsonify({'success': True, 'is_valid': is_valid}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/search', methods=['GET'])
@login_required
def search_schedules():
    """Search schedules"""
    try:
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')
        
        results = schedule_system.search_schedules(query, search_type)
        return jsonify({'success': True, 'results': results}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/export', methods=['GET'])
@login_required
def export_schedule_data():
    """Export schedule data"""
    try:
        export_type = request.args.get('type', 'csv')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        export_data = schedule_system.export_data(export_type, date_from, date_to)
        
        if export_type == 'csv':
            from flask import send_file
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Schedule Type', 'Party', 'Due Date', 'Amount', 'Priority', 'Status', 'Reference'])
            
            # Write data
            for row in export_data:
                writer.writerow(row)
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'schedules_{datetime.now().strftime("%Y%m%d")}.csv'
            )
        else:
            return jsonify({'success': True, 'data': export_data}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@schedule_management_bp.route('/api/schedule/dashboard-data', methods=['GET'])
@login_required
def get_schedule_dashboard_data():
    """Get dashboard data for schedule management"""
    try:
        dashboard_data = schedule_system.get_dashboard_data()
        return jsonify({'success': True, 'dashboard_data': dashboard_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500 