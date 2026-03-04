from flask import Blueprint, jsonify, request, render_template, send_file, current_app
from flask_login import login_required
from models import Payment, Reservation
from extensions import db

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/api', methods=['GET'])
@login_required
def get_payments():
    res_id = request.args.get('reservation_id', type=int)
    query  = Payment.query
    if res_id:
        query = query.filter_by(reservation_id=res_id)
    payments = query.order_by(Payment.payment_date.desc()).all()
    return jsonify([p.to_dict() for p in payments])

@payments_bp.route('/api', methods=['POST'])
@login_required
def create_payment():
    data = request.get_json()
    res  = Reservation.query.get_or_404(data['reservation_id'])
    payment = Payment(
        reservation_id=data['reservation_id'],
        amount=data['amount'],
        payment_method=data['payment_method'],
        status=data.get('status', 'completed'),
        transaction_id=data.get('transaction_id'),
        notes=data.get('notes')
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify(payment.to_dict()), 201
