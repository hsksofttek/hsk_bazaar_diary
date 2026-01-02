#!/usr/bin/env python3
"""
Agent Management System
Sales agent management, commission tracking, and performance analytics
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database import db
from models import Agent, Party, Sale, Purchase
import json
import logging

class AgentManagementSystem:
    """Comprehensive Agent Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_agent(self, agent_data: Dict) -> Tuple[bool, str]:
        """Create new agent"""
        try:
            # Validate required fields
            required_fields = ['agent_cd', 'agent_nm']
            for field in required_fields:
                if not agent_data.get(field):
                    return False, f"{field.replace('_', ' ').title()} is required"
            
            # Check if agent code already exists
            existing = Agent.query.filter_by(agent_cd=agent_data['agent_cd']).first()
            if existing:
                return False, "Agent code already exists"
            
            # Create new agent
            agent = Agent(
                agent_cd=agent_data['agent_cd'],
                agent_nm=agent_data['agent_nm'],
                commission_rate=float(agent_data.get('commission_rate', 0)),
                phone=agent_data.get('phone', ''),
                address=agent_data.get('address', ''),
                email=agent_data.get('email', ''),
                mobile=agent_data.get('mobile', ''),
                gst_no=agent_data.get('gst_no', ''),
                pan_no=agent_data.get('pan_no', ''),
                bank_name=agent_data.get('bank_name', ''),
                account_no=agent_data.get('account_no', ''),
                ifsc_code=agent_data.get('ifsc_code', ''),
                status=agent_data.get('status', 'ACTIVE'),
                joining_date=datetime.strptime(agent_data['joining_date'], '%Y-%m-%d').date() if agent_data.get('joining_date') else None,
                remarks=agent_data.get('remarks', '')
            )
            
            db.session.add(agent)
            db.session.commit()
            
            return True, "Agent created successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating agent: {e}")
            return False, f"Error creating agent: {str(e)}"
    
    def update_agent(self, agent_cd: str, agent_data: Dict) -> Tuple[bool, str]:
        """Update existing agent"""
        try:
            agent = Agent.query.filter_by(agent_cd=agent_cd).first()
            if not agent:
                return False, "Agent not found"
            
            # Update fields
            for key, value in agent_data.items():
                if hasattr(agent, key):
                    if key in ['joining_date'] and value:
                        setattr(agent, key, datetime.strptime(value, '%Y-%m-%d').date())
                    elif key in ['commission_rate']:
                        setattr(agent, key, float(value))
                    else:
                        setattr(agent, key, value)
            
            db.session.commit()
            return True, "Agent updated successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating agent: {e}")
            return False, f"Error updating agent: {str(e)}"
    
    def delete_agent(self, agent_cd: str) -> Tuple[bool, str]:
        """Delete agent"""
        try:
            agent = Agent.query.filter_by(agent_cd=agent_cd).first()
            if not agent:
                return False, "Agent not found"
            
            # Check if agent has associated parties or transactions
            parties_count = Party.query.filter_by(agent_cd=agent_cd).count()
            sales_count = Sale.query.filter_by(agent_cd=agent_cd).count()
            
            if parties_count > 0 or sales_count > 0:
                return False, f"Cannot delete agent. Associated with {parties_count} parties and {sales_count} sales transactions"
            
            db.session.delete(agent)
            db.session.commit()
            return True, "Agent deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error deleting agent: {e}")
            return False, f"Error deleting agent: {str(e)}"
    
    def get_agents(self, filters: Dict = None) -> List[Dict]:
        """Get agents with optional filters"""
        try:
            query = Agent.query
            
            if filters:
                if filters.get('status'):
                    query = query.filter(Agent.status == filters['status'])
                if filters.get('agent_cd'):
                    query = query.filter(Agent.agent_cd.like(f"%{filters['agent_cd']}%"))
                if filters.get('agent_nm'):
                    query = query.filter(Agent.agent_nm.like(f"%{filters['agent_nm']}%"))
            
            agents = query.order_by(Agent.agent_nm).all()
            return [self._agent_to_dict(agent) for agent in agents]
            
        except Exception as e:
            self.logger.error(f"Error getting agents: {e}")
            return []
    
    def get_agent_by_code(self, agent_cd: str) -> Optional[Dict]:
        """Get agent by code"""
        try:
            agent = Agent.query.filter_by(agent_cd=agent_cd).first()
            return self._agent_to_dict(agent) if agent else None
        except Exception as e:
            self.logger.error(f"Error getting agent by code: {e}")
            return None
    
    def get_agent_performance(self, agent_cd: str, date_from: str = None, date_to: str = None) -> Dict:
        """Get agent performance statistics"""
        try:
            # Get agent details
            agent = Agent.query.filter_by(agent_cd=agent_cd).first()
            if not agent:
                return {}
            
            # Build date filters
            date_filter = ""
            params = [agent_cd]
            if date_from and date_to:
                date_filter = "AND s.bill_date BETWEEN ? AND ?"
                params.extend([date_from, date_to])
            
            # Get sales performance
            sales_query = f"""
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(s.sal_amt) as total_amount,
                    SUM(s.comm) as total_commission,
                    AVG(s.sal_amt) as avg_sale_amount,
                    COUNT(DISTINCT s.party_cd) as unique_customers
                FROM sales s
                WHERE s.agent_cd = ? {date_filter}
            """
            
            result = db.session.execute(sales_query, params).fetchone()
            
            # Get party count
            parties_count = Party.query.filter_by(agent_cd=agent_cd).count()
            
            # Get recent sales
            recent_sales_query = f"""
                SELECT s.bill_no, s.bill_date, s.party_cd, s.sal_amt, s.comm, p.party_nm
                FROM sales s
                LEFT JOIN parties p ON s.party_cd = p.party_cd
                WHERE s.agent_cd = ? {date_filter}
                ORDER BY s.bill_date DESC
                LIMIT 10
            """
            
            recent_sales = db.session.execute(recent_sales_query, params).fetchall()
            
            return {
                'agent_info': self._agent_to_dict(agent),
                'performance': {
                    'total_sales': result.total_sales or 0,
                    'total_amount': result.total_amount or 0,
                    'total_commission': result.total_commission or 0,
                    'avg_sale_amount': result.avg_sale_amount or 0,
                    'unique_customers': result.unique_customers or 0,
                    'parties_count': parties_count
                },
                'recent_sales': [
                    {
                        'bill_no': sale.bill_no,
                        'bill_date': sale.bill_date.isoformat() if sale.bill_date else None,
                        'party_cd': sale.party_cd,
                        'party_nm': sale.party_nm,
                        'amount': sale.sal_amt,
                        'commission': sale.comm
                    } for sale in recent_sales
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting agent performance: {e}")
            return {}
    
    def get_agent_statistics(self) -> Dict:
        """Get overall agent statistics"""
        try:
            total_agents = Agent.query.count()
            active_agents = Agent.query.filter_by(status='ACTIVE').count()
            inactive_agents = Agent.query.filter_by(status='INACTIVE').count()
            
            # Get top performing agents
            top_agents_query = """
                SELECT 
                    s.agent_cd,
                    a.agent_nm,
                    COUNT(*) as total_sales,
                    SUM(s.sal_amt) as total_amount,
                    SUM(s.comm) as total_commission
                FROM sales s
                LEFT JOIN agents a ON s.agent_cd = a.agent_cd
                WHERE s.agent_cd IS NOT NULL
                GROUP BY s.agent_cd, a.agent_nm
                ORDER BY total_amount DESC
                LIMIT 10
            """
            
            top_agents = db.session.execute(top_agents_query).fetchall()
            
            # Get commission statistics
            commission_stats_query = """
                SELECT 
                    AVG(commission_rate) as avg_commission_rate,
                    MIN(commission_rate) as min_commission_rate,
                    MAX(commission_rate) as max_commission_rate
                FROM agents
                WHERE status = 'ACTIVE'
            """
            
            commission_stats = db.session.execute(commission_stats_query).fetchone()
            
            # Get agents by status
            status_stats = db.session.query(
                Agent.status,
                db.func.count(Agent.agent_cd).label('count')
            ).group_by(Agent.status).all()
            
            return {
                'total_agents': total_agents,
                'active_agents': active_agents,
                'inactive_agents': inactive_agents,
                'top_performers': [
                    {
                        'agent_cd': agent.agent_cd,
                        'agent_nm': agent.agent_nm,
                        'total_sales': agent.total_sales,
                        'total_amount': agent.total_amount,
                        'total_commission': agent.total_commission
                    } for agent in top_agents
                ],
                'commission_stats': {
                    'avg_rate': commission_stats.avg_commission_rate or 0,
                    'min_rate': commission_stats.min_commission_rate or 0,
                    'max_rate': commission_stats.max_commission_rate or 0
                },
                'status_distribution': [
                    {
                        'status': stat.status,
                        'count': stat.count
                    } for stat in status_stats
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting agent statistics: {e}")
            return {}
    
    def get_agent_reports(self, report_type: str, filters: Dict = None) -> List[Dict]:
        """Get agent reports"""
        try:
            if report_type == 'performance':
                return self._get_performance_report(filters)
            elif report_type == 'commission':
                return self._get_commission_report(filters)
            elif report_type == 'customer_wise':
                return self._get_customer_wise_report(filters)
            elif report_type == 'monthly':
                return self._get_monthly_report(filters)
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting agent reports: {e}")
            return []
    
    def _get_performance_report(self, filters: Dict = None) -> List[Dict]:
        """Get performance report"""
        try:
            query = """
                SELECT 
                    a.agent_cd,
                    a.agent_nm,
                    a.commission_rate,
                    COUNT(s.id) as total_sales,
                    SUM(s.sal_amt) as total_amount,
                    SUM(s.comm) as total_commission,
                    AVG(s.sal_amt) as avg_sale_amount,
                    COUNT(DISTINCT s.party_cd) as unique_customers
                FROM agents a
                LEFT JOIN sales s ON a.agent_cd = s.agent_cd
            """
            
            where_clause = "WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('status'):
                    where_clause += " AND a.status = ?"
                    params.append(filters['status'])
                if filters.get('date_from'):
                    where_clause += " AND s.bill_date >= ?"
                    params.append(filters['date_from'])
                if filters.get('date_to'):
                    where_clause += " AND s.bill_date <= ?"
                    params.append(filters['date_to'])
            
            query += f" {where_clause} GROUP BY a.agent_cd, a.agent_nm, a.commission_rate ORDER BY total_amount DESC"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'agent_cd': result.agent_cd,
                    'agent_nm': result.agent_nm,
                    'commission_rate': result.commission_rate,
                    'total_sales': result.total_sales or 0,
                    'total_amount': result.total_amount or 0,
                    'total_commission': result.total_commission or 0,
                    'avg_sale_amount': result.avg_sale_amount or 0,
                    'unique_customers': result.unique_customers or 0
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting performance report: {e}")
            return []
    
    def _get_commission_report(self, filters: Dict = None) -> List[Dict]:
        """Get commission report"""
        try:
            query = """
                SELECT 
                    s.agent_cd,
                    a.agent_nm,
                    s.bill_no,
                    s.bill_date,
                    s.party_cd,
                    p.party_nm,
                    s.sal_amt,
                    s.comm,
                    (s.comm / s.sal_amt * 100) as commission_percentage
                FROM sales s
                LEFT JOIN agents a ON s.agent_cd = a.agent_cd
                LEFT JOIN parties p ON s.party_cd = p.party_cd
                WHERE s.agent_cd IS NOT NULL AND s.sal_amt > 0
            """
            
            where_clause = ""
            params = []
            
            if filters:
                if filters.get('agent_cd'):
                    where_clause += " AND s.agent_cd = ?"
                    params.append(filters['agent_cd'])
                if filters.get('date_from'):
                    where_clause += " AND s.bill_date >= ?"
                    params.append(filters['date_from'])
                if filters.get('date_to'):
                    where_clause += " AND s.bill_date <= ?"
                    params.append(filters['date_to'])
            
            query += f" {where_clause} ORDER BY s.bill_date DESC"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'agent_cd': result.agent_cd,
                    'agent_nm': result.agent_nm,
                    'bill_no': result.bill_no,
                    'bill_date': result.bill_date.isoformat() if result.bill_date else None,
                    'party_cd': result.party_cd,
                    'party_nm': result.party_nm,
                    'amount': result.sal_amt,
                    'commission': result.comm,
                    'commission_percentage': result.commission_percentage
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting commission report: {e}")
            return []
    
    def _get_customer_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get customer-wise agent report"""
        try:
            query = """
                SELECT 
                    s.agent_cd,
                    a.agent_nm,
                    s.party_cd,
                    p.party_nm,
                    COUNT(s.id) as total_sales,
                    SUM(s.sal_amt) as total_amount,
                    SUM(s.comm) as total_commission
                FROM sales s
                LEFT JOIN agents a ON s.agent_cd = a.agent_cd
                LEFT JOIN parties p ON s.party_cd = p.party_cd
                WHERE s.agent_cd IS NOT NULL
            """
            
            where_clause = ""
            params = []
            
            if filters:
                if filters.get('agent_cd'):
                    where_clause += " AND s.agent_cd = ?"
                    params.append(filters['agent_cd'])
                if filters.get('date_from'):
                    where_clause += " AND s.bill_date >= ?"
                    params.append(filters['date_from'])
                if filters.get('date_to'):
                    where_clause += " AND s.bill_date <= ?"
                    params.append(filters['date_to'])
            
            query += f" {where_clause} GROUP BY s.agent_cd, a.agent_nm, s.party_cd, p.party_nm ORDER BY total_amount DESC"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'agent_cd': result.agent_cd,
                    'agent_nm': result.agent_nm,
                    'party_cd': result.party_cd,
                    'party_nm': result.party_nm,
                    'total_sales': result.total_sales,
                    'total_amount': result.total_amount,
                    'total_commission': result.total_commission
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting customer-wise report: {e}")
            return []
    
    def _get_monthly_report(self, filters: Dict = None) -> List[Dict]:
        """Get monthly agent report"""
        try:
            query = """
                SELECT 
                    s.agent_cd,
                    a.agent_nm,
                    strftime('%Y-%m', s.bill_date) as month,
                    COUNT(s.id) as total_sales,
                    SUM(s.sal_amt) as total_amount,
                    SUM(s.comm) as total_commission
                FROM sales s
                LEFT JOIN agents a ON s.agent_cd = a.agent_cd
                WHERE s.agent_cd IS NOT NULL
            """
            
            where_clause = ""
            params = []
            
            if filters:
                if filters.get('agent_cd'):
                    where_clause += " AND s.agent_cd = ?"
                    params.append(filters['agent_cd'])
                if filters.get('year'):
                    where_clause += " AND strftime('%Y', s.bill_date) = ?"
                    params.append(filters['year'])
            
            query += f" {where_clause} GROUP BY s.agent_cd, a.agent_nm, month ORDER BY month DESC, total_amount DESC"
            
            results = db.session.execute(query, params).fetchall()
            
            return [
                {
                    'agent_cd': result.agent_cd,
                    'agent_nm': result.agent_nm,
                    'month': result.month,
                    'total_sales': result.total_sales,
                    'total_amount': result.total_amount,
                    'total_commission': result.total_commission
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting monthly report: {e}")
            return []
    
    def validate_agent_data(self, agent_data: Dict) -> Tuple[bool, str]:
        """Validate agent data"""
        try:
            # Check required fields
            if not agent_data.get('agent_cd'):
                return False, "Agent code is required"
            
            if not agent_data.get('agent_nm'):
                return False, "Agent name is required"
            
            # Check if agent code already exists (for new entries)
            if 'id' not in agent_data:
                existing = Agent.query.filter_by(agent_cd=agent_data['agent_cd']).first()
                if existing:
                    return False, "Agent code already exists"
            
            # Validate commission rate
            if agent_data.get('commission_rate'):
                try:
                    rate = float(agent_data['commission_rate'])
                    if rate < 0 or rate > 100:
                        return False, "Commission rate must be between 0 and 100"
                except ValueError:
                    return False, "Invalid commission rate"
            
            # Validate date format
            if agent_data.get('joining_date'):
                try:
                    datetime.strptime(agent_data['joining_date'], '%Y-%m-%d')
                except ValueError:
                    return False, "Invalid joining date format. Use YYYY-MM-DD"
            
            return True, "Data is valid"
            
        except Exception as e:
            self.logger.error(f"Error validating agent data: {e}")
            return False, f"Validation error: {str(e)}"
    
    def get_next_agent_code(self) -> str:
        """Get next available agent code"""
        try:
            last_agent = Agent.query.order_by(Agent.agent_cd.desc()).first()
            if last_agent:
                # Try to extract number from agent code
                try:
                    import re
                    match = re.search(r'(\d+)$', last_agent.agent_cd)
                    if match:
                        next_num = int(match.group(1)) + 1
                        return f"A{next_num:03d}"
                except:
                    pass
                return f"A{len(Agent.query.all()) + 1:03d}"
            return "A001"
        except Exception as e:
            self.logger.error(f"Error getting next agent code: {e}")
            return "A001"
    
    def _agent_to_dict(self, agent: Agent) -> Dict:
        """Convert agent object to dictionary"""
        if not agent:
            return {}
        
        return {
            'id': agent.id,
            'agent_cd': agent.agent_cd,
            'agent_nm': agent.agent_nm,
            'commission_rate': agent.commission_rate,
            'phone': agent.phone,
            'address': agent.address,
            'email': agent.email,
            'mobile': agent.mobile,
            'gst_no': agent.gst_no,
            'pan_no': agent.pan_no,
            'bank_name': agent.bank_name,
            'account_no': agent.account_no,
            'ifsc_code': agent.ifsc_code,
            'status': agent.status,
            'joining_date': agent.joining_date.isoformat() if agent.joining_date else None,
            'remarks': agent.remarks,
            'created_date': agent.created_date.isoformat() if agent.created_date else None,
            'modified_date': agent.modified_date.isoformat() if agent.modified_date else None
        } 