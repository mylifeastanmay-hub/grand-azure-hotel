from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from models import Guest
from extensions import db

guests_bp = Blueprint('guests', __name__)

@guests_bp.route('/')
@login_required
def index():
    return render_template('guests.html')

@guests_bp.route('/api', methods=['GET'])
@login_required
def get_guests():
    q = request.args.get('q', '').strip()
    query = Guest.query
    if q:
        query = query.filter(
            db.or_(
                Guest.name.ilike(f'%{q}%'),
                Guest.email.ilike(f'%{q}%'),
                Guest.phone.ilike(f'%{q}%')
            )
        )
    guests = query.order_by(Guest.name).all()
    return jsonify([g.to_dict() for g in guests])

@guests_bp.route('/api/<int:guest_id>', methods=['GET'])
@login_required
def get_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    return jsonify(guest.to_dict())

@guests_bp.route('/api', methods=['POST'])
@login_required
def create_guest():
    data = request.get_json()
    if Guest.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    guest = Guest(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        address=data.get('address'),
        id_proof_type=data.get('id_proof_type'),
        id_proof_number=data.get('id_proof_number')
    )
    db.session.add(guest)
    db.session.commit()
    return jsonify(guest.to_dict()), 201

@guests_bp.route('/api/<int:guest_id>', methods=['PUT'])
@login_required
def update_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    data = request.get_json()
    for field in ['name', 'email', 'phone', 'address', 'id_proof_type', 'id_proof_number']:
        if field in data:
            setattr(guest, field, data[field])
    db.session.commit()
    return jsonify(guest.to_dict())

@guests_bp.route('/api/<int:guest_id>', methods=['DELETE'])
@login_required
def delete_guest(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    db.session.delete(guest)
    db.session.commit()
    return jsonify({'message': 'Guest deleted'})
