import os
from flask import Blueprint, jsonify, send_file, current_app, render_template
from flask_login import login_required
from models import Reservation, Payment, GuestService
from extensions import db
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import HexColor
import tempfile
from datetime import datetime

invoices_bp = Blueprint('invoices', __name__)

BRAND_DARK  = HexColor('#0D1B2A')
BRAND_BLUE  = HexColor('#1B4F72')
BRAND_GOLD  = HexColor('#D4A853')
BRAND_LIGHT = HexColor('#F4F6F8')

def generate_invoice_pdf(reservation_id):
    res      = Reservation.query.get_or_404(reservation_id)
    payments = Payment.query.filter_by(reservation_id=reservation_id, status='completed').all()
    services = GuestService.query.filter_by(reservation_id=reservation_id).all()

    cfg  = current_app.config
    path = os.path.join(cfg['INVOICE_FOLDER'], f'invoice_{reservation_id}.pdf')

    doc    = SimpleDocTemplate(path, pagesize=A4,
                               leftMargin=15*mm, rightMargin=15*mm,
                               topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    story  = []

    # Header styles
    h_title = ParagraphStyle('HTitle', fontName='Helvetica-Bold', fontSize=22,
                              textColor=BRAND_DARK, spaceAfter=2)
    h_sub   = ParagraphStyle('HSub',   fontName='Helvetica',      fontSize=10,
                              textColor=BRAND_BLUE)
    h_small = ParagraphStyle('HSmall', fontName='Helvetica',      fontSize=8,
                              textColor=colors.grey)
    h_right = ParagraphStyle('HRight', fontName='Helvetica',      fontSize=9,
                              textColor=BRAND_DARK, alignment=TA_RIGHT)
    h_label = ParagraphStyle('HLabel', fontName='Helvetica-Bold', fontSize=9,
                              textColor=BRAND_GOLD)
    h_val   = ParagraphStyle('HVal',   fontName='Helvetica',      fontSize=9,
                              textColor=BRAND_DARK)
    h_total = ParagraphStyle('HTotal', fontName='Helvetica-Bold', fontSize=11,
                              textColor=BRAND_DARK, alignment=TA_RIGHT)

    # Top header table
    nights   = (res.check_out_date - res.check_in_date).days
    inv_num  = f'INV-{reservation_id:05d}'
    inv_date = datetime.now().strftime('%B %d, %Y')

    header_data = [[
        [Paragraph(cfg['HOTEL_NAME'],    h_title),
         Paragraph(cfg['HOTEL_ADDRESS'], h_sub),
         Paragraph(cfg['HOTEL_CITY'],    h_sub),
         Paragraph(f"Tel: {cfg['HOTEL_PHONE']} | {cfg['HOTEL_EMAIL']}", h_small)],
        [Paragraph('INVOICE',            ParagraphStyle('Inv', fontName='Helvetica-Bold',
                                          fontSize=28, textColor=BRAND_GOLD, alignment=TA_RIGHT)),
         Paragraph(f'{inv_num}',         h_right),
         Paragraph(f'Date: {inv_date}',  h_right)]
    ]]
    header_tbl = Table(header_data, colWidths=[100*mm, 80*mm])
    header_tbl.setStyle(TableStyle([
        ('VALIGN',      (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND',  (0,0), (-1,-1), BRAND_LIGHT),
        ('ROWPADDING',  (0,0), (-1,-1), 8),
        ('LINEBELOW',   (0,0), (-1,0), 2, BRAND_GOLD),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 8*mm))

    # Guest & Reservation Info
    info_data = [
        [Paragraph('BILL TO', h_label),
         Paragraph('RESERVATION DETAILS', h_label)],
        [Paragraph(res.guest.name,  h_val),
         Paragraph(f'Room: {res.room.room_number} ({res.room.room_type})', h_val)],
        [Paragraph(res.guest.email, h_val),
         Paragraph(f'Check-in:  {res.check_in_date.strftime("%b %d, %Y")}', h_val)],
        [Paragraph(res.guest.phone, h_val),
         Paragraph(f'Check-out: {res.check_out_date.strftime("%b %d, %Y")}', h_val)],
        [Paragraph('', h_val),
         Paragraph(f'Nights: {nights}  |  Guests: {res.adults} adult(s)', h_val)],
    ]
    info_tbl = Table(info_data, colWidths=[90*mm, 90*mm])
    info_tbl.setStyle(TableStyle([
        ('VALIGN',      (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',  (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0),(-1,-1), 4),
        ('LINEAFTER',   (0,0), (0,-1), 0.5, colors.lightgrey),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 8*mm))

    # Charges table
    story.append(Paragraph('CHARGES', h_label))
    story.append(Spacer(1, 3*mm))

    rows = [['Description', 'Qty', 'Unit Price', 'Amount']]
    subtotal = 0.0

    # Room charges
    room_total = float(res.room.price_per_night) * nights
    rows.append([
        f'Room {res.room.room_number} - {res.room.room_type}',
        f'{nights} nights',
        f'${float(res.room.price_per_night):.2f}',
        f'${room_total:.2f}'
    ])
    subtotal += room_total

    # Additional services
    for gs in services:
        rows.append([
            gs.service.service_name,
            str(gs.quantity),
            f'${float(gs.service.price):.2f}',
            f'${float(gs.total_price):.2f}'
        ])
        subtotal += float(gs.total_price)

    tax_rate = cfg['TAX_RATE']
    tax_amt  = subtotal * tax_rate
    grand    = subtotal + tax_amt
    paid     = sum(float(p.amount) for p in payments)
    due      = grand - paid

    charges_tbl = Table(rows, colWidths=[90*mm, 25*mm, 32*mm, 33*mm])
    charges_tbl.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), BRAND_DARK),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('ALIGN',        (1,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING',   (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, BRAND_LIGHT]),
        ('GRID',         (0,0), (-1,-1), 0.25, colors.lightgrey),
    ]))
    story.append(charges_tbl)
    story.append(Spacer(1, 5*mm))

    # Totals
    totals_data = [
        ['', 'Subtotal:', f'${subtotal:.2f}'],
        ['', f'Tax ({int(tax_rate*100)}%):', f'${tax_amt:.2f}'],
        ['', 'TOTAL:', f'${grand:.2f}'],
        ['', 'Paid:', f'${paid:.2f}'],
        ['', 'BALANCE DUE:', f'${due:.2f}'],
    ]
    totals_tbl = Table(totals_data, colWidths=[100*mm, 40*mm, 40*mm])
    totals_tbl.setStyle(TableStyle([
        ('ALIGN',       (1,0), (-1,-1), 'RIGHT'),
        ('FONTSIZE',    (0,0), (-1,-1), 9),
        ('FONTNAME',    (1,2), (-1,2), 'Helvetica-Bold'),
        ('FONTSIZE',    (1,2), (-1,2), 11),
        ('FONTNAME',    (1,4), (-1,4), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (1,4), (-1,4), BRAND_GOLD),
        ('FONTSIZE',    (1,4), (-1,4), 12),
        ('TOPPADDING',  (0,0), (-1,-1), 3),
        ('LINEABOVE',   (1,2), (-1,2), 1, BRAND_DARK),
        ('LINEABOVE',   (1,4), (-1,4), 1, BRAND_GOLD),
    ]))
    story.append(totals_tbl)
    story.append(Spacer(1, 8*mm))

    # Payment history
    if payments:
        story.append(Paragraph('PAYMENTS RECEIVED', h_label))
        story.append(Spacer(1, 3*mm))
        pay_rows = [['Date', 'Method', 'Transaction ID', 'Amount']]
        for p in payments:
            pay_rows.append([
                p.payment_date.strftime('%b %d, %Y'),
                p.payment_method.replace('_', ' ').title(),
                p.transaction_id or '—',
                f'${float(p.amount):.2f}'
            ])
        pay_tbl = Table(pay_rows, colWidths=[40*mm, 40*mm, 60*mm, 40*mm])
        pay_tbl.setStyle(TableStyle([
            ('BACKGROUND',   (0,0), (-1,0), BRAND_BLUE),
            ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
            ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',     (0,0), (-1,-1), 8),
            ('ALIGN',        (3,0), (-1,-1), 'RIGHT'),
            ('TOPPADDING',   (0,0), (-1,-1), 4),
            ('BOTTOMPADDING',(0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, BRAND_LIGHT]),
            ('GRID',         (0,0), (-1,-1), 0.25, colors.lightgrey),
        ]))
        story.append(pay_tbl)

    story.append(Spacer(1, 12*mm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 4*mm))

    footer = ParagraphStyle('Footer', fontName='Helvetica', fontSize=8,
                             textColor=colors.grey, alignment=TA_CENTER)
    story.append(Paragraph(
        f'Thank you for staying at {cfg["HOTEL_NAME"]}. '
        f'For inquiries: {cfg["HOTEL_PHONE"]} | {cfg["HOTEL_EMAIL"]} | {cfg["HOTEL_WEBSITE"]}',
        footer
    ))

    doc.build(story)
    return path


@invoices_bp.route('/generate/<int:reservation_id>')
@login_required
def generate(reservation_id):
    path = generate_invoice_pdf(reservation_id)
    return send_file(path, as_attachment=True,
                     download_name=f'Invoice_{reservation_id}.pdf',
                     mimetype='application/pdf')

@invoices_bp.route('/view/<int:reservation_id>')
@login_required
def view_invoice(reservation_id):
    path = generate_invoice_pdf(reservation_id)
    return send_file(path, as_attachment=False, mimetype='application/pdf')
