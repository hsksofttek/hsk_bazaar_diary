#!/usr/bin/env python3
"""
Transport & Logistics Management System
Comprehensive transport company and freight management
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database import db
from models import TransportMaster, Party, Item
import json
import logging

class TransportManagementSystem:
    """Comprehensive Transport & Logistics Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_transport_company(self, transport_data: Dict) -> Tuple[bool, str]:
        """Create new transport company"""
        try:
            # Validate required fields
            required_fields = ['trans_cd', 'trans_nm']
            for field in required_fields:
                if not transport_data.get(field):
                    return False, f"{field.replace('_', ' ').title()} is required"
            
            # Check if transport code already exists
            existing = TransportMaster.query.filter_by(trans_cd=transport_data['trans_cd']).first()
            if existing:
                return False, "Transport code already exists"
            
            # Create new transport company
            transport = TransportMaster(
                trans_cd=transport_data['trans_cd'],
                trans_nm=transport_data['trans_nm'],
                address=transport_data.get('address', ''),
                phone=transport_data.get('phone', ''),
                mobile=transport_data.get('mobile', ''),
                email=transport_data.get('email', ''),
                dest=transport_data.get('dest', ''),
                city=transport_data.get('city', ''),
                state=transport_data.get('state', ''),
                vehicle_no=transport_data.get('vehicle_no', ''),
                driver_name=transport_data.get('driver_name', ''),
                license_no=transport_data.get('license_no', ''),
                gst_no=transport_data.get('gst_no', ''),
                pan_no=transport_data.get('pan_no', ''),
                commission=float(transport_data.get('commission', 0)),
                status=transport_data.get('status', 'ACTIVE'),
                remarks=transport_data.get('remarks', ''),
                is_active=1
            )
            
            db.session.add(transport)
            db.session.commit()
            
            return True, "Transport company created successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating transport company: {e}")
            return False, f"Error creating transport company: {str(e)}"
    
    def update_transport_company(self, transport_id: int, transport_data: Dict) -> Tuple[bool, str]:
        """Update existing transport company"""
        try:
            transport = TransportMaster.query.get(transport_id)
            if not transport:
                return False, "Transport company not found"
            
            # Update fields
            for key, value in transport_data.items():
                if hasattr(transport, key):
                    if key == 'commission':
                        setattr(transport, key, float(value))
                    elif key == 'is_active':
                        setattr(transport, key, int(value))
                    else:
                        setattr(transport, key, value)
            
            db.session.commit()
            return True, "Transport company updated successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating transport company: {e}")
            return False, f"Error updating transport company: {str(e)}"
    
    def delete_transport_company(self, transport_id: int) -> Tuple[bool, str]:
        """Delete transport company"""
        try:
            transport = TransportMaster.query.get(transport_id)
            if not transport:
                return False, "Transport company not found"
            
            db.session.delete(transport)
            db.session.commit()
            return True, "Transport company deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error deleting transport company: {e}")
            return False, f"Error deleting transport company: {str(e)}"
    
    def get_transport_companies(self, filters: Dict = None) -> List[Dict]:
        """Get transport companies with optional filters"""
        try:
            query = TransportMaster.query
            
            if filters:
                if filters.get('status'):
                    query = query.filter(TransportMaster.status == filters['status'])
                if filters.get('city'):
                    query = query.filter(TransportMaster.city == filters['city'])
                if filters.get('state'):
                    query = query.filter(TransportMaster.state == filters['state'])
                if filters.get('is_active'):
                    query = query.filter(TransportMaster.is_active == filters['is_active'])
            
            transports = query.all()
            return [self._transport_to_dict(transport) for transport in transports]
            
        except Exception as e:
            self.logger.error(f"Error getting transport companies: {e}")
            return []
    
    def get_transport_by_id(self, transport_id: int) -> Optional[Dict]:
        """Get transport company by ID"""
        try:
            transport = TransportMaster.query.get(transport_id)
            return self._transport_to_dict(transport) if transport else None
        except Exception as e:
            self.logger.error(f"Error getting transport by ID: {e}")
            return None
    
    def get_transport_by_code(self, trans_cd: str) -> Optional[Dict]:
        """Get transport company by code"""
        try:
            transport = TransportMaster.query.filter_by(trans_cd=trans_cd).first()
            return self._transport_to_dict(transport) if transport else None
        except Exception as e:
            self.logger.error(f"Error getting transport by code: {e}")
            return None
    
    def calculate_freight_charges(self, freight_data: Dict) -> Dict:
        """Calculate freight charges for given data"""
        try:
            distance = float(freight_data.get('distance', 0))
            weight = float(freight_data.get('weight', 0))
            volume = float(freight_data.get('volume', 0))
            transport_type = freight_data.get('transport_type', 'road')
            urgency = freight_data.get('urgency', 'normal')
            
            # Base rates
            base_rate_per_km = 2.0  # Base rate per kilometer
            weight_rate = 0.5  # Rate per kg
            volume_rate = 0.3  # Rate per cubic meter
            
            # Calculate base freight
            distance_charge = distance * base_rate_per_km
            weight_charge = weight * weight_rate
            volume_charge = volume * volume_rate
            
            # Apply transport type multiplier
            type_multipliers = {
                'road': 1.0,
                'rail': 0.8,
                'air': 3.0,
                'sea': 0.6
            }
            type_multiplier = type_multipliers.get(transport_type, 1.0)
            
            # Apply urgency multiplier
            urgency_multipliers = {
                'normal': 1.0,
                'express': 1.5,
                'urgent': 2.0,
                'same_day': 3.0
            }
            urgency_multiplier = urgency_multipliers.get(urgency, 1.0)
            
            # Calculate total
            base_freight = max(distance_charge, weight_charge, volume_charge)
            total_freight = base_freight * type_multiplier * urgency_multiplier
            
            # Additional charges
            fuel_surcharge = total_freight * 0.1  # 10% fuel surcharge
            handling_charge = 50.0  # Fixed handling charge
            insurance_charge = total_freight * 0.02  # 2% insurance
            
            grand_total = total_freight + fuel_surcharge + handling_charge + insurance_charge
            
            return {
                'distance_charge': round(distance_charge, 2),
                'weight_charge': round(weight_charge, 2),
                'volume_charge': round(volume_charge, 2),
                'base_freight': round(base_freight, 2),
                'type_multiplier': type_multiplier,
                'urgency_multiplier': urgency_multiplier,
                'total_freight': round(total_freight, 2),
                'fuel_surcharge': round(fuel_surcharge, 2),
                'handling_charge': round(handling_charge, 2),
                'insurance_charge': round(insurance_charge, 2),
                'grand_total': round(grand_total, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating freight charges: {e}")
            return {}
    
    def get_transport_statistics(self) -> Dict:
        """Get transport statistics"""
        try:
            total_companies = TransportMaster.query.count()
            active_companies = TransportMaster.query.filter_by(is_active=1).count()
            inactive_companies = TransportMaster.query.filter_by(is_active=0).count()
            
            # Get companies by status
            status_stats = db.session.query(
                TransportMaster.status,
                db.func.count(TransportMaster.id).label('count')
            ).group_by(TransportMaster.status).all()
            
            # Get companies by state
            state_stats = db.session.query(
                TransportMaster.state,
                db.func.count(TransportMaster.id).label('count')
            ).group_by(TransportMaster.state).order_by(db.func.count(TransportMaster.id).desc()).limit(10).all()
            
            # Get companies by city
            city_stats = db.session.query(
                TransportMaster.city,
                db.func.count(TransportMaster.id).label('count')
            ).group_by(TransportMaster.city).order_by(db.func.count(TransportMaster.id).desc()).limit(10).all()
            
            return {
                'total_companies': total_companies,
                'active_companies': active_companies,
                'inactive_companies': inactive_companies,
                'status_distribution': [
                    {
                        'status': stat.status,
                        'count': stat.count
                    } for stat in status_stats
                ],
                'top_states': [
                    {
                        'state': stat.state or 'Unknown',
                        'count': stat.count
                    } for stat in state_stats
                ],
                'top_cities': [
                    {
                        'city': stat.city or 'Unknown',
                        'count': stat.count
                    } for stat in city_stats
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting transport statistics: {e}")
            return {}
    
    def get_transport_reports(self, report_type: str, filters: Dict = None) -> List[Dict]:
        """Get transport reports"""
        try:
            if report_type == 'summary':
                return self._get_summary_report(filters)
            elif report_type == 'status_wise':
                return self._get_status_wise_report(filters)
            elif report_type == 'location_wise':
                return self._get_location_wise_report(filters)
            elif report_type == 'commission_wise':
                return self._get_commission_wise_report(filters)
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting transport reports: {e}")
            return []
    
    def _get_summary_report(self, filters: Dict = None) -> List[Dict]:
        """Get summary report"""
        try:
            query = db.session.query(
                TransportMaster.trans_cd,
                TransportMaster.trans_nm,
                TransportMaster.city,
                TransportMaster.state,
                TransportMaster.status,
                TransportMaster.commission,
                TransportMaster.is_active
            )
            
            if filters:
                if filters.get('status'):
                    query = query.filter(TransportMaster.status == filters['status'])
                if filters.get('state'):
                    query = query.filter(TransportMaster.state == filters['state'])
                if filters.get('is_active'):
                    query = query.filter(TransportMaster.is_active == filters['is_active'])
            
            results = query.all()
            return [
                {
                    'trans_cd': result.trans_cd,
                    'trans_nm': result.trans_nm,
                    'city': result.city,
                    'state': result.state,
                    'status': result.status,
                    'commission': result.commission,
                    'is_active': bool(result.is_active)
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting summary report: {e}")
            return []
    
    def _get_status_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get status-wise report"""
        try:
            query = db.session.query(
                TransportMaster.status,
                db.func.count(TransportMaster.id).label('count'),
                db.func.avg(TransportMaster.commission).label('avg_commission')
            ).group_by(TransportMaster.status)
            
            if filters:
                if filters.get('is_active'):
                    query = query.filter(TransportMaster.is_active == filters['is_active'])
            
            results = query.all()
            return [
                {
                    'status': result.status,
                    'count': result.count,
                    'avg_commission': round(result.avg_commission or 0, 2)
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting status-wise report: {e}")
            return []
    
    def _get_location_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get location-wise report"""
        try:
            query = db.session.query(
                TransportMaster.state,
                TransportMaster.city,
                db.func.count(TransportMaster.id).label('count')
            ).group_by(TransportMaster.state, TransportMaster.city)
            
            if filters:
                if filters.get('status'):
                    query = query.filter(TransportMaster.status == filters['status'])
                if filters.get('is_active'):
                    query = query.filter(TransportMaster.is_active == filters['is_active'])
            
            results = query.all()
            return [
                {
                    'state': result.state or 'Unknown',
                    'city': result.city or 'Unknown',
                    'count': result.count
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting location-wise report: {e}")
            return []
    
    def _get_commission_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get commission-wise report"""
        try:
            query = db.session.query(
                TransportMaster.trans_cd,
                TransportMaster.trans_nm,
                TransportMaster.commission,
                TransportMaster.status
            ).order_by(TransportMaster.commission.desc())
            
            if filters:
                if filters.get('status'):
                    query = query.filter(TransportMaster.status == filters['status'])
                if filters.get('is_active'):
                    query = query.filter(TransportMaster.is_active == filters['is_active'])
            
            results = query.all()
            return [
                {
                    'trans_cd': result.trans_cd,
                    'trans_nm': result.trans_nm,
                    'commission': result.commission,
                    'status': result.status
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting commission-wise report: {e}")
            return []
    
    def validate_transport_data(self, transport_data: Dict) -> Tuple[bool, str]:
        """Validate transport data"""
        try:
            # Check required fields
            if not transport_data.get('trans_cd'):
                return False, "Transport code is required"
            
            if not transport_data.get('trans_nm'):
                return False, "Transport name is required"
            
            # Check if transport code already exists (for new entries)
            if 'id' not in transport_data:
                existing = TransportMaster.query.filter_by(trans_cd=transport_data['trans_cd']).first()
                if existing:
                    return False, "Transport code already exists"
            
            # Validate email format if provided
            if transport_data.get('email'):
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, transport_data['email']):
                    return False, "Invalid email format"
            
            # Validate phone number if provided
            if transport_data.get('phone'):
                phone = transport_data['phone'].replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                if not phone.isdigit() or len(phone) < 10:
                    return False, "Invalid phone number format"
            
            return True, "Data is valid"
            
        except Exception as e:
            self.logger.error(f"Error validating transport data: {e}")
            return False, f"Validation error: {str(e)}"
    
    def get_transport_cities(self) -> List[str]:
        """Get available transport cities"""
        try:
            cities = db.session.query(TransportMaster.city).distinct().all()
            return [city[0] for city in cities if city[0]]
        except Exception as e:
            self.logger.error(f"Error getting transport cities: {e}")
            return []
    
    def get_transport_states(self) -> List[str]:
        """Get available transport states"""
        try:
            states = db.session.query(TransportMaster.state).distinct().all()
            return [state[0] for state in states if state[0]]
        except Exception as e:
            self.logger.error(f"Error getting transport states: {e}")
            return []
    
    def _transport_to_dict(self, transport: TransportMaster) -> Dict:
        """Convert transport object to dictionary"""
        if not transport:
            return {}
        
        return {
            'id': transport.id,
            'trans_cd': transport.trans_cd,
            'trans_nm': transport.trans_nm,
            'address': transport.address,
            'phone': transport.phone,
            'mobile': transport.mobile,
            'email': transport.email,
            'dest': transport.dest,
            'city': transport.city,
            'state': transport.state,
            'vehicle_no': transport.vehicle_no,
            'driver_name': transport.driver_name,
            'license_no': transport.license_no,
            'gst_no': transport.gst_no,
            'pan_no': transport.pan_no,
            'commission': transport.commission,
            'status': transport.status,
            'remarks': transport.remarks,
            'is_active': bool(transport.is_active),
            'created_date': transport.created_date.isoformat() if transport.created_date else None,
            'modified_date': transport.modified_date.isoformat() if transport.modified_date else None
        } 