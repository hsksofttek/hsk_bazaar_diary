#!/usr/bin/env python3
"""
Schedule Management System
Payment and delivery schedule management with reminders
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database import db
from models import Schedule, Party, Sale, Purchase
import json
import logging

class ScheduleManagementSystem:
    """Comprehensive Schedule Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_schedule(self, schedule_data: Dict) -> Tuple[bool, str]:
        """Create new schedule"""
        try:
            # Validate required fields
            required_fields = ['schedule_type', 'due_date', 'amount', 'party_cd']
            for field in required_fields:
                if not schedule_data.get(field):
                    return False, f"{field.replace('_', ' ').title()} is required"
            
            # Create new schedule
            schedule = Schedule(
                schedule_type=schedule_data['schedule_type'],  # PAYMENT, DELIVERY, REMINDER
                due_date=datetime.strptime(schedule_data['due_date'], '%Y-%m-%d').date(),
                amount=float(schedule_data['amount']),
                party_cd=schedule_data['party_cd'],
                description=schedule_data.get('description', ''),
                reference_no=schedule_data.get('reference_no', ''),
                sale_id=schedule_data.get('sale_id'),
                purchase_id=schedule_data.get('purchase_id'),
                status=schedule_data.get('status', 'PENDING'),  # PENDING, COMPLETED, OVERDUE, CANCELLED
                priority=schedule_data.get('priority', 'MEDIUM'),  # LOW, MEDIUM, HIGH, URGENT
                reminder_days=schedule_data.get('reminder_days', 7),
                remarks=schedule_data.get('remarks', '')
            )
            
            db.session.add(schedule)
            db.session.commit()
            
            return True, "Schedule created successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating schedule: {e}")
            return False, f"Error creating schedule: {str(e)}"
    
    def update_schedule(self, schedule_id: int, schedule_data: Dict) -> Tuple[bool, str]:
        """Update existing schedule"""
        try:
            schedule = Schedule.query.get(schedule_id)
            if not schedule:
                return False, "Schedule not found"
            
            # Update fields
            for key, value in schedule_data.items():
                if hasattr(schedule, key):
                    if key in ['due_date'] and value:
                        setattr(schedule, key, datetime.strptime(value, '%Y-%m-%d').date())
                    elif key in ['amount', 'reminder_days']:
                        setattr(schedule, key, float(value))
                    else:
                        setattr(schedule, key, value)
            
            db.session.commit()
            return True, "Schedule updated successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating schedule: {e}")
            return False, f"Error updating schedule: {str(e)}"
    
    def delete_schedule(self, schedule_id: int) -> Tuple[bool, str]:
        """Delete schedule"""
        try:
            schedule = Schedule.query.get(schedule_id)
            if not schedule:
                return False, "Schedule not found"
            
            db.session.delete(schedule)
            db.session.commit()
            return True, "Schedule deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error deleting schedule: {e}")
            return False, f"Error deleting schedule: {str(e)}"
    
    def get_schedules(self, filters: Dict = None) -> List[Dict]:
        """Get schedules with optional filters"""
        try:
            query = Schedule.query.join(Party)
            
            if filters:
                if filters.get('status'):
                    query = query.filter(Schedule.status == filters['status'])
                if filters.get('schedule_type'):
                    query = query.filter(Schedule.schedule_type == filters['schedule_type'])
                if filters.get('party_cd'):
                    query = query.filter(Schedule.party_cd == filters['party_cd'])
                if filters.get('priority'):
                    query = query.filter(Schedule.priority == filters['priority'])
                if filters.get('date_from'):
                    query = query.filter(Schedule.due_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(Schedule.due_date <= filters['date_to'])
            
            schedules = query.order_by(Schedule.due_date).all()
            return [self._schedule_to_dict(schedule) for schedule in schedules]
            
        except Exception as e:
            self.logger.error(f"Error getting schedules: {e}")
            return []
    
    def get_schedule_by_id(self, schedule_id: int) -> Optional[Dict]:
        """Get schedule by ID"""
        try:
            schedule = Schedule.query.get(schedule_id)
            return self._schedule_to_dict(schedule) if schedule else None
        except Exception as e:
            self.logger.error(f"Error getting schedule by ID: {e}")
            return None
    
    def get_overdue_schedules(self) -> List[Dict]:
        """Get overdue schedules"""
        try:
            today = datetime.now().date()
            overdue_schedules = Schedule.query.filter(
                Schedule.due_date < today,
                Schedule.status.in_(['PENDING', 'REMINDED'])
            ).join(Party).order_by(Schedule.due_date).all()
            
            return [self._schedule_to_dict(schedule) for schedule in overdue_schedules]
            
        except Exception as e:
            self.logger.error(f"Error getting overdue schedules: {e}")
            return []
    
    def get_upcoming_schedules(self, days: int = 7) -> List[Dict]:
        """Get upcoming schedules within specified days"""
        try:
            today = datetime.now().date()
            end_date = today + timedelta(days=days)
            
            upcoming_schedules = Schedule.query.filter(
                Schedule.due_date >= today,
                Schedule.due_date <= end_date,
                Schedule.status.in_(['PENDING', 'REMINDED'])
            ).join(Party).order_by(Schedule.due_date).all()
            
            return [self._schedule_to_dict(schedule) for schedule in upcoming_schedules]
            
        except Exception as e:
            self.logger.error(f"Error getting upcoming schedules: {e}")
            return []
    
    def mark_schedule_completed(self, schedule_id: int) -> Tuple[bool, str]:
        """Mark schedule as completed"""
        try:
            schedule = Schedule.query.get(schedule_id)
            if not schedule:
                return False, "Schedule not found"
            
            schedule.status = 'COMPLETED'
            schedule.completed_date = datetime.now()
            db.session.commit()
            
            return True, "Schedule marked as completed"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error marking schedule completed: {e}")
            return False, f"Error marking schedule completed: {str(e)}"
    
    def get_schedule_statistics(self) -> Dict:
        """Get schedule statistics"""
        try:
            total_schedules = Schedule.query.count()
            pending_schedules = Schedule.query.filter_by(status='PENDING').count()
            completed_schedules = Schedule.query.filter_by(status='COMPLETED').count()
            overdue_schedules = Schedule.query.filter(
                Schedule.due_date < datetime.now().date(),
                Schedule.status.in_(['PENDING', 'REMINDED'])
            ).count()
            
            # Get schedules by type
            type_stats = db.session.query(
                Schedule.schedule_type,
                db.func.count(Schedule.id).label('count'),
                db.func.sum(Schedule.amount).label('total_amount')
            ).group_by(Schedule.schedule_type).all()
            
            # Get schedules by priority
            priority_stats = db.session.query(
                Schedule.priority,
                db.func.count(Schedule.id).label('count')
            ).group_by(Schedule.priority).all()
            
            # Get schedules by status
            status_stats = db.session.query(
                Schedule.status,
                db.func.count(Schedule.id).label('count')
            ).group_by(Schedule.status).all()
            
            # Get total amount by status
            amount_by_status = db.session.query(
                Schedule.status,
                db.func.sum(Schedule.amount).label('total_amount')
            ).group_by(Schedule.status).all()
            
            return {
                'total_schedules': total_schedules,
                'pending_schedules': pending_schedules,
                'completed_schedules': completed_schedules,
                'overdue_schedules': overdue_schedules,
                'type_distribution': [
                    {
                        'type': stat.schedule_type,
                        'count': stat.count,
                        'total_amount': stat.total_amount or 0
                    } for stat in type_stats
                ],
                'priority_distribution': [
                    {
                        'priority': stat.priority,
                        'count': stat.count
                    } for stat in priority_stats
                ],
                'status_distribution': [
                    {
                        'status': stat.status,
                        'count': stat.count
                    } for stat in status_stats
                ],
                'amount_by_status': [
                    {
                        'status': stat.status,
                        'total_amount': stat.total_amount or 0
                    } for stat in amount_by_status
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting schedule statistics: {e}")
            return {}
    
    def get_schedule_reports(self, report_type: str, filters: Dict = None) -> List[Dict]:
        """Get schedule reports"""
        try:
            if report_type == 'summary':
                return self._get_summary_report(filters)
            elif report_type == 'overdue':
                return self._get_overdue_report(filters)
            elif report_type == 'upcoming':
                return self._get_upcoming_report(filters)
            elif report_type == 'party_wise':
                return self._get_party_wise_report(filters)
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting schedule reports: {e}")
            return []
    
    def _get_summary_report(self, filters: Dict = None) -> List[Dict]:
        """Get summary report"""
        try:
            query = """
                SELECT 
                    s.id,
                    s.schedule_type,
                    s.due_date,
                    s.amount,
                    s.party_cd,
                    p.party_nm,
                    s.description,
                    s.reference_no,
                    s.status,
                    s.priority,
                    s.reminder_days,
                    DATEDIFF(s.due_date, CURRENT_DATE) as days_remaining
                FROM schedules s
                LEFT JOIN parties p ON s.party_cd = p.party_cd
            """
            
            where_clause = "WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('status'):
                    where_clause += " AND s.status = ?"
                    params.append(filters['status'])
                if filters.get('schedule_type'):
                    where_clause += " AND s.schedule_type = ?"
                    params.append(filters['schedule_type'])
                if filters.get('party_cd'):
                    where_clause += " AND s.party_cd = ?"
                    params.append(filters['party_cd'])
                if filters.get('date_from'):
                    where_clause += " AND s.due_date >= ?"
                    params.append(filters['date_from'])
                if filters.get('date_to'):
                    where_clause += " AND s.due_date <= ?"
                    params.append(filters['date_to'])
            
            query += f" {where_clause} ORDER BY s.due_date"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'id': result.id,
                    'schedule_type': result.schedule_type,
                    'due_date': result.due_date.isoformat() if result.due_date else None,
                    'amount': result.amount,
                    'party_cd': result.party_cd,
                    'party_nm': result.party_nm,
                    'description': result.description,
                    'reference_no': result.reference_no,
                    'status': result.status,
                    'priority': result.priority,
                    'reminder_days': result.reminder_days,
                    'days_remaining': result.days_remaining
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting summary report: {e}")
            return []
    
    def _get_overdue_report(self, filters: Dict = None) -> List[Dict]:
        """Get overdue report"""
        try:
            query = """
                SELECT 
                    s.id,
                    s.schedule_type,
                    s.due_date,
                    s.amount,
                    s.party_cd,
                    p.party_nm,
                    s.description,
                    s.reference_no,
                    s.status,
                    s.priority,
                    DATEDIFF(CURRENT_DATE, s.due_date) as days_overdue
                FROM schedules s
                LEFT JOIN parties p ON s.party_cd = p.party_cd
                WHERE s.due_date < CURRENT_DATE AND s.status IN ('PENDING', 'REMINDED')
            """
            
            params = []
            
            if filters:
                if filters.get('schedule_type'):
                    query += " AND s.schedule_type = ?"
                    params.append(filters['schedule_type'])
                if filters.get('party_cd'):
                    query += " AND s.party_cd = ?"
                    params.append(filters['party_cd'])
            
            query += " ORDER BY s.due_date"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'id': result.id,
                    'schedule_type': result.schedule_type,
                    'due_date': result.due_date.isoformat() if result.due_date else None,
                    'amount': result.amount,
                    'party_cd': result.party_cd,
                    'party_nm': result.party_nm,
                    'description': result.description,
                    'reference_no': result.reference_no,
                    'status': result.status,
                    'priority': result.priority,
                    'days_overdue': result.days_overdue
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting overdue report: {e}")
            return []
    
    def _get_upcoming_report(self, filters: Dict = None) -> List[Dict]:
        """Get upcoming report"""
        try:
            days = filters.get('days', 7) if filters else 7
            query = f"""
                SELECT 
                    s.id,
                    s.schedule_type,
                    s.due_date,
                    s.amount,
                    s.party_cd,
                    p.party_nm,
                    s.description,
                    s.reference_no,
                    s.status,
                    s.priority,
                    DATEDIFF(s.due_date, CURRENT_DATE) as days_remaining
                FROM schedules s
                LEFT JOIN parties p ON s.party_cd = p.party_cd
                WHERE s.due_date >= CURRENT_DATE 
                AND s.due_date <= DATE_ADD(CURRENT_DATE, INTERVAL {days} DAY)
                AND s.status IN ('PENDING', 'REMINDED')
            """
            
            params = []
            
            if filters:
                if filters.get('schedule_type'):
                    query += " AND s.schedule_type = ?"
                    params.append(filters['schedule_type'])
                if filters.get('party_cd'):
                    query += " AND s.party_cd = ?"
                    params.append(filters['party_cd'])
            
            query += " ORDER BY s.due_date"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'id': result.id,
                    'schedule_type': result.schedule_type,
                    'due_date': result.due_date.isoformat() if result.due_date else None,
                    'amount': result.amount,
                    'party_cd': result.party_cd,
                    'party_nm': result.party_nm,
                    'description': result.description,
                    'reference_no': result.reference_no,
                    'status': result.status,
                    'priority': result.priority,
                    'days_remaining': result.days_remaining
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting upcoming report: {e}")
            return []
    
    def _get_party_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get party-wise report"""
        try:
            query = """
                SELECT 
                    s.party_cd,
                    p.party_nm,
                    COUNT(s.id) as total_schedules,
                    SUM(s.amount) as total_amount,
                    COUNT(CASE WHEN s.status = 'PENDING' THEN 1 END) as pending_count,
                    COUNT(CASE WHEN s.status = 'COMPLETED' THEN 1 END) as completed_count,
                    COUNT(CASE WHEN s.due_date < CURRENT_DATE AND s.status IN ('PENDING', 'REMINDED') THEN 1 END) as overdue_count
                FROM schedules s
                LEFT JOIN parties p ON s.party_cd = p.party_cd
            """
            
            where_clause = "WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('schedule_type'):
                    where_clause += " AND s.schedule_type = ?"
                    params.append(filters['schedule_type'])
                if filters.get('status'):
                    where_clause += " AND s.status = ?"
                    params.append(filters['status'])
            
            query += f" {where_clause} GROUP BY s.party_cd, p.party_nm ORDER BY total_amount DESC"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'party_cd': result.party_cd,
                    'party_nm': result.party_nm,
                    'total_schedules': result.total_schedules,
                    'total_amount': result.total_amount or 0,
                    'pending_count': result.pending_count,
                    'completed_count': result.completed_count,
                    'overdue_count': result.overdue_count
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting party-wise report: {e}")
            return []
    
    def validate_schedule_data(self, schedule_data: Dict) -> Tuple[bool, str]:
        """Validate schedule data"""
        try:
            # Check required fields
            if not schedule_data.get('schedule_type'):
                return False, "Schedule type is required"
            
            if not schedule_data.get('due_date'):
                return False, "Due date is required"
            
            if not schedule_data.get('amount'):
                return False, "Amount is required"
            
            if not schedule_data.get('party_cd'):
                return False, "Party is required"
            
            # Validate schedule type
            if schedule_data['schedule_type'] not in ['PAYMENT', 'DELIVERY', 'REMINDER']:
                return False, "Schedule type must be PAYMENT, DELIVERY, or REMINDER"
            
            # Validate amount
            try:
                amount = float(schedule_data['amount'])
                if amount <= 0:
                    return False, "Amount must be greater than 0"
            except ValueError:
                return False, "Invalid amount"
            
            # Validate date format
            try:
                datetime.strptime(schedule_data['due_date'], '%Y-%m-%d')
            except ValueError:
                return False, "Invalid date format. Use YYYY-MM-DD"
            
            # Validate priority
            if schedule_data.get('priority') and schedule_data['priority'] not in ['LOW', 'MEDIUM', 'HIGH', 'URGENT']:
                return False, "Priority must be LOW, MEDIUM, HIGH, or URGENT"
            
            return True, "Data is valid"
            
        except Exception as e:
            self.logger.error(f"Error validating schedule data: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _schedule_to_dict(self, schedule: Schedule) -> Dict:
        """Convert schedule object to dictionary"""
        if not schedule:
            return {}
        
        return {
            'id': schedule.id,
            'schedule_type': schedule.schedule_type,
            'due_date': schedule.due_date.isoformat() if schedule.due_date else None,
            'amount': schedule.amount,
            'party_cd': schedule.party_cd,
            'description': schedule.description,
            'reference_no': schedule.reference_no,
            'sale_id': schedule.sale_id,
            'purchase_id': schedule.purchase_id,
            'status': schedule.status,
            'priority': schedule.priority,
            'reminder_days': schedule.reminder_days,
            'remarks': schedule.remarks,
            'created_date': schedule.created_date.isoformat() if schedule.created_date else None,
            'completed_date': schedule.completed_date.isoformat() if schedule.completed_date else None
        } 