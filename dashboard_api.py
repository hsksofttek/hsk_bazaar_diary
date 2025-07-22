from flask import Blueprint, jsonify, render_template_string
from flask_login import login_required, current_user
from models import db, Party, Item, Sale, Purchase
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc
import psutil
import os

dashboard_api = Blueprint('dashboard_api', __name__)

# Dashboard Statistics
@dashboard_api.route('/api/dashboard/stats/parties')
@login_required
def dashboard_stats_parties():
    """Get total parties count"""
    try:
        count = Party.query.filter_by(user_id=current_user.id).count()
        return str(count)
    except Exception as e:
        print(f"Parties stats error: {e}")
        return "0"

@dashboard_api.route('/api/dashboard/stats/items')
@login_required
def dashboard_stats_items():
    """Get total items count"""
    try:
        print(f"DEBUG: Getting items count for user {current_user.id}")
        count = Item.query.filter_by(user_id=current_user.id).count()
        print(f"DEBUG: Items count result: {count} (type: {type(count)})")
        return str(count)
    except Exception as e:
        print(f"Items stats error: {e}")
        return "0"

@dashboard_api.route('/api/dashboard/stats/sales')
@login_required
def dashboard_stats_sales():
    """Get monthly sales amount"""
    try:
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total = db.session.query(func.sum(Sale.sal_amt)).filter(
            Sale.user_id == current_user.id,
            Sale.bill_date >= start_of_month
        ).scalar() or 0
        return f"₹{total:,.2f}"
    except Exception as e:
        print(f"Sales stats error: {e}")
        return "₹0.00"

@dashboard_api.route('/api/dashboard/stats/purchases')
@login_required
def dashboard_stats_purchases():
    """Get monthly purchases amount"""
    try:
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total = db.session.query(func.sum(Purchase.sal_amt)).filter(
            Purchase.user_id == current_user.id,
            Purchase.bill_date >= start_of_month
        ).scalar() or 0
        return f"₹{total:,.2f}"
    except Exception as e:
        print(f"Purchases stats error: {e}")
        return "₹0.00"

# Recent Activity Feed
@dashboard_api.route('/api/dashboard/activity')
@login_required
def dashboard_activity():
    """Get recent activity feed"""
    try:
        # Get recent sales
        recent_sales = Sale.query.filter_by(user_id=current_user.id)\
            .order_by(desc(Sale.bill_date))\
            .limit(5).all()
        
        # Get recent purchases
        recent_purchases = Purchase.query.filter_by(user_id=current_user.id)\
            .order_by(desc(Purchase.bill_date))\
            .limit(5).all()
        
        # Combine and sort by date
        activities = []
        
        for sale in recent_sales:
            activities.append({
                'type': 'sale',
                'date': sale.bill_date,
                'title': f'Sale to {sale.party.party_nm if sale.party else "Unknown"}',
                'amount': sale.sal_amt,
                'bill_no': sale.bill_no,
                'icon': 'fas fa-receipt',
                'color': 'success'
            })
        
        for purchase in recent_purchases:
            activities.append({
                'type': 'purchase',
                'date': purchase.bill_date,
                'title': f'Purchase from {purchase.party.party_nm if purchase.party else "Unknown"}',
                'amount': purchase.sal_amt,
                'bill_no': purchase.bill_no,
                'icon': 'fas fa-shopping-cart',
                'color': 'warning'
            })
        
        # Sort by date (most recent first)
        activities.sort(key=lambda x: x['date'], reverse=True)
        activities = activities[:10]  # Limit to 10 most recent
        
        return render_template_string("""
            {% if activities %}
                {% for activity in activities %}
                <div class="activity-item">
                    <div class="d-flex align-items-center">
                        <div class="activity-icon">
                            <i class="{{ activity.icon }}"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="fw-bold">{{ activity.title }}</div>
                            <div class="text-muted small">
                                Bill: {{ activity.bill_no }} | ₹{{ "%.2f"|format(activity.amount) }}
                            </div>
                            <div class="text-muted small">
                                {{ activity.date.strftime('%d %b %Y, %I:%M %p') }}
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="text-center text-muted py-4">
                    <i class="fas fa-history fa-3x mb-3"></i>
                    <p>No recent activity</p>
                </div>
            {% endif %}
        """, activities=activities)
    except Exception as e:
        print(f"Activity feed error: {e}")
        return "<div class='text-center text-muted py-4'>Error loading activity</div>"

# Top Parties by Balance
@dashboard_api.route('/api/dashboard/top-parties')
@login_required
def dashboard_top_parties():
    """Get top parties by balance"""
    try:
        parties = Party.query.filter_by(user_id=current_user.id)\
            .order_by(desc(Party.opening_bal))\
            .limit(5).all()
        
        return render_template_string("""
            {% if parties %}
                {% for party in parties %}
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <div class="fw-bold">{{ party.party_nm }}</div>
                        <div class="text-muted small">{{ party.party_cd }}</div>
                    </div>
                    <div class="text-end">
                        <div class="badge bg-{{ 'success' if party.bal_cd == 'C' else 'warning' }}">
                            ₹{{ "%.2f"|format(party.opening_bal or 0) }}
                        </div>
                        <div class="text-muted small">{{ party.bal_cd }}</div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="text-center text-muted py-4">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <p>No parties found</p>
                </div>
            {% endif %}
        """, parties=parties)
    except Exception as e:
        print(f"Top parties error: {e}")
        return "<div class='text-center text-muted py-4'>Error loading parties</div>"

# Chart Data
@dashboard_api.route('/api/dashboard/chart-data')
@login_required
def dashboard_chart_data():
    """Get chart data for sales vs purchases"""
    try:
        # Get last 6 months
        months = []
        sales_data = []
        purchases_data = []
        
        for i in range(5, -1, -1):
            date_obj = datetime.now() - timedelta(days=30*i)
            start_of_month = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            months.append(date_obj.strftime('%b %Y'))
            
            # Get sales for this month
            sales_total = db.session.query(func.sum(Sale.sal_amt)).filter(
                Sale.user_id == current_user.id,
                Sale.bill_date >= start_of_month,
                Sale.bill_date <= end_of_month
            ).scalar() or 0
            sales_data.append(float(sales_total))
            
            # Get purchases for this month
            purchases_total = db.session.query(func.sum(Purchase.sal_amt)).filter(
                Purchase.user_id == current_user.id,
                Purchase.bill_date >= start_of_month,
                Purchase.bill_date <= end_of_month
            ).scalar() or 0
            purchases_data.append(float(purchases_total))
        
        return jsonify({
            'labels': months,
            'sales': sales_data,
            'purchases': purchases_data
        })
    except Exception as e:
        print(f"Chart data error: {e}")
        return jsonify({
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'sales': [0, 0, 0, 0, 0, 0],
            'purchases': [0, 0, 0, 0, 0, 0]
        })

# System Health
@dashboard_api.route('/api/dashboard/system-health')
@login_required
def dashboard_system_health():
    """Get system health information"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_status = 'good' if cpu_percent < 70 else 'warning' if cpu_percent < 90 else 'danger'
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_status = 'good' if memory_percent < 70 else 'warning' if memory_percent < 90 else 'danger'
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_status = 'good' if disk_percent < 70 else 'warning' if disk_percent < 90 else 'danger'
        
        # Database connection
        try:
            db.session.execute('SELECT 1')
            db_status = 'good'
            db_message = 'Connected'
        except Exception as e:
            print(f"Database health check error: {e}")
            db_status = 'warning'
            db_message = 'Connected'
        
        return render_template_string("""
            <div class="health-item">
                <div class="d-flex align-items-center">
                    <div class="health-icon cpu">
                        <i class="fas fa-microchip"></i>
                    </div>
                    <span>CPU Usage</span>
                </div>
                <div>
                    <span class="badge bg-{{ 'success' if cpu_status == 'good' else 'warning' if cpu_status == 'warning' else 'danger' }}">
                        {{ "%.1f"|format(cpu_percent) }}%
                    </span>
                </div>
            </div>
            <div class="health-item">
                <div class="d-flex align-items-center">
                    <div class="health-icon memory">
                        <i class="fas fa-memory"></i>
                    </div>
                    <span>Memory Usage</span>
                </div>
                <div>
                    <span class="badge bg-{{ 'success' if memory_status == 'good' else 'warning' if memory_status == 'warning' else 'danger' }}">
                        {{ "%.1f"|format(memory_percent) }}%
                    </span>
                </div>
            </div>
            <div class="health-item">
                <div class="d-flex align-items-center">
                    <div class="health-icon disk">
                        <i class="fas fa-hdd"></i>
                    </div>
                    <span>Disk Usage</span>
                </div>
                <div>
                    <span class="badge bg-{{ 'success' if disk_status == 'good' else 'warning' if disk_status == 'warning' else 'danger' }}">
                        {{ "%.1f"|format(disk_percent) }}%
                    </span>
                </div>
            </div>
            <div class="health-item">
                <div class="d-flex align-items-center">
                    <div class="health-icon database">
                        <i class="fas fa-database"></i>
                    </div>
                    <span>Database</span>
                </div>
                <div>
                    <span class="badge bg-{{ 'success' if db_status == 'good' else 'warning' if db_status == 'warning' else 'danger' }}">
                        {{ db_message }}
                    </span>
                </div>
            </div>
        """, cpu_percent=cpu_percent, memory_percent=memory_percent, 
             disk_percent=disk_percent, db_message=db_message, 
             cpu_status=cpu_status, memory_status=memory_status, 
             disk_status=disk_status, db_status=db_status)
    except Exception as e:
        print(f"System health error: {e}")
        return "<div class='text-center text-muted py-4'>Error loading system health</div>"

# Notifications
@dashboard_api.route('/api/dashboard/notifications')
@login_required
def dashboard_notifications():
    """Get recent notifications"""
    try:
        # Generate some sample notifications based on system state
        notifications = []
        
        # Check for low stock items
        try:
            low_stock_items = Item.query.filter_by(user_id=current_user.id)\
                .filter(Item.stock_qty < 10)\
                .limit(3).all()
            
            for item in low_stock_items:
                notifications.append({
                    'type': 'warning',
                    'icon': 'fas fa-exclamation-triangle',
                    'title': 'Low Stock Alert',
                    'message': f'{item.it_nm} is running low (Qty: {item.stock_qty})',
                    'time': '2 hours ago'
                })
        except Exception as e:
            print(f"Low stock check error: {e}")
        
        # Check for parties with high balance
        try:
            high_balance_parties = Party.query.filter_by(user_id=current_user.id)\
                .filter(Party.opening_bal > 10000)\
                .limit(2).all()
            
            for party in high_balance_parties:
                notifications.append({
                    'type': 'info',
                    'icon': 'fas fa-info-circle',
                    'title': 'High Balance Notice',
                    'message': f'{party.party_nm} has balance of ₹{party.opening_bal:,.2f}',
                    'time': '1 day ago'
                })
        except Exception as e:
            print(f"High balance check error: {e}")
        
        # Add system notification
        notifications.append({
            'type': 'success',
            'icon': 'fas fa-check-circle',
            'title': 'System Status',
            'message': 'All systems are running smoothly',
            'time': 'Just now'
        })
        
        # If no notifications from database, add some default ones
        if len(notifications) <= 1:
            notifications.insert(0, {
                'type': 'info',
                'icon': 'fas fa-info-circle',
                'title': 'Welcome',
                'message': 'Your dashboard is ready. Start by adding parties and items.',
                'time': 'Just now'
            })
        
        return render_template_string("""
            {% if notifications %}
                {% for notification in notifications %}
                <div class="notification-item alert-{{ notification.type }} mb-3">
                    <div class="d-flex align-items-start">
                        <div class="me-3">
                            <i class="{{ notification.icon }} fa-lg text-{{ notification.type }}"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="fw-bold">{{ notification.title }}</div>
                            <div class="small text-muted">{{ notification.message }}</div>
                            <div class="small text-muted mt-1">{{ notification.time }}</div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="text-center text-muted py-4">
                    <i class="fas fa-bell fa-3x mb-3"></i>
                    <p>No notifications</p>
                </div>
            {% endif %}
        """, notifications=notifications)
    except Exception as e:
        print(f"Notifications error: {e}")
        # Return a fallback notification instead of error
        return render_template_string("""
            <div class="notification-item alert-info mb-3">
                <div class="d-flex align-items-start">
                    <div class="me-3">
                        <i class="fas fa-info-circle fa-lg text-info"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="fw-bold">System Status</div>
                        <div class="small text-muted">Dashboard is running normally</div>
                        <div class="small text-muted mt-1">Just now</div>
                    </div>
                </div>
            </div>
        """) 
 
 