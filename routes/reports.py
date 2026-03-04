from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required
from models import Reservation, Payment, Room, Guest
from extensions import db
from datetime import datetime, date, timedelta
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    return render_template('reports.html')

@reports_bp.route('/api/revenue')
@login_required
def revenue_report():
    period    = request.args.get('period', 'monthly')
    year      = request.args.get('year', date.today().year, type=int)
    today     = date.today()

    if period == 'daily':
        results = []
        for i in range(29, -1, -1):
            d   = today - timedelta(days=i)
            rev = db.session.query(func.sum(Payment.amount)).filter(
                func.cast(Payment.payment_date, db.Date) == d,
                Payment.status == 'completed'
            ).scalar() or 0
            results.append({'label': d.strftime('%b %d'), 'revenue': float(rev)})
        return jsonify(results)

    elif period == 'monthly':
        results = []
        for m in range(1, 13):
            rev = db.session.query(func.sum(Payment.amount)).filter(
                db.extract('year',  Payment.payment_date) == year,
                db.extract('month', Payment.payment_date) == m,
                Payment.status == 'completed'
            ).scalar() or 0
            results.append({'label': datetime(year, m, 1).strftime('%b'), 'revenue': float(rev)})
        return jsonify(results)

@reports_bp.route('/api/occupancy')
@login_required
def occupancy_report():
    today     = date.today()
    results   = []
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        occupied = Reservation.query.filter(
            Reservation.check_in_date  <= d,
            Reservation.check_out_date >  d,
            Reservation.status.in_(['checked_in', 'checked_out', 'confirmed'])
        ).count()
        total = Room.query.count()
        results.append({
            'date': d.strftime('%b %d'),
            'occupied': occupied,
            'total': total,
            'rate': round(occupied / total * 100, 1) if total else 0
        })
    return jsonify(results)

@reports_bp.route('/api/summary')
@login_required
def summary_report():
    today       = date.today()
    month_start = today.replace(day=1)
    year_start  = today.replace(month=1, day=1)

    total_rev_month = db.session.query(func.sum(Payment.amount)).filter(
        func.cast(Payment.payment_date, db.Date) >= month_start,
        Payment.status == 'completed'
    ).scalar() or 0

    total_rev_year = db.session.query(func.sum(Payment.amount)).filter(
        func.cast(Payment.payment_date, db.Date) >= year_start,
        Payment.status == 'completed'
    ).scalar() or 0

    total_bookings_month = Reservation.query.filter(
        func.cast(Reservation.booking_date, db.Date) >= month_start
    ).count()

    avg_stay = db.session.query(
        func.avg(
            db.func.datediff(db.text('day'), Reservation.check_in_date, Reservation.check_out_date)
        )
    ).scalar() or 0

    return jsonify({
        'monthly_revenue': float(total_rev_month),
        'annual_revenue': float(total_rev_year),
        'monthly_bookings': total_bookings_month,
        'avg_stay_nights': round(float(avg_stay), 1),
        'total_guests': Guest.query.count(),
        'total_rooms': Room.query.count()
    })
