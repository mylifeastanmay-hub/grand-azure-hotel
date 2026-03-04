from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import Staff
from extensions import db
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        data = request.get_json() or request.form
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        user = Staff.query.filter_by(username=username, status='active').first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('dashboard.index')})
            return redirect(url_for('dashboard.index'))

        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        flash('Invalid username or password', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/setup-admin', methods=['GET'])
def setup_admin():
    """One-time setup to create default admin user"""
    if Staff.query.filter_by(username='admin').first():
        return jsonify({'message': 'Admin already exists'})

    admin = Staff(
        name='Administrator',
        position='System Administrator',
        salary=5000,
        contact='555-0001',
        email='admin@hotel.com',
        shift='morning',
        username='admin',
        role='admin',
        status='active'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    return jsonify({'message': 'Admin created. Username: admin, Password: admin123'})
