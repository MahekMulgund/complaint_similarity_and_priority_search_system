"""
User Routes - Module 1 (Member 1 - Ayeesha)
Responsibilities:
- User dashboard
- Complaint intake submission
- View submitted complaints
- Track individual complaint status
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Complaint, Category

user_bp = Blueprint('user', __name__)


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing their personal submitted complaints."""
    user_complaints = Complaint.query.filter_by(
        user_id=current_user.user_id
    ).order_by(Complaint.created_at.desc()).all()
    return render_template('user/dashboard.html', complaints=user_complaints)


@user_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_complaint():
    """Form to submit a new complaint into the system."""
    categories = Category.query.all()
    return render_template('user/submit.html', categories=categories)


@user_bp.route('/track/<int:complaint_id>')
@login_required
def track_complaint(complaint_id):
    """Detailed tracking view of a specific complaint."""
    complaint = Complaint.query.get_or_404(complaint_id)
    # Ensure regular users can only track their own complaints
    if current_user.role == 'user' and complaint.user_id != current_user.user_id:
        flash('Unauthorized to view this complaint.', 'danger')
        return redirect(url_for('user.dashboard'))
    return render_template('user/track.html', complaint=complaint)
