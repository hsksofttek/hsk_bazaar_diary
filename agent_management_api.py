#!/usr/bin/env python3
"""
Agent Management API
Flask API endpoints for Agent Management System
"""

from flask import Blueprint, request, jsonify, render_template
from agent_management import AgentManagementSystem
from database import db
from models import User
from flask_login import login_required, current_user
import json
from datetime import datetime, timedelta

# Create Blueprint
agent_management_bp = Blueprint('agent_management', __name__)

# Initialize Agent Management System
agent_system = AgentManagementSystem()

@agent_management_bp.route('/agent-management')
@login_required
def agent_management():
    """Agent Management Dashboard"""
    return render_template('agent_management.html')

# Template-compatible endpoints (plural form)
@agent_management_bp.route('/api/agents', methods=['GET'])
@login_required
def get_agents_plural():
    """Get agents with pagination (for template compatibility)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Mock data for now - replace with actual database queries
        mock_agents = [
            {
                'id': 1,
                'agent_cd': 'AG001',
                'agent_nm': 'John Doe',
                'commission_rate': 5.0,
                'phone': '+91-9876543210',
                'email': 'john.doe@example.com',
                'mobile': '+91-9876543210',
                'status': 'ACTIVE',
                'joining_date': '2024-01-15',
                'created_date': '2024-01-15T09:00:00'
            },
            {
                'id': 2,
                'agent_cd': 'AG002',
                'agent_nm': 'Jane Smith',
                'commission_rate': 7.5,
                'phone': '+91-9876543211',
                'email': 'jane.smith@example.com',
                'mobile': '+91-9876543211',
                'status': 'ACTIVE',
                'joining_date': '2024-02-01',
                'created_date': '2024-02-01T09:00:00'
            }
        ]
        
        return jsonify({
            'success': True, 
            'agents': mock_agents,
            'total_pages': 1,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agents/<int:agent_id>', methods=['GET'])
@login_required
def get_agent_by_id_plural(agent_id):
    """Get agent by ID (for template compatibility)"""
    try:
        # Mock data for now
        mock_agent = {
            'id': agent_id,
            'agent_cd': f'AG{agent_id:03d}',
            'agent_nm': 'John Doe',
            'commission_rate': 5.0,
            'phone': '+91-9876543210',
            'email': 'john.doe@example.com',
            'mobile': '+91-9876543210',
            'gst_no': 'GST123456789',
            'pan_no': 'ABCDE1234F',
            'bank_name': 'HDFC Bank',
            'account_no': '1234567890',
            'ifsc_code': 'HDFC0001234',
            'status': 'ACTIVE',
            'joining_date': '2024-01-15',
            'address': '123 Main Street, City, State',
            'remarks': 'Experienced sales agent',
            'created_date': '2024-01-15T09:00:00'
        }
        
        return jsonify({'success': True, 'agent': mock_agent}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agents/<int:agent_id>', methods=['PUT'])
@login_required
def update_agent_plural(agent_id):
    """Update agent (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock update - replace with actual database update
        return jsonify({'success': True, 'message': 'Agent updated successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agents/<int:agent_id>', methods=['DELETE'])
@login_required
def delete_agent_plural(agent_id):
    """Delete agent (for template compatibility)"""
    try:
        # Mock delete - replace with actual database delete
        return jsonify({'success': True, 'message': 'Agent deleted successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agents', methods=['POST'])
@login_required
def create_agent_plural():
    """Create new agent (for template compatibility)"""
    try:
        data = request.get_json()
        
        # Mock create - replace with actual database create
        return jsonify({'success': True, 'message': 'Agent created successfully'}), 201
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Original endpoints (singular form)
@agent_management_bp.route('/api/agent', methods=['POST'])
@login_required
def create_agent():
    """Create new agent"""
    try:
        data = request.get_json()
        
        # Validate data
        is_valid, message = agent_system.validate_agent_data(data)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Create agent
        success, message = agent_system.create_agent(data)
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agent/<int:agent_id>', methods=['PUT'])
@login_required
def update_agent(agent_id):
    """Update agent"""
    try:
        data = request.get_json()
        
        success, message = agent_system.update_agent(agent_id, data)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agent/<int:agent_id>', methods=['DELETE'])
@login_required
def delete_agent(agent_id):
    """Delete agent"""
    try:
        success, message = agent_system.delete_agent(agent_id)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agent', methods=['GET'])
@login_required
def get_agents():
    """Get agents with filters"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('commission_rate'):
            filters['commission_rate'] = request.args.get('commission_rate')
        if request.args.get('joining_date'):
            filters['joining_date'] = datetime.strptime(request.args.get('joining_date'), '%Y-%m-%d').date()
        
        agents = agent_system.get_agents(filters)
        return jsonify({'success': True, 'data': agents}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agent/<int:agent_id>', methods=['GET'])
@login_required
def get_agent(agent_id):
    """Get agent by ID"""
    try:
        agent = agent_system.get_agent_by_id(agent_id)
        if agent:
            return jsonify({'success': True, 'agent': agent}), 200
        else:
            return jsonify({'success': False, 'message': 'Agent not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agent/commission-report/<int:agent_id>', methods=['GET'])
@login_required
def get_agent_commission_report(agent_id):
    """Get agent commission report"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        report_data = agent_system.get_commission_report(agent_id, date_from, date_to)
        return jsonify({'success': True, 'report': report_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agent/performance/<int:agent_id>', methods=['GET'])
@login_required
def get_agent_performance(agent_id):
    """Get agent performance metrics"""
    try:
        performance_data = agent_system.get_performance_metrics(agent_id)
        return jsonify({'success': True, 'performance': performance_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agent/validate-code/<agent_code>', methods=['GET'])
@login_required
def validate_agent_code(agent_code):
    """Validate agent code"""
    try:
        is_valid = agent_system.validate_agent_code(agent_code)
        return jsonify({'success': True, 'is_valid': is_valid}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agent/search', methods=['GET'])
@login_required
def search_agents():
    """Search agents"""
    try:
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')
        
        results = agent_system.search_agents(query, search_type)
        return jsonify({'success': True, 'results': results}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agent/export', methods=['GET'])
@login_required
def export_agent_data():
    """Export agent data"""
    try:
        export_type = request.args.get('type', 'csv')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        export_data = agent_system.export_data(export_type, date_from, date_to)
        
        if export_type == 'csv':
            from flask import send_file
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Agent Code', 'Agent Name', 'Commission Rate', 'Phone', 'Email', 'Status', 'Joining Date'])
            
            # Write data
            for row in export_data:
                writer.writerow(row)
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'agents_{datetime.now().strftime("%Y%m%d")}.csv'
            )
        else:
            return jsonify({'success': True, 'data': export_data}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@agent_management_bp.route('/api/agent/dashboard-data', methods=['GET'])
@login_required
def get_agent_dashboard_data():
    """Get dashboard data for agent management"""
    try:
        dashboard_data = agent_system.get_dashboard_data()
        return jsonify({'success': True, 'dashboard_data': dashboard_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500 