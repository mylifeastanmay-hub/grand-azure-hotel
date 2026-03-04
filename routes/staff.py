from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from models import Staff
from extensions import db

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/')
@login_required
def index():
    return render_template('staff.html')

@staff_bp.route('/api', methods=['GET'])
@login_required
def get_staff():
    staff = Staff.query.order_by(Staff.name).all()
    return jsonify([s.to_dict() for s in staff])

@staff_bp.route('/api/<int:staff_id>', methods=['GET'])
@login_required
def get_staff_member(staff_id):
    s = Staff.query.get_or_404(staff_id)
    return jsonify(s.to_dict())

@staff_bp.route('/api', methods=['POST'])
@login_required
def create_staff():
    if current_user.role not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    if Staff.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': 'Username already taken'}), 400
    s = Staff(
        name=data['name'], position=data['position'],
        salary=data['salary'], contact=data['contact'],
        email=data.get('email'), shift=data.get('shift', 'morning'),
        username=data.get('username'), role=data.get('role', 'staff'),
        status='active'
    )
    if data.get('password'):
        s.set_password(data['password'])
    db.session.add(s)
    db.session.commit()
    return jsonify(s.to_dict()), 201

@staff_bp.route('/api/<int:staff_id>', methods=['PUT'])
@login_required
def update_staff(staff_id):
    if current_user.role not in ['admin', 'manager'] and current_user.staff_id != staff_id:
        return jsonify({'error': 'Unauthorized'}), 403
    s    = Staff.query.get_or_404(staff_id)
    data = request.get_json()
    for f in ['name','position','salary','contact','email','shift','status','role']:
        if f in data:
            setattr(s, f, data[f])
    if data.get('password') and current_user.role == 'admin':
        s.set_password(data['password'])
    db.session.commit()
    return jsonify(s.to_dict())

@staff_bp.route('/api/<int:staff_id>', methods=['DELETE'])
@login_required
def delete_staff(staff_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    s = Staff.query.get_or_404(staff_id)
    s.status = 'inactive'
    db.session.commit()
    return jsonify({'message': 'Staff deactivated'})
