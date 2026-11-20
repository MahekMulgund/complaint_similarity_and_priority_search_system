"""
Authentication Routes (Member 1 - Ayeesha)
Manages login, user registration, and logout for user, admin, and staff roles.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Placeholder login route for Member 1 to implement."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Placeholder registration route for Member 1 to implement."""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logs out the active user."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
