#!/usr/bin/env python3
"""
Gate Pass Management System
Vehicle entry and exit tracking system
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database import db
from models import GatePass, Party, TransportMaster
import json
import logging

class GatePassManagementSystem:
    """Comprehensive Gate Pass Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_gate_pass(self, gate_pass_data: Dict) -> Tuple[bool, str]:
        """Create new gate pass entry"""
        try:
            # Validate required fields
            required_fields = ['gate_pass_no', 'gate_pass_date', 'party_cd']
            for field in required_fields:
                if not gate_pass_data.get(field):
                    return False, f"{field.replace('_', ' ').title()} is required"
            
            # Check if gate pass number already exists
            existing = GatePass.query.filter_by(gate_pass_no=gate_pass_data['gate_pass_no']).first()
            if existing:
                return False, "Gate pass number already exists"
            
            # Create new gate pass
            gate_pass = GatePass(
                gate_pass_no=gate_pass_data['gate_pass_no'],
                gate_pass_date=datetime.strptime(gate_pass_data['gate_pass_date'], '%Y-%m-%d').date(),
                party_cd=gate_pass_data['party_cd'],
                vehicle_no=gate_pass_data.get('vehicle_no', ''),
                driver_name=gate_pass_data.get('driver_name', ''),
                license_no=gate_pass_data.get('license_no', ''),
                purpose=gate_pass_data.get('purpose', ''),
                items_description=gate_pass_data.get('items_description', ''),
                quantity=float(gate_pass_data.get('quantity', 0)),
                weight=float(gate_pass_data.get('weight', 0)),
                entry_time=datetime.strptime(gate_pass_data['entry_time'], '%Y-%m-%d %H:%M:%S') if gate_pass_data.get('entry_time') else None,
                exit_time=datetime.strptime(gate_pass_data['exit_time'], '%Y-%m-%d %H:%M:%S') if gate_pass_data.get('exit_time') else None,
                status=gate_pass_data.get('status', 'ACTIVE'),
                authorized_by=gate_pass_data.get('authorized_by', ''),
                remarks=gate_pass_data.get('remarks', '')
            )
            
            db.session.add(gate_pass)
            db.session.commit()
            
            return True, "Gate pass created successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating gate pass: {e}")
            return False, f"Error creating gate pass: {str(e)}"
    
    def update_gate_pass(self, gate_pass_id: int, gate_pass_data: Dict) -> Tuple[bool, str]:
        """Update existing gate pass"""
        try:
            gate_pass = GatePass.query.get(gate_pass_id)
            if not gate_pass:
                return False, "Gate pass not found"
            
            # Update fields
            for key, value in gate_pass_data.items():
                if hasattr(gate_pass, key):
                    if key in ['gate_pass_date'] and value:
                        setattr(gate_pass, key, datetime.strptime(value, '%Y-%m-%d').date())
                    elif key in ['entry_time', 'exit_time'] and value:
                        setattr(gate_pass, key, datetime.strptime(value, '%Y-%m-%d %H:%M:%S'))
                    elif key in ['quantity', 'weight']:
                        setattr(gate_pass, key, float(value))
                    else:
                        setattr(gate_pass, key, value)
            
            db.session.commit()
            return True, "Gate pass updated successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating gate pass: {e}")
            return False, f"Error updating gate pass: {str(e)}"
    
    def delete_gate_pass(self, gate_pass_id: int) -> Tuple[bool, str]:
        """Delete gate pass"""
        try:
            gate_pass = GatePass.query.get(gate_pass_id)
            if not gate_pass:
                return False, "Gate pass not found"
            
            db.session.delete(gate_pass)
            db.session.commit()
            return True, "Gate pass deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error deleting gate pass: {e}")
            return False, f"Error deleting gate pass: {str(e)}"
    
    def get_gate_passes(self, filters: Dict = None) -> List[Dict]:
        """Get gate passes with optional filters"""
        try:
            query = GatePass.query
            
            if filters:
                if filters.get('status'):
                    query = query.filter(GatePass.status == filters['status'])
                if filters.get('party_cd'):
                    query = query.filter(GatePass.party_cd == filters['party_cd'])
                if filters.get('vehicle_no'):
                    query = query.filter(GatePass.vehicle_no.like(f"%{filters['vehicle_no']}%"))
                if filters.get('date_from'):
                    query = query.filter(GatePass.gate_pass_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(GatePass.gate_pass_date <= filters['date_to'])
            
            gate_passes = query.order_by(GatePass.gate_pass_date.desc()).all()
            return [self._gate_pass_to_dict(gate_pass) for gate_pass in gate_passes]
            
        except Exception as e:
            self.logger.error(f"Error getting gate passes: {e}")
            return []
    
    def get_gate_pass_by_id(self, gate_pass_id: int) -> Optional[Dict]:
        """Get gate pass by ID"""
        try:
            gate_pass = GatePass.query.get(gate_pass_id)
            return self._gate_pass_to_dict(gate_pass) if gate_pass else None
        except Exception as e:
            self.logger.error(f"Error getting gate pass by ID: {e}")
            return None
    
    def get_gate_pass_by_number(self, gate_pass_no: int) -> Optional[Dict]:
        """Get gate pass by number"""
        try:
            gate_pass = GatePass.query.filter_by(gate_pass_no=gate_pass_no).first()
            return self._gate_pass_to_dict(gate_pass) if gate_pass else None
        except Exception as e:
            self.logger.error(f"Error getting gate pass by number: {e}")
            return None
    
    def record_entry(self, gate_pass_id: int, entry_time: str = None) -> Tuple[bool, str]:
        """Record vehicle entry"""
        try:
            gate_pass = GatePass.query.get(gate_pass_id)
            if not gate_pass:
                return False, "Gate pass not found"
            
            if gate_pass.entry_time:
                return False, "Entry already recorded"
            
            if entry_time:
                gate_pass.entry_time = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
            else:
                gate_pass.entry_time = datetime.now()
            
            gate_pass.status = 'INSIDE'
            db.session.commit()
            return True, "Entry recorded successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error recording entry: {e}")
            return False, f"Error recording entry: {str(e)}"
    
    def record_exit(self, gate_pass_id: int, exit_time: str = None) -> Tuple[bool, str]:
        """Record vehicle exit"""
        try:
            gate_pass = GatePass.query.get(gate_pass_id)
            if not gate_pass:
                return False, "Gate pass not found"
            
            if not gate_pass.entry_time:
                return False, "Entry must be recorded before exit"
            
            if gate_pass.exit_time:
                return False, "Exit already recorded"
            
            if exit_time:
                gate_pass.exit_time = datetime.strptime(exit_time, '%Y-%m-%d %H:%M:%S')
            else:
                gate_pass.exit_time = datetime.now()
            
            gate_pass.status = 'COMPLETED'
            db.session.commit()
            return True, "Exit recorded successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error recording exit: {e}")
            return False, f"Error recording exit: {str(e)}"
    
    def get_gate_pass_statistics(self) -> Dict:
        """Get gate pass statistics"""
        try:
            total_passes = GatePass.query.count()
            active_passes = GatePass.query.filter_by(status='ACTIVE').count()
            inside_passes = GatePass.query.filter_by(status='INSIDE').count()
            completed_passes = GatePass.query.filter_by(status='COMPLETED').count()
            
            # Get passes by status
            status_stats = db.session.query(
                GatePass.status,
                db.func.count(GatePass.id).label('count')
            ).group_by(GatePass.status).all()
            
            # Get passes by party
            party_stats = db.session.query(
                GatePass.party_cd,
                db.func.count(GatePass.id).label('count')
            ).group_by(GatePass.party_cd).order_by(db.func.count(GatePass.id).desc()).limit(10).all()
            
            # Get today's passes
            today = datetime.now().date()
            today_passes = GatePass.query.filter_by(gate_pass_date=today).count()
            
            # Get pending entries (no entry time)
            pending_entries = GatePass.query.filter(
                GatePass.status == 'ACTIVE',
                GatePass.entry_time.is_(None)
            ).count()
            
            # Get pending exits (entry recorded but no exit)
            pending_exits = GatePass.query.filter(
                GatePass.status == 'INSIDE',
                GatePass.exit_time.is_(None)
            ).count()
            
            return {
                'total_passes': total_passes,
                'active_passes': active_passes,
                'inside_passes': inside_passes,
                'completed_passes': completed_passes,
                'today_passes': today_passes,
                'pending_entries': pending_entries,
                'pending_exits': pending_exits,
                'status_distribution': [
                    {
                        'status': stat.status,
                        'count': stat.count
                    } for stat in status_stats
                ],
                'top_parties': [
                    {
                        'party_cd': stat.party_cd,
                        'count': stat.count
                    } for stat in party_stats
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting gate pass statistics: {e}")
            return {}
    
    def get_gate_pass_reports(self, report_type: str, filters: Dict = None) -> List[Dict]:
        """Get gate pass reports"""
        try:
            if report_type == 'summary':
                return self._get_summary_report(filters)
            elif report_type == 'status_wise':
                return self._get_status_wise_report(filters)
            elif report_type == 'party_wise':
                return self._get_party_wise_report(filters)
            elif report_type == 'vehicle_wise':
                return self._get_vehicle_wise_report(filters)
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting gate pass reports: {e}")
            return []
    
    def _get_summary_report(self, filters: Dict = None) -> List[Dict]:
        """Get summary report"""
        try:
            query = db.session.query(
                GatePass.gate_pass_no,
                GatePass.gate_pass_date,
                GatePass.party_cd,
                GatePass.vehicle_no,
                GatePass.driver_name,
                GatePass.purpose,
                GatePass.status,
                GatePass.entry_time,
                GatePass.exit_time
            )
            
            if filters:
                if filters.get('status'):
                    query = query.filter(GatePass.status == filters['status'])
                if filters.get('party_cd'):
                    query = query.filter(GatePass.party_cd == filters['party_cd'])
                if filters.get('date_from'):
                    query = query.filter(GatePass.gate_pass_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(GatePass.gate_pass_date <= filters['date_to'])
            
            results = query.all()
            return [
                {
                    'gate_pass_no': result.gate_pass_no,
                    'gate_pass_date': result.gate_pass_date.isoformat() if result.gate_pass_date else None,
                    'party_cd': result.party_cd,
                    'vehicle_no': result.vehicle_no,
                    'driver_name': result.driver_name,
                    'purpose': result.purpose,
                    'status': result.status,
                    'entry_time': result.entry_time.isoformat() if result.entry_time else None,
                    'exit_time': result.exit_time.isoformat() if result.exit_time else None
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting summary report: {e}")
            return []
    
    def _get_status_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get status-wise report"""
        try:
            query = db.session.query(
                GatePass.status,
                db.func.count(GatePass.id).label('count'),
                db.func.avg(db.func.julianday(GatePass.exit_time) - db.func.julianday(GatePass.entry_time)).label('avg_duration')
            ).group_by(GatePass.status)
            
            if filters:
                if filters.get('date_from'):
                    query = query.filter(GatePass.gate_pass_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(GatePass.gate_pass_date <= filters['date_to'])
            
            results = query.all()
            return [
                {
                    'status': result.status,
                    'count': result.count,
                    'avg_duration_hours': round(result.avg_duration * 24, 2) if result.avg_duration else 0
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting status-wise report: {e}")
            return []
    
    def _get_party_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get party-wise report"""
        try:
            query = db.session.query(
                GatePass.party_cd,
                db.func.count(GatePass.id).label('count'),
                db.func.sum(GatePass.quantity).label('total_quantity'),
                db.func.sum(GatePass.weight).label('total_weight')
            ).group_by(GatePass.party_cd)
            
            if filters:
                if filters.get('status'):
                    query = query.filter(GatePass.status == filters['status'])
                if filters.get('date_from'):
                    query = query.filter(GatePass.gate_pass_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(GatePass.gate_pass_date <= filters['date_to'])
            
            results = query.all()
            return [
                {
                    'party_cd': result.party_cd,
                    'count': result.count,
                    'total_quantity': result.total_quantity or 0,
                    'total_weight': result.total_weight or 0
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting party-wise report: {e}")
            return []
    
    def _get_vehicle_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get vehicle-wise report"""
        try:
            query = db.session.query(
                GatePass.vehicle_no,
                db.func.count(GatePass.id).label('count'),
                db.func.avg(db.func.julianday(GatePass.exit_time) - db.func.julianday(GatePass.entry_time)).label('avg_duration')
            ).group_by(GatePass.vehicle_no)
            
            if filters:
                if filters.get('status'):
                    query = query.filter(GatePass.status == filters['status'])
                if filters.get('date_from'):
                    query = query.filter(GatePass.gate_pass_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(GatePass.gate_pass_date <= filters['date_to'])
            
            results = query.all()
            return [
                {
                    'vehicle_no': result.vehicle_no or 'Unknown',
                    'count': result.count,
                    'avg_duration_hours': round(result.avg_duration * 24, 2) if result.avg_duration else 0
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting vehicle-wise report: {e}")
            return []
    
    def validate_gate_pass_data(self, gate_pass_data: Dict) -> Tuple[bool, str]:
        """Validate gate pass data"""
        try:
            # Check required fields
            if not gate_pass_data.get('gate_pass_no'):
                return False, "Gate pass number is required"
            
            if not gate_pass_data.get('gate_pass_date'):
                return False, "Gate pass date is required"
            
            if not gate_pass_data.get('party_cd'):
                return False, "Party code is required"
            
            # Check if gate pass number already exists (for new entries)
            if 'id' not in gate_pass_data:
                existing = GatePass.query.filter_by(gate_pass_no=gate_pass_data['gate_pass_no']).first()
                if existing:
                    return False, "Gate pass number already exists"
            
            # Validate date format
            try:
                datetime.strptime(gate_pass_data['gate_pass_date'], '%Y-%m-%d')
            except ValueError:
                return False, "Invalid date format. Use YYYY-MM-DD"
            
            # Validate time formats if provided
            if gate_pass_data.get('entry_time'):
                try:
                    datetime.strptime(gate_pass_data['entry_time'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return False, "Invalid entry time format. Use YYYY-MM-DD HH:MM:SS"
            
            if gate_pass_data.get('exit_time'):
                try:
                    datetime.strptime(gate_pass_data['exit_time'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return False, "Invalid exit time format. Use YYYY-MM-DD HH:MM:SS"
            
            return True, "Data is valid"
            
        except Exception as e:
            self.logger.error(f"Error validating gate pass data: {e}")
            return False, f"Validation error: {str(e)}"
    
    def get_next_gate_pass_number(self) -> int:
        """Get next available gate pass number"""
        try:
            last_pass = GatePass.query.order_by(GatePass.gate_pass_no.desc()).first()
            return (last_pass.gate_pass_no + 1) if last_pass else 1
        except Exception as e:
            self.logger.error(f"Error getting next gate pass number: {e}")
            return 1
    
    def _gate_pass_to_dict(self, gate_pass: GatePass) -> Dict:
        """Convert gate pass object to dictionary"""
        if not gate_pass:
            return {}
        
        return {
            'id': gate_pass.id,
            'gate_pass_no': gate_pass.gate_pass_no,
            'gate_pass_date': gate_pass.gate_pass_date.isoformat() if gate_pass.gate_pass_date else None,
            'party_cd': gate_pass.party_cd,
            'vehicle_no': gate_pass.vehicle_no,
            'driver_name': gate_pass.driver_name,
            'license_no': gate_pass.license_no,
            'purpose': gate_pass.purpose,
            'items_description': gate_pass.items_description,
            'quantity': gate_pass.quantity,
            'weight': gate_pass.weight,
            'entry_time': gate_pass.entry_time.isoformat() if gate_pass.entry_time else None,
            'exit_time': gate_pass.exit_time.isoformat() if gate_pass.exit_time else None,
            'status': gate_pass.status,
            'authorized_by': gate_pass.authorized_by,
            'remarks': gate_pass.remarks,
            'created_date': gate_pass.created_date.isoformat() if gate_pass.created_date else None
        } 