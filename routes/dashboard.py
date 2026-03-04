from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from models import Guest, Room, Reservation, Payment, Staff, GuestService
from extensions import db
from datetime import datetime, date, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/dashboard/stats')
@login_required
def stats():
    today = date.today()
    month_start = today.replace(day=1)

    total_rooms       = Room.query.count()
    available_rooms   = Room.query.filter_by(status='available').count()
    occupied_rooms    = Room.query.filter_by(status='occupied').count()
    occupancy_rate    = round((occupied_rooms / total_rooms * 100), 1) if total_rooms else 0

    total_guests      = Guest.query.count()
    active_reservations = Reservation.query.filter(
        Reservation.status.in_(['confirmed', 'checked_in'])
    ).count()

    checkins_today    = Reservation.query.filter_by(check_in_date=today, status='confirmed').count()
    checkouts_today   = Reservation.query.filter_by(check_out_date=today, status='checked_in').count()

    monthly_revenue = db.session.query(func.sum(Payment.amount)).filter(
        func.cast(Payment.payment_date, db.Date) >= month_start,
        Payment.status == 'completed'
    ).scalar() or 0

    today_revenue = db.session.query(func.sum(Payment.amount)).filter(
        func.cast(Payment.payment_date, db.Date) == today,
        Payment.status == 'completed'
    ).scalar() or 0

    # Revenue for last 7 days
    revenue_chart = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        rev = db.session.query(func.sum(Payment.amount)).filter(
            func.cast(Payment.payment_date, db.Date) == d,
            Payment.status == 'completed'
        ).scalar() or 0
        revenue_chart.append({'date': d.strftime('%b %d'), 'revenue': float(rev)})

    # Room type distribution
    room_types = db.session.query(
        Room.room_type, func.count(Room.room_id)
    ).group_by(Room.room_type).all()

    # Recent reservations
    recent = Reservation.query.order_by(Reservation.booking_date.desc()).limit(5).all()

    return jsonify({
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'occupancy_rate': occupancy_rate,
        'total_guests': total_guests,
        'active_reservations': active_reservations,
        'checkins_today': checkins_today,
        'checkouts_today': checkouts_today,
        'monthly_revenue': float(monthly_revenue),
        'today_revenue': float(today_revenue),
        'revenue_chart': revenue_chart,
        'room_types': [{'type': r[0], 'count': r[1]} for r in room_types],
        'recent_reservations': [r.to_dict() for r in recent]
    })
