"""
Hotel Management System - Main Application
Flask Backend with SQL Server via pyodbc
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv

from config import Config
from extensions import db
from models import Staff

# Load environment variables
load_dotenv()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return Staff.query.get(int(user_id))

    # Register blueprints
    from routes.auth      import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.guests    import guests_bp
    from routes.rooms     import rooms_bp
    from routes.reservations import reservations_bp
    from routes.payments  import payments_bp
    from routes.services  import services_bp
    from routes.staff     import staff_bp
    from routes.reports   import reports_bp
    from routes.invoices  import invoices_bp
    from routes.public    import public_bp

    app.register_blueprint(public_bp,       url_prefix='')
    app.register_blueprint(auth_bp,         url_prefix='/auth')
    app.register_blueprint(dashboard_bp,    url_prefix='/admin')
    app.register_blueprint(guests_bp,       url_prefix='/guests')
    app.register_blueprint(rooms_bp,        url_prefix='/rooms')
    app.register_blueprint(reservations_bp, url_prefix='/reservations')
    app.register_blueprint(payments_bp,     url_prefix='/payments')
    app.register_blueprint(services_bp,     url_prefix='/services')
    app.register_blueprint(staff_bp,        url_prefix='/staff')
    app.register_blueprint(reports_bp,      url_prefix='/reports')
    app.register_blueprint(invoices_bp,     url_prefix='/invoices')

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
