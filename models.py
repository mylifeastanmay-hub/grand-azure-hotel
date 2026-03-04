"""
Database Models for Hotel Management System
"""

from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Guest(db.Model):
    __tablename__ = 'Guests'
    guest_id        = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    email           = db.Column(db.String(150), unique=True, nullable=False)
    phone           = db.Column(db.String(20), nullable=False)
    address         = db.Column(db.String(300))
    id_proof_type   = db.Column(db.String(50))
    id_proof_number = db.Column(db.String(100))
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reservations    = db.relationship('Reservation', backref='guest', lazy=True)
    guest_services  = db.relationship('GuestService', backref='guest', lazy=True)

    def to_dict(self):
        return {
            'guest_id': self.guest_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'id_proof_type': self.id_proof_type,
            'id_proof_number': self.id_proof_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Room(db.Model):
    __tablename__ = 'Rooms'
    room_id         = db.Column(db.Integer, primary_key=True)
    room_number     = db.Column(db.String(10), unique=True, nullable=False)
    room_type       = db.Column(db.String(50), nullable=False)
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    status          = db.Column(db.String(20), default='available')
    floor           = db.Column(db.Integer, nullable=False)
    description     = db.Column(db.String(500))
    max_occupancy   = db.Column(db.Integer, default=2)
    amenities       = db.Column(db.String(500))
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    reservations    = db.relationship('Reservation', backref='room', lazy=True)

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'room_number': self.room_number,
            'room_type': self.room_type,
            'price_per_night': float(self.price_per_night),
            'status': self.status,
            'floor': self.floor,
            'description': self.description,
            'max_occupancy': self.max_occupancy,
            'amenities': self.amenities
        }


class Reservation(db.Model):
    __tablename__ = 'Reservations'
    reservation_id   = db.Column(db.Integer, primary_key=True)
    guest_id         = db.Column(db.Integer, db.ForeignKey('Guests.guest_id'), nullable=False)
    room_id          = db.Column(db.Integer, db.ForeignKey('Rooms.room_id'), nullable=False)
    check_in_date    = db.Column(db.Date, nullable=False)
    check_out_date   = db.Column(db.Date, nullable=False)
    total_price      = db.Column(db.Numeric(10, 2), nullable=False)
    status           = db.Column(db.String(20), default='confirmed')
    booking_date     = db.Column(db.DateTime, default=datetime.utcnow)
    special_requests = db.Column(db.String(500))
    adults           = db.Column(db.Integer, default=1)
    children         = db.Column(db.Integer, default=0)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payments         = db.relationship('Payment', backref='reservation', lazy=True)
    guest_services   = db.relationship('GuestService', backref='reservation', lazy=True)

    def to_dict(self):
        return {
            'reservation_id': self.reservation_id,
            'guest_id': self.guest_id,
            'guest_name': self.guest.name if self.guest else None,
            'room_id': self.room_id,
            'room_number': self.room.room_number if self.room else None,
            'room_type': self.room.room_type if self.room else None,
            'check_in_date': self.check_in_date.isoformat() if self.check_in_date else None,
            'check_out_date': self.check_out_date.isoformat() if self.check_out_date else None,
            'total_price': float(self.total_price),
            'status': self.status,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'special_requests': self.special_requests,
            'adults': self.adults,
            'children': self.children
        }


class Payment(db.Model):
    __tablename__ = 'Payments'
    payment_id      = db.Column(db.Integer, primary_key=True)
    reservation_id  = db.Column(db.Integer, db.ForeignKey('Reservations.reservation_id'), nullable=False)
    amount          = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date    = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method  = db.Column(db.String(50), nullable=False)
    status          = db.Column(db.String(20), default='completed')
    transaction_id  = db.Column(db.String(100))
    notes           = db.Column(db.String(300))

    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'reservation_id': self.reservation_id,
            'amount': float(self.amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'status': self.status,
            'transaction_id': self.transaction_id,
            'notes': self.notes
        }


class Staff(UserMixin, db.Model):
    __tablename__ = 'Staff'
    staff_id      = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    position      = db.Column(db.String(100), nullable=False)
    salary        = db.Column(db.Numeric(10, 2), nullable=False)
    contact       = db.Column(db.String(20), nullable=False)
    email         = db.Column(db.String(150), unique=True)
    shift         = db.Column(db.String(20), default='morning')
    hire_date     = db.Column(db.Date, default=datetime.utcnow)
    status        = db.Column(db.String(20), default='active')
    username      = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(256))
    role          = db.Column(db.String(20), default='staff')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return str(self.staff_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'staff_id': self.staff_id,
            'name': self.name,
            'position': self.position,
            'salary': float(self.salary),
            'contact': self.contact,
            'email': self.email,
            'shift': self.shift,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'status': self.status,
            'username': self.username,
            'role': self.role
        }


class Service(db.Model):
    __tablename__ = 'Services'
    service_id   = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    description  = db.Column(db.String(500))
    price        = db.Column(db.Numeric(10, 2), nullable=False)
    category     = db.Column(db.String(50))
    available    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    guest_services = db.relationship('GuestService', backref='service', lazy=True)

    def to_dict(self):
        return {
            'service_id': self.service_id,
            'service_name': self.service_name,
            'description': self.description,
            'price': float(self.price),
            'category': self.category,
            'available': self.available
        }


class GuestService(db.Model):
    __tablename__ = 'Guest_Services'
    guest_service_id = db.Column(db.Integer, primary_key=True)
    guest_id         = db.Column(db.Integer, db.ForeignKey('Guests.guest_id'), nullable=False)
    service_id       = db.Column(db.Integer, db.ForeignKey('Services.service_id'), nullable=False)
    reservation_id   = db.Column(db.Integer, db.ForeignKey('Reservations.reservation_id'))
    date             = db.Column(db.DateTime, default=datetime.utcnow)
    quantity         = db.Column(db.Integer, default=1)
    total_price      = db.Column(db.Numeric(10, 2), nullable=False)
    status           = db.Column(db.String(20), default='pending')
    notes            = db.Column(db.String(300))

    def to_dict(self):
        return {
            'guest_service_id': self.guest_service_id,
            'guest_id': self.guest_id,
            'guest_name': self.guest.name if self.guest else None,
            'service_id': self.service_id,
            'service_name': self.service.service_name if self.service else None,
            'reservation_id': self.reservation_id,
            'date': self.date.isoformat() if self.date else None,
            'quantity': self.quantity,
            'total_price': float(self.total_price),
            'status': self.status,
            'notes': self.notes
        }
