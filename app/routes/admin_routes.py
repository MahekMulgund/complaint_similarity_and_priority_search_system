"""
Admin Routes - Module 2 (Member 1 - Ayeesha)
Responsibilities:
- Admin dashboard & KPI statistics
- View all complaints
- Search & filter complaints
- Update resolution status with audit trail
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Complaint, Category, Department, IssueGroup, ComplaintHistory

admin_bp = Blueprint('admin', __name__)


def admin_or_staff_required(f):
    """Decorator to restrict access to admin or staff roles."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'staff']:
            flash('Access restricted to administrators and authorized staff.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_or_staff_required
def dashboard():
    """Admin overview dashboard with statistics and recent complaints."""
    total_complaints = Complaint.query.count()
    open_complaints = Complaint.query.filter_by(resolution_status='Open').count()
    resolved_complaints = Complaint.query.filter_by(resolution_status='Resolved').count()
    critical_complaints = Complaint.query.filter_by(priority_level='Critical').count()

    stats = {
        'total': total_complaints,
        'open': open_complaints,
        'resolved': resolved_complaints,
        'critical': critical_complaints
    }
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/complaints')
@login_required
@admin_or_staff_required
def complaint_list():
    """Search and filter complaints list, ordered by priority score descending."""
    complaints = Complaint.query.order_by(
        Complaint.priority_score.desc().nullslast(),
        Complaint.created_at.desc()
    ).all()
    categories = Category.query.all()
    return render_template('admin/complaints.html', complaints=complaints, categories=categories)
