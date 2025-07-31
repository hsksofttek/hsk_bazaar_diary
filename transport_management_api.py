#!/usr/bin/env python3
"""
Transport & Logistics Management API
Flask API endpoints for Transport Management System
"""

from flask import Blueprint, request, jsonify, render_template
from transport_management import TransportManagementSystem
from database import db
from models import User
from flask_login import login_required, current_user
import json
from datetime import datetime, timedelta

# Create Blueprint
transport_management_bp = Blueprint('transport_management', __name__)

# Initialize Transport Management System
transport_system = TransportManagementSystem()

@transport_management_bp.route('/transport-management')
@login_required
def transport_management():
    """Transport Management Dashboard"""
    return render_template('transport_management.html')

@transport_management_bp.route('/api/transport/company', methods=['POST'])
@login_required
def create_transport_company():
    """Create new transport company"""
    try:
        data = request.get_json()
        
        # Validate data
        is_valid, message = transport_system.validate_transport_data(data)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Create company
        success, message = transport_system.create_transport_company(data)
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/company/<int:transport_id>', methods=['PUT'])
@login_required
def update_transport_company(transport_id):
    """Update transport company"""
    try:
        data = request.get_json()
        
        success, message = transport_system.update_transport_company(transport_id, data)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/company/<int:transport_id>', methods=['DELETE'])
@login_required
def delete_transport_company(transport_id):
    """Delete transport company"""
    try:
        success, message = transport_system.delete_transport_company(transport_id)
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/companies', methods=['GET'])
@login_required
def get_transport_companies():
    """Get transport companies with filters"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('city'):
            filters['city'] = request.args.get('city')
        if request.args.get('state'):
            filters['state'] = request.args.get('state')
        if request.args.get('is_active'):
            filters['is_active'] = int(request.args.get('is_active'))
        
        companies = transport_system.get_transport_companies(filters)
        return jsonify({'success': True, 'data': companies}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/company/<int:transport_id>', methods=['GET'])
@login_required
def get_transport_company(transport_id):
    """Get transport company by ID"""
    try:
        company = transport_system.get_transport_by_id(transport_id)
        if company:
            return jsonify({'success': True, 'data': company}), 200
        else:
            return jsonify({'success': False, 'message': 'Transport company not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/company/code/<trans_cd>', methods=['GET'])
@login_required
def get_transport_by_code(trans_cd):
    """Get transport company by code"""
    try:
        company = transport_system.get_transport_by_code(trans_cd)
        if company:
            return jsonify({'success': True, 'data': company}), 200
        else:
            return jsonify({'success': False, 'message': 'Transport company not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/calculate-freight', methods=['POST'])
@login_required
def calculate_freight_charges():
    """Calculate freight charges"""
    try:
        data = request.get_json()
        charges = transport_system.calculate_freight_charges(data)
        return jsonify({'success': True, 'data': charges}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/statistics', methods=['GET'])
@login_required
def get_transport_statistics():
    """Get transport statistics"""
    try:
        stats = transport_system.get_transport_statistics()
        return jsonify({'success': True, 'data': stats}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/reports/<report_type>', methods=['GET'])
@login_required
def get_transport_reports(report_type):
    """Get transport reports"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('state'):
            filters['state'] = request.args.get('state')
        if request.args.get('is_active'):
            filters['is_active'] = int(request.args.get('is_active'))
        
        reports = transport_system.get_transport_reports(report_type, filters)
        return jsonify({'success': True, 'data': reports}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/cities', methods=['GET'])
@login_required
def get_transport_cities():
    """Get available transport cities"""
    try:
        cities = transport_system.get_transport_cities()
        return jsonify({'success': True, 'data': cities}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/states', methods=['GET'])
@login_required
def get_transport_states():
    """Get available transport states"""
    try:
        states = transport_system.get_transport_states()
        return jsonify({'success': True, 'data': states}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# UI Routes
@transport_management_bp.route('/transport-companies')
@login_required
def transport_companies():
    """Transport Companies Page"""
    return render_template('transport_companies.html')

@transport_management_bp.route('/transport-reports')
@login_required
def transport_reports():
    """Transport Reports Page"""
    return render_template('transport_reports.html')

@transport_management_bp.route('/transport-settings')
@login_required
def transport_settings():
    """Transport Settings Page"""
    return render_template('transport_settings.html')

# Utility Routes
@transport_management_bp.route('/api/transport/validate-code/<trans_cd>', methods=['GET'])
@login_required
def validate_transport_code(trans_cd):
    """Validate transport code"""
    try:
        company = transport_system.get_transport_by_code(trans_cd)
        if company:
            return jsonify({'success': True, 'data': company}), 200
        else:
            return jsonify({'success': False, 'message': 'Transport company not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/search', methods=['GET'])
@login_required
def search_transport_companies():
    """Search transport companies"""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({'success': False, 'message': 'Search term is required'}), 400
        
        # Get all companies and filter by search term
        companies = transport_system.get_transport_companies()
        filtered_companies = []
        
        for company in companies:
            if (search_term.lower() in company['trans_cd'].lower() or
                search_term.lower() in company['trans_nm'].lower() or
                search_term.lower() in (company['city'] or '').lower() or
                search_term.lower() in (company['state'] or '').lower()):
                filtered_companies.append(company)
        
        return jsonify({'success': True, 'data': filtered_companies}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Bulk Operations
@transport_management_bp.route('/api/transport/bulk-import', methods=['POST'])
@login_required
def bulk_import_transport():
    """Bulk import transport companies"""
    try:
        data = request.get_json()
        companies = data.get('companies', [])
        
        results = []
        success_count = 0
        error_count = 0
        
        for company in companies:
            is_valid, message = transport_system.validate_transport_data(company)
            if is_valid:
                success, msg = transport_system.create_transport_company(company)
                if success:
                    success_count += 1
                    results.append({'company': company, 'status': 'success', 'message': msg})
                else:
                    error_count += 1
                    results.append({'company': company, 'status': 'error', 'message': msg})
            else:
                error_count += 1
                results.append({'company': company, 'status': 'error', 'message': message})
        
        return jsonify({
            'success': True,
            'data': {
                'total': len(companies),
                'success_count': success_count,
                'error_count': error_count,
                'results': results
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@transport_management_bp.route('/api/transport/export', methods=['GET'])
@login_required
def export_transport_data():
    """Export transport data"""
    try:
        filters = {}
        
        # Get filter parameters
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('city'):
            filters['city'] = request.args.get('city')
        if request.args.get('state'):
            filters['state'] = request.args.get('state')
        if request.args.get('is_active'):
            filters['is_active'] = int(request.args.get('is_active'))
        
        companies = transport_system.get_transport_companies(filters)
        
        # Format for export
        export_data = []
        for company in companies:
            export_data.append({
                'Transport Code': company.get('trans_cd'),
                'Transport Name': company.get('trans_nm'),
                'Address': company.get('address'),
                'Phone': company.get('phone'),
                'Mobile': company.get('mobile'),
                'Email': company.get('email'),
                'Destination': company.get('dest'),
                'City': company.get('city'),
                'State': company.get('state'),
                'Vehicle No': company.get('vehicle_no'),
                'Driver Name': company.get('driver_name'),
                'License No': company.get('license_no'),
                'GST No': company.get('gst_no'),
                'PAN No': company.get('pan_no'),
                'Commission': company.get('commission'),
                'Status': company.get('status'),
                'Remarks': company.get('remarks'),
                'Is Active': 'Yes' if company.get('is_active') else 'No',
                'Created Date': company.get('created_date')
            })
        
        return jsonify({'success': True, 'data': export_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Dashboard Data
@transport_management_bp.route('/api/transport/dashboard-data', methods=['GET'])
@login_required
def get_transport_dashboard_data():
    """Get dashboard data for transport management"""
    try:
        # Get statistics
        stats = transport_system.get_transport_statistics()
        
        # Get recent companies
        recent_companies = transport_system.get_transport_companies()
        recent_companies = recent_companies[:10]  # Limit to 10 recent companies
        
        # Get top states
        top_states = stats.get('top_states', [])[:5]
        
        # Get top cities
        top_cities = stats.get('top_cities', [])[:5]
        
        return jsonify({
            'success': True,
            'data': {
                'statistics': stats,
                'recent_companies': recent_companies,
                'top_states': top_states,
                'top_cities': top_cities
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500 