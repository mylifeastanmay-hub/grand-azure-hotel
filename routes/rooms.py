from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from models import Room, Reservation
from extensions import db
from datetime import datetime

rooms_bp = Blueprint('rooms', __name__)

@rooms_bp.route('/')
@login_required
def index():
    return render_template('rooms.html')

@rooms_bp.route('/api', methods=['GET'])
@login_required
def get_rooms():
    status    = request.args.get('status')
    room_type = request.args.get('room_type')
    query = Room.query
    if status:
        query = query.filter_by(status=status)
    if room_type:
        query = query.filter_by(room_type=room_type)
    rooms = query.order_by(Room.room_number).all()
    return jsonify([r.to_dict() for r in rooms])

@rooms_bp.route('/api/available', methods=['GET'])
@login_required
def get_available_rooms():
    check_in  = request.args.get('check_in')
    check_out = request.args.get('check_out')
    room_type = request.args.get('room_type')
    max_price = request.args.get('max_price', type=float)

    if not check_in or not check_out:
        return jsonify({'error': 'check_in and check_out dates required'}), 400

    ci = datetime.strptime(check_in, '%Y-%m-%d').date()
    co = datetime.strptime(check_out, '%Y-%m-%d').date()

    # Find rooms already booked for this period
    booked_room_ids = db.session.query(Reservation.room_id).filter(
        Reservation.status.in_(['confirmed', 'checked_in']),
        Reservation.check_in_date  < co,
        Reservation.check_out_date > ci
    ).subquery()

    query = Room.query.filter(
        Room.status == 'available',
        ~Room.room_id.in_(booked_room_ids)
    )
    if room_type:
        query = query.filter_by(room_type=room_type)
    if max_price:
        query = query.filter(Room.price_per_night <= max_price)

    rooms = query.order_by(Room.price_per_night).all()
    return jsonify([r.to_dict() for r in rooms])

@rooms_bp.route('/api/<int:room_id>', methods=['GET'])
@login_required
def get_room(room_id):
    room = Room.query.get_or_404(room_id)
    return jsonify(room.to_dict())

@rooms_bp.route('/api', methods=['POST'])
@login_required
def create_room():
    data = request.get_json()
    if Room.query.filter_by(room_number=data['room_number']).first():
        return jsonify({'error': 'Room number already exists'}), 400
    room = Room(**{k: data[k] for k in [
        'room_number','room_type','price_per_night','floor',
        'description','max_occupancy','amenities'
    ] if k in data})
    room.status = data.get('status', 'available')
    db.session.add(room)
    db.session.commit()
    return jsonify(room.to_dict()), 201

@rooms_bp.route('/api/<int:room_id>', methods=['PUT'])
@login_required
def update_room(room_id):
    room = Room.query.get_or_404(room_id)
    data = request.get_json()
    for field in ['room_type','price_per_night','status','floor','description','max_occupancy','amenities']:
        if field in data:
            setattr(room, field, data[field])
    db.session.commit()
    return jsonify(room.to_dict())

@rooms_bp.route('/api/<int:room_id>', methods=['DELETE'])
@login_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    return jsonify({'message': 'Room deleted'})
