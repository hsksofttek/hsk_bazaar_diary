#!/usr/bin/env python3
"""
Narration Management System
Predefined narration templates and quick narration selection
"""

from datetime import datetime
from typing import List, Dict, Optional, Tuple
from database import db
from models import Narration
import json
import logging

class NarrationManagementSystem:
    """Comprehensive Narration Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_narration(self, narration_data: Dict) -> Tuple[bool, str]:
        """Create new narration template"""
        try:
            # Validate required fields
            required_fields = ['narration_text', 'category']
            for field in required_fields:
                if not narration_data.get(field):
                    return False, f"{field.replace('_', ' ').title()} is required"
            
            # Create new narration
            narration = Narration(
                narration_text=narration_data['narration_text'],
                category=narration_data['category'],
                description=narration_data.get('description', ''),
                is_active=narration_data.get('is_active', True),
                usage_count=narration_data.get('usage_count', 0),
                created_by=narration_data.get('created_by', 'system')
            )
            
            db.session.add(narration)
            db.session.commit()
            
            return True, "Narration template created successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating narration: {e}")
            return False, f"Error creating narration: {str(e)}"
    
    def update_narration(self, narration_id: int, narration_data: Dict) -> Tuple[bool, str]:
        """Update existing narration template"""
        try:
            narration = Narration.query.get(narration_id)
            if not narration:
                return False, "Narration template not found"
            
            # Update fields
            for key, value in narration_data.items():
                if hasattr(narration, key):
                    setattr(narration, key, value)
            
            db.session.commit()
            return True, "Narration template updated successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating narration: {e}")
            return False, f"Error updating narration: {str(e)}"
    
    def delete_narration(self, narration_id: int) -> Tuple[bool, str]:
        """Delete narration template"""
        try:
            narration = Narration.query.get(narration_id)
            if not narration:
                return False, "Narration template not found"
            
            db.session.delete(narration)
            db.session.commit()
            return True, "Narration template deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error deleting narration: {e}")
            return False, f"Error deleting narration: {str(e)}"
    
    def get_narrations(self, filters: Dict = None) -> List[Dict]:
        """Get narrations with optional filters"""
        try:
            query = Narration.query
            
            if filters:
                if filters.get('category'):
                    query = query.filter(Narration.category == filters['category'])
                if filters.get('is_active') is not None:
                    query = query.filter(Narration.is_active == filters['is_active'])
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        db.or_(
                            Narration.narration_text.like(search_term),
                            Narration.description.like(search_term),
                            Narration.category.like(search_term)
                        )
                    )
            
            narrations = query.order_by(Narration.usage_count.desc(), Narration.narration_text).all()
            return [self._narration_to_dict(narration) for narration in narrations]
            
        except Exception as e:
            self.logger.error(f"Error getting narrations: {e}")
            return []
    
    def get_narration_by_id(self, narration_id: int) -> Optional[Dict]:
        """Get narration by ID"""
        try:
            narration = Narration.query.get(narration_id)
            return self._narration_to_dict(narration) if narration else None
        except Exception as e:
            self.logger.error(f"Error getting narration by ID: {e}")
            return None
    
    def get_narrations_by_category(self, category: str) -> List[Dict]:
        """Get narrations by category"""
        try:
            narrations = Narration.query.filter_by(
                category=category,
                is_active=True
            ).order_by(Narration.usage_count.desc()).all()
            
            return [self._narration_to_dict(narration) for narration in narrations]
            
        except Exception as e:
            self.logger.error(f"Error getting narrations by category: {e}")
            return []
    
    def get_popular_narrations(self, limit: int = 10) -> List[Dict]:
        """Get most popular narrations"""
        try:
            narrations = Narration.query.filter_by(
                is_active=True
            ).order_by(Narration.usage_count.desc()).limit(limit).all()
            
            return [self._narration_to_dict(narration) for narration in narrations]
            
        except Exception as e:
            self.logger.error(f"Error getting popular narrations: {e}")
            return []
    
    def increment_usage_count(self, narration_id: int) -> Tuple[bool, str]:
        """Increment usage count for narration"""
        try:
            narration = Narration.query.get(narration_id)
            if not narration:
                return False, "Narration template not found"
            
            narration.usage_count += 1
            db.session.commit()
            
            return True, "Usage count incremented"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error incrementing usage count: {e}")
            return False, f"Error incrementing usage count: {str(e)}"
    
    def get_narration_categories(self) -> List[str]:
        """Get all narration categories"""
        try:
            categories = db.session.query(Narration.category).distinct().all()
            return [category[0] for category in categories if category[0]]
            
        except Exception as e:
            self.logger.error(f"Error getting narration categories: {e}")
            return []
    
    def get_narration_statistics(self) -> Dict:
        """Get narration statistics"""
        try:
            total_narrations = Narration.query.count()
            active_narrations = Narration.query.filter_by(is_active=True).count()
            inactive_narrations = Narration.query.filter_by(is_active=False).count()
            
            # Get narrations by category
            category_stats = db.session.query(
                Narration.category,
                db.func.count(Narration.id).label('count'),
                db.func.sum(Narration.usage_count).label('total_usage')
            ).group_by(Narration.category).all()
            
            # Get most used narrations
            most_used = Narration.query.order_by(
                Narration.usage_count.desc()
            ).limit(5).all()
            
            # Get recently created narrations
            recent_narrations = Narration.query.order_by(
                Narration.created_date.desc()
            ).limit(5).all()
            
            return {
                'total_narrations': total_narrations,
                'active_narrations': active_narrations,
                'inactive_narrations': inactive_narrations,
                'category_distribution': [
                    {
                        'category': stat.category,
                        'count': stat.count,
                        'total_usage': stat.total_usage or 0
                    } for stat in category_stats
                ],
                'most_used_narrations': [
                    self._narration_to_dict(narration) for narration in most_used
                ],
                'recent_narrations': [
                    self._narration_to_dict(narration) for narration in recent_narrations
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting narration statistics: {e}")
            return {}
    
    def search_narrations(self, search_term: str, category: str = None) -> List[Dict]:
        """Search narrations by text"""
        try:
            query = Narration.query.filter_by(is_active=True)
            
            if category:
                query = query.filter_by(category=category)
            
            if search_term:
                search_pattern = f"%{search_term}%"
                query = query.filter(
                    db.or_(
                        Narration.narration_text.like(search_pattern),
                        Narration.description.like(search_pattern)
                    )
                )
            
            narrations = query.order_by(Narration.usage_count.desc()).limit(20).all()
            return [self._narration_to_dict(narration) for narration in narrations]
            
        except Exception as e:
            self.logger.error(f"Error searching narrations: {e}")
            return []
    
    def get_quick_narrations(self) -> Dict[str, List[Dict]]:
        """Get quick narration templates organized by category"""
        try:
            categories = self.get_narration_categories()
            quick_narrations = {}
            
            for category in categories:
                narrations = self.get_narrations_by_category(category)
                quick_narrations[category] = narrations[:5]  # Limit to 5 per category
            
            return quick_narrations
            
        except Exception as e:
            self.logger.error(f"Error getting quick narrations: {e}")
            return {}
    
    def bulk_import_narrations(self, narrations_data: List[Dict]) -> Tuple[bool, str, Dict]:
        """Bulk import narration templates"""
        try:
            results = {
                'total': len(narrations_data),
                'success_count': 0,
                'error_count': 0,
                'errors': []
            }
            
            for narration_data in narrations_data:
                is_valid, message = self.validate_narration_data(narration_data)
                if is_valid:
                    success, msg = self.create_narration(narration_data)
                    if success:
                        results['success_count'] += 1
                    else:
                        results['error_count'] += 1
                        results['errors'].append({
                            'data': narration_data,
                            'error': msg
                        })
                else:
                    results['error_count'] += 1
                    results['errors'].append({
                        'data': narration_data,
                        'error': message
                    })
            
            return True, f"Import completed. {results['success_count']} successful, {results['error_count']} failed", results
            
        except Exception as e:
            self.logger.error(f"Error bulk importing narrations: {e}")
            return False, f"Error bulk importing narrations: {str(e)}", {}
    
    def export_narrations(self, filters: Dict = None) -> List[Dict]:
        """Export narrations for backup/transfer"""
        try:
            narrations = self.get_narrations(filters)
            
            export_data = []
            for narration in narrations:
                export_data.append({
                    'narration_text': narration['narration_text'],
                    'category': narration['category'],
                    'description': narration['description'],
                    'is_active': narration['is_active'],
                    'usage_count': narration['usage_count'],
                    'created_by': narration['created_by']
                })
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error exporting narrations: {e}")
            return []
    
    def validate_narration_data(self, narration_data: Dict) -> Tuple[bool, str]:
        """Validate narration data"""
        try:
            # Check required fields
            if not narration_data.get('narration_text'):
                return False, "Narration text is required"
            
            if not narration_data.get('category'):
                return False, "Category is required"
            
            # Validate text length
            if len(narration_data['narration_text']) > 500:
                return False, "Narration text is too long (max 500 characters)"
            
            # Validate category length
            if len(narration_data['category']) > 50:
                return False, "Category name is too long (max 50 characters)"
            
            return True, "Data is valid"
            
        except Exception as e:
            self.logger.error(f"Error validating narration data: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _narration_to_dict(self, narration: Narration) -> Dict:
        """Convert narration object to dictionary"""
        if not narration:
            return {}
        
        return {
            'id': narration.id,
            'narration_text': narration.narration_text,
            'category': narration.category,
            'description': narration.description,
            'is_active': narration.is_active,
            'usage_count': narration.usage_count,
            'created_by': narration.created_by,
            'created_date': narration.created_date.isoformat() if narration.created_date else None,
            'modified_date': narration.modified_date.isoformat() if narration.modified_date else None
        } 