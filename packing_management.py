#!/usr/bin/env python3
"""
Packing Management System
Comprehensive packing material and charge management
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database import db
from models import Packing, Item, Party
import json
import logging

class PackingManagementSystem:
    """Comprehensive Packing Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_packing_entry(self, packing_data: Dict) -> Tuple[bool, str]:
        """Create new packing entry"""
        try:
            # Validate required fields
            required_fields = ['bill_no', 'it_cd', 'packing_desc', 'qty']
            for field in required_fields:
                if not packing_data.get(field):
                    return False, f"{field.replace('_', ' ').title()} is required"
            
            # Create new packing entry
            packing = Packing(
                bill_no=packing_data['bill_no'],
                it_cd=packing_data['it_cd'],
                packing_desc=packing_data['packing_desc'],
                qty=float(packing_data['qty']),
                mrp=float(packing_data.get('mrp', 0)),
                sprc=float(packing_data.get('sprc', 0)),
                pkt=float(packing_data.get('pkt', 0)),
                bnd_dtl1=packing_data.get('bnd_dtl1', ''),
                bnd_dtl2=packing_data.get('bnd_dtl2', ''),
                cat_cd=packing_data.get('cat_cd', ''),
                maxrt=float(packing_data.get('maxrt', 0)),
                minrt=float(packing_data.get('minrt', 0)),
                taxpr=float(packing_data.get('taxpr', 0)),
                hamrt=float(packing_data.get('hamrt', 0)),
                itwt=float(packing_data.get('itwt', 0)),
                ccess=int(packing_data.get('ccess', 0))
            )
            
            db.session.add(packing)
            db.session.commit()
            
            return True, "Packing entry created successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating packing entry: {e}")
            return False, f"Error creating packing entry: {str(e)}"
    
    def update_packing_entry(self, packing_id: int, packing_data: Dict) -> Tuple[bool, str]:
        """Update existing packing entry"""
        try:
            packing = Packing.query.get(packing_id)
            if not packing:
                return False, "Packing entry not found"
            
            # Update fields
            for key, value in packing_data.items():
                if hasattr(packing, key):
                    if key in ['qty', 'mrp', 'sprc', 'pkt', 'maxrt', 'minrt', 'taxpr', 'hamrt', 'itwt']:
                        setattr(packing, key, float(value))
                    elif key == 'ccess':
                        setattr(packing, key, int(value))
                    else:
                        setattr(packing, key, value)
            
            db.session.commit()
            return True, "Packing entry updated successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating packing entry: {e}")
            return False, f"Error updating packing entry: {str(e)}"
    
    def delete_packing_entry(self, packing_id: int) -> Tuple[bool, str]:
        """Delete packing entry"""
        try:
            packing = Packing.query.get(packing_id)
            if not packing:
                return False, "Packing entry not found"
            
            db.session.delete(packing)
            db.session.commit()
            return True, "Packing entry deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error deleting packing entry: {e}")
            return False, f"Error deleting packing entry: {str(e)}"
    
    def get_packing_entries(self, filters: Dict = None) -> List[Dict]:
        """Get packing entries with optional filters"""
        try:
            query = Packing.query
            
            if filters:
                if filters.get('bill_no'):
                    query = query.filter(Packing.bill_no == filters['bill_no'])
                if filters.get('it_cd'):
                    query = query.filter(Packing.it_cd == filters['it_cd'])
                if filters.get('cat_cd'):
                    query = query.filter(Packing.cat_cd == filters['cat_cd'])
                if filters.get('date_from'):
                    query = query.filter(Packing.created_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(Packing.created_date <= filters['date_to'])
            
            packings = query.all()
            return [self._packing_to_dict(packing) for packing in packings]
            
        except Exception as e:
            self.logger.error(f"Error getting packing entries: {e}")
            return []
    
    def get_packing_by_id(self, packing_id: int) -> Optional[Dict]:
        """Get packing entry by ID"""
        try:
            packing = Packing.query.get(packing_id)
            return self._packing_to_dict(packing) if packing else None
        except Exception as e:
            self.logger.error(f"Error getting packing by ID: {e}")
            return None
    
    def get_packing_by_bill(self, bill_no: int) -> List[Dict]:
        """Get packing entries by bill number"""
        try:
            packings = Packing.query.filter_by(bill_no=bill_no).all()
            return [self._packing_to_dict(packing) for packing in packings]
        except Exception as e:
            self.logger.error(f"Error getting packing by bill: {e}")
            return []
    
    def get_packing_by_item(self, it_cd: str) -> List[Dict]:
        """Get packing entries by item code"""
        try:
            packings = Packing.query.filter_by(it_cd=it_cd).all()
            return [self._packing_to_dict(packing) for packing in packings]
        except Exception as e:
            self.logger.error(f"Error getting packing by item: {e}")
            return []
    
    def calculate_packing_charges(self, packing_data: Dict) -> Dict:
        """Calculate packing charges for given data"""
        try:
            qty = float(packing_data.get('qty', 0))
            mrp = float(packing_data.get('mrp', 0))
            sprc = float(packing_data.get('sprc', 0))
            pkt = float(packing_data.get('pkt', 0))
            taxpr = float(packing_data.get('taxpr', 0))
            hamrt = float(packing_data.get('hamrt', 0))
            ccess = int(packing_data.get('ccess', 0))
            
            # Calculate charges
            basic_amount = qty * sprc
            mrp_amount = qty * mrp
            pkt_amount = qty * pkt
            tax_amount = (basic_amount * taxpr) / 100
            hamali_amount = qty * hamrt
            cess_amount = (basic_amount * ccess) / 100
            
            total_amount = basic_amount + tax_amount + hamali_amount + cess_amount
            
            return {
                'basic_amount': round(basic_amount, 2),
                'mrp_amount': round(mrp_amount, 2),
                'pkt_amount': round(pkt_amount, 2),
                'tax_amount': round(tax_amount, 2),
                'hamali_amount': round(hamali_amount, 2),
                'cess_amount': round(cess_amount, 2),
                'total_amount': round(total_amount, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating packing charges: {e}")
            return {}
    
    def get_packing_statistics(self) -> Dict:
        """Get packing statistics"""
        try:
            total_entries = Packing.query.count()
            total_qty = db.session.query(db.func.sum(Packing.qty)).scalar() or 0
            total_value = db.session.query(db.func.sum(Packing.qty * Packing.sprc)).scalar() or 0
            
            # Get top items by packing quantity
            top_items = db.session.query(
                Packing.it_cd,
                db.func.sum(Packing.qty).label('total_qty'),
                db.func.sum(Packing.qty * Packing.sprc).label('total_value')
            ).group_by(Packing.it_cd).order_by(db.func.sum(Packing.qty).desc()).limit(10).all()
            
            # Get top categories
            top_categories = db.session.query(
                Packing.cat_cd,
                db.func.sum(Packing.qty).label('total_qty')
            ).group_by(Packing.cat_cd).order_by(db.func.sum(Packing.qty).desc()).limit(5).all()
            
            return {
                'total_entries': total_entries,
                'total_qty': round(total_qty, 2),
                'total_value': round(total_value, 2),
                'top_items': [
                    {
                        'it_cd': item.it_cd,
                        'total_qty': round(item.total_qty, 2),
                        'total_value': round(item.total_value, 2)
                    } for item in top_items
                ],
                'top_categories': [
                    {
                        'cat_cd': cat.cat_cd,
                        'total_qty': round(cat.total_qty, 2)
                    } for cat in top_categories
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting packing statistics: {e}")
            return {}
    
    def get_packing_reports(self, report_type: str, filters: Dict = None) -> List[Dict]:
        """Get packing reports"""
        try:
            if report_type == 'summary':
                return self._get_summary_report(filters)
            elif report_type == 'item_wise':
                return self._get_item_wise_report(filters)
            elif report_type == 'category_wise':
                return self._get_category_wise_report(filters)
            elif report_type == 'bill_wise':
                return self._get_bill_wise_report(filters)
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting packing reports: {e}")
            return []
    
    def _get_summary_report(self, filters: Dict = None) -> List[Dict]:
        """Get summary report"""
        try:
            query = db.session.query(
                Packing.it_cd,
                db.func.sum(Packing.qty).label('total_qty'),
                db.func.avg(Packing.sprc).label('avg_rate'),
                db.func.sum(Packing.qty * Packing.sprc).label('total_value'),
                db.func.count(Packing.id).label('entry_count')
            ).group_by(Packing.it_cd)
            
            if filters:
                if filters.get('date_from'):
                    query = query.filter(Packing.created_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(Packing.created_date <= filters['date_to'])
            
            results = query.all()
            return [
                {
                    'it_cd': result.it_cd,
                    'total_qty': round(result.total_qty, 2),
                    'avg_rate': round(result.avg_rate, 2),
                    'total_value': round(result.total_value, 2),
                    'entry_count': result.entry_count
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting summary report: {e}")
            return []
    
    def _get_item_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get item-wise report"""
        try:
            query = Packing.query
            if filters:
                if filters.get('it_cd'):
                    query = query.filter(Packing.it_cd == filters['it_cd'])
                if filters.get('date_from'):
                    query = query.filter(Packing.created_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(Packing.created_date <= filters['date_to'])
            
            packings = query.order_by(Packing.created_date.desc()).all()
            return [self._packing_to_dict(packing) for packing in packings]
            
        except Exception as e:
            self.logger.error(f"Error getting item-wise report: {e}")
            return []
    
    def _get_category_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get category-wise report"""
        try:
            query = db.session.query(
                Packing.cat_cd,
                db.func.sum(Packing.qty).label('total_qty'),
                db.func.sum(Packing.qty * Packing.sprc).label('total_value'),
                db.func.count(Packing.id).label('entry_count')
            ).group_by(Packing.cat_cd)
            
            if filters:
                if filters.get('date_from'):
                    query = query.filter(Packing.created_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(Packing.created_date <= filters['date_to'])
            
            results = query.all()
            return [
                {
                    'cat_cd': result.cat_cd,
                    'total_qty': round(result.total_qty, 2),
                    'total_value': round(result.total_value, 2),
                    'entry_count': result.entry_count
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting category-wise report: {e}")
            return []
    
    def _get_bill_wise_report(self, filters: Dict = None) -> List[Dict]:
        """Get bill-wise report"""
        try:
            query = db.session.query(
                Packing.bill_no,
                db.func.sum(Packing.qty).label('total_qty'),
                db.func.sum(Packing.qty * Packing.sprc).label('total_value'),
                db.func.count(Packing.id).label('entry_count')
            ).group_by(Packing.bill_no)
            
            if filters:
                if filters.get('bill_no'):
                    query = query.filter(Packing.bill_no == filters['bill_no'])
                if filters.get('date_from'):
                    query = query.filter(Packing.created_date >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(Packing.created_date <= filters['date_to'])
            
            results = query.all()
            return [
                {
                    'bill_no': result.bill_no,
                    'total_qty': round(result.total_qty, 2),
                    'total_value': round(result.total_value, 2),
                    'entry_count': result.entry_count
                } for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting bill-wise report: {e}")
            return []
    
    def _packing_to_dict(self, packing: Packing) -> Dict:
        """Convert packing object to dictionary"""
        if not packing:
            return {}
        
        return {
            'id': packing.id,
            'bill_no': packing.bill_no,
            'it_cd': packing.it_cd,
            'packing_desc': packing.packing_desc,
            'qty': packing.qty,
            'mrp': packing.mrp,
            'sprc': packing.sprc,
            'pkt': packing.pkt,
            'bnd_dtl1': packing.bnd_dtl1,
            'bnd_dtl2': packing.bnd_dtl2,
            'cat_cd': packing.cat_cd,
            'maxrt': packing.maxrt,
            'minrt': packing.minrt,
            'taxpr': packing.taxpr,
            'hamrt': packing.hamrt,
            'itwt': packing.itwt,
            'ccess': packing.ccess,
            'created_date': packing.created_date.isoformat() if packing.created_date else None
        }
    
    def validate_packing_data(self, packing_data: Dict) -> Tuple[bool, str]:
        """Validate packing data"""
        try:
            # Check required fields
            if not packing_data.get('bill_no'):
                return False, "Bill number is required"
            
            if not packing_data.get('it_cd'):
                return False, "Item code is required"
            
            if not packing_data.get('packing_desc'):
                return False, "Packing description is required"
            
            if not packing_data.get('qty') or float(packing_data['qty']) <= 0:
                return False, "Quantity must be greater than 0"
            
            # Check if item exists
            item = Item.query.filter_by(it_cd=packing_data['it_cd']).first()
            if not item:
                return False, "Item not found"
            
            return True, "Data is valid"
            
        except Exception as e:
            self.logger.error(f"Error validating packing data: {e}")
            return False, f"Validation error: {str(e)}"
    
    def get_packing_types(self) -> List[str]:
        """Get available packing types"""
        try:
            packing_types = db.session.query(Packing.packing_desc).distinct().all()
            return [pt[0] for pt in packing_types if pt[0]]
        except Exception as e:
            self.logger.error(f"Error getting packing types: {e}")
            return []
    
    def get_packing_categories(self) -> List[str]:
        """Get available packing categories"""
        try:
            categories = db.session.query(Packing.cat_cd).distinct().all()
            return [cat[0] for cat in categories if cat[0]]
        except Exception as e:
            self.logger.error(f"Error getting packing categories: {e}")
            return [] 