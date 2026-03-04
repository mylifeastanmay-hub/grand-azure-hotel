from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from models import Reservation, Room, Guest
from extensions import db
from datetime import datetime, date

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/')
@login_required
def index():
    return render_template('reservations.html')

@reservations_bp.route('/api', methods=['GET'])
@login_required
def get_reservations():
    status = request.args.get('status')
    query  = Reservation.query
    if status:
        query = query.filter_by(status=status)
    reservations = query.order_by(Reservation.booking_date.desc()).all()
    return jsonify([r.to_dict() for r in reservations])

@reservations_bp.route('/api/<int:res_id>', methods=['GET'])
@login_required
def get_reservation(res_id):
    r = Reservation.query.get_or_404(res_id)
    data = r.to_dict()
    data['payments'] = [p.to_dict() for p in r.payments]
    data['services'] = [gs.to_dict() for gs in r.guest_services]
    return jsonify(data)

@reservations_bp.route('/api', methods=['POST'])
@login_required
def create_reservation():
    data     = request.get_json()
    ci       = datetime.strptime(data['check_in_date'],  '%Y-%m-%d').date()
    co       = datetime.strptime(data['check_out_date'], '%Y-%m-%d').date()
    nights   = (co - ci).days
    if nights <= 0:
        return jsonify({'error': 'Check-out must be after check-in'}), 400

    room = Room.query.get_or_404(data['room_id'])

    # Check availability
    conflict = Reservation.query.filter(
        Reservation.room_id == data['room_id'],
        Reservation.status.in_(['confirmed', 'checked_in']),
        Reservation.check_in_date  < co,
        Reservation.check_out_date > ci
    ).first()
    if conflict:
        return jsonify({'error': 'Room not available for selected dates'}), 409

    total = float(room.price_per_night) * nights
    res = Reservation(
        guest_id=data['guest_id'],
        room_id=data['room_id'],
        check_in_date=ci,
        check_out_date=co,
        total_price=total,
        status='confirmed',
        special_requests=data.get('special_requests'),
        adults=data.get('adults', 1),
        children=data.get('children', 0)
    )
    db.session.add(res)
    db.session.commit()
    return jsonify(res.to_dict()), 201

@reservations_bp.route('/api/<int:res_id>/checkin', methods=['POST'])
@login_required
def check_in(res_id):
    res = Reservation.query.get_or_404(res_id)
    if res.status != 'confirmed':
        return jsonify({'error': 'Reservation must be confirmed to check in'}), 400
    res.status = 'checked_in'
    res.room.status = 'occupied'
    db.session.commit()
    return jsonify({'message': 'Checked in successfully', 'reservation': res.to_dict()})

@reservations_bp.route('/api/<int:res_id>/checkout', methods=['POST'])
@login_required
def check_out(res_id):
    res = Reservation.query.get_or_404(res_id)
    if res.status != 'checked_in':
        return jsonify({'error': 'Guest must be checked in to check out'}), 400
    res.status = 'checked_out'
    res.room.status = 'available'
    db.session.commit()
    return jsonify({'message': 'Checked out successfully', 'reservation': res.to_dict()})

@reservations_bp.route('/api/<int:res_id>/cancel', methods=['POST'])
@login_required
def cancel_reservation(res_id):
    res = Reservation.query.get_or_404(res_id)
    if res.status in ['checked_out', 'cancelled']:
        return jsonify({'error': 'Cannot cancel this reservation'}), 400
    res.status = 'cancelled'
    if res.room.status == 'occupied':
        res.room.status = 'available'
    db.session.commit()
    return jsonify({'message': 'Reservation cancelled', 'reservation': res.to_dict()})

@reservations_bp.route('/api/<int:res_id>', methods=['PUT'])
@login_required
def update_reservation(res_id):
    res  = Reservation.query.get_or_404(res_id)
    data = request.get_json()
    for field in ['special_requests', 'adults', 'children']:
        if field in data:
            setattr(res, field, data[field])
    db.session.commit()
    return jsonify(res.to_dict())
