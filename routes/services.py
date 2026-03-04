from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required
from models import Service, GuestService, Guest
from extensions import db

services_bp = Blueprint('services', __name__)

@services_bp.route('/')
@login_required
def index():
    return render_template('services.html')

@services_bp.route('/api', methods=['GET'])
@login_required
def get_services():
    services = Service.query.filter_by(available=True).order_by(Service.category, Service.service_name).all()
    return jsonify([s.to_dict() for s in services])

@services_bp.route('/api', methods=['POST'])
@login_required
def create_service():
    data = request.get_json()
    svc  = Service(**{k: data[k] for k in ['service_name','description','price','category'] if k in data})
    db.session.add(svc)
    db.session.commit()
    return jsonify(svc.to_dict()), 201

@services_bp.route('/api/<int:svc_id>', methods=['PUT'])
@login_required
def update_service(svc_id):
    svc  = Service.query.get_or_404(svc_id)
    data = request.get_json()
    for f in ['service_name','description','price','category','available']:
        if f in data:
            setattr(svc, f, data[f])
    db.session.commit()
    return jsonify(svc.to_dict())

@services_bp.route('/api/<int:svc_id>', methods=['DELETE'])
@login_required
def delete_service(svc_id):
    svc = Service.query.get_or_404(svc_id)
    svc.available = False
    db.session.commit()
    return jsonify({'message': 'Service deactivated'})

@services_bp.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    orders = GuestService.query.order_by(GuestService.date.desc()).limit(50).all()
    return jsonify([o.to_dict() for o in orders])

@services_bp.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    data    = request.get_json()
    service = Service.query.get_or_404(data['service_id'])
    qty     = int(data.get('quantity', 1))
    order   = GuestService(
        guest_id=data['guest_id'],
        service_id=data['service_id'],
        reservation_id=data.get('reservation_id'),
        quantity=qty,
        total_price=float(service.price) * qty,
        notes=data.get('notes'),
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201

@services_bp.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    order  = GuestService.query.get_or_404(order_id)
    data   = request.get_json()
    order.status = data['status']
    db.session.commit()
    return jsonify(order.to_dict())
