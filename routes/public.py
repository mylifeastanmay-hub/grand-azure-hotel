from flask import Blueprint, render_template, jsonify, request
from models import Room, Guest, Reservation, Service
from extensions import db
from datetime import datetime
public_bp = Blueprint("public", __name__)
@public_bp.route("/")
def home():
    return render_template("public/home.html")
@public_bp.route("/rooms")
def rooms():
    return render_template("public/rooms.html")
@public_bp.route("/book")
def book():
    return render_template("public/book.html")
@public_bp.route("/confirmation/<int:reservation_id>")
def confirmation(reservation_id):
    res = Reservation.query.get_or_404(reservation_id)
    return render_template("public/confirmation.html", reservation=res)
@public_bp.route("/lookup")
def lookup():
    return render_template("public/lookup.html")
@public_bp.route("/api/rooms")
def api_rooms():
    check_in = request.args.get("check_in")
    check_out = request.args.get("check_out")
    room_type = request.args.get("room_type")
    max_price = request.args.get("max_price", type=float)
    query = Room.query.filter_by(status="available")
    if check_in and check_out:
        ci = datetime.strptime(check_in, "%Y-%m-%d").date()
        co = datetime.strptime(check_out, "%Y-%m-%d").date()
        booked_ids = db.session.query(Reservation.room_id).filter(Reservation.status.in_(["confirmed","checked_in"]),Reservation.check_in_date < co,Reservation.check_out_date > ci).subquery()
        query = query.filter(~Room.room_id.in_(booked_ids))
    if room_type:
        query = query.filter_by(room_type=room_type)
    if max_price:
        query = query.filter(Room.price_per_night <= max_price)
    rooms = query.order_by(Room.price_per_night).all()
    return jsonify([r.to_dict() for r in rooms])
@public_bp.route("/api/book", methods=["POST"])
def api_book():
    data = request.get_json()
    ci = datetime.strptime(data["check_in_date"], "%Y-%m-%d").date()
    co = datetime.strptime(data["check_out_date"], "%Y-%m-%d").date()
    nights = (co - ci).days
    if nights <= 0:
        return jsonify({"error": "Check-out must be after check-in"}), 400
    room = Room.query.get_or_404(data["room_id"])
    conflict = Reservation.query.filter(Reservation.room_id==data["room_id"],Reservation.status.in_(["confirmed","checked_in"]),Reservation.check_in_date < co,Reservation.check_out_date > ci).first()
    if conflict:
        return jsonify({"error": "Room not available for selected dates"}), 409
    guest = Guest.query.filter_by(email=data["email"]).first()
    if not guest:
        guest = Guest(name=data["name"],email=data["email"],phone=data["phone"],address=data.get("address",""),id_proof_type=data.get("id_proof_type",""),id_proof_number=data.get("id_proof_number",""))
        db.session.add(guest)
        db.session.flush()
    total = float(room.price_per_night) * nights
    res = Reservation(guest_id=guest.guest_id,room_id=room.room_id,check_in_date=ci,check_out_date=co,total_price=total,status="confirmed",special_requests=data.get("special_requests",""),adults=data.get("adults",1),children=data.get("children",0))
    db.session.add(res)
    db.session.commit()
    return jsonify({"success":True,"reservation_id":res.reservation_id,"total_price":total,"nights":nights,"room_number":room.room_number,"room_type":room.room_type,"check_in_date":ci.isoformat(),"check_out_date":co.isoformat(),"guest_name":guest.name}), 201
@public_bp.route("/api/lookup", methods=["POST"])
def api_lookup():
    data = request.get_json()
    email = data.get("email","").strip()
    ref = data.get("reservation_id","")
    query = Reservation.query.join(Guest).filter(Guest.email==email)
    if ref:
        query = query.filter(Reservation.reservation_id==int(ref))
    reservations = query.order_by(Reservation.booking_date.desc()).all()
    return jsonify([r.to_dict() for r in reservations])
