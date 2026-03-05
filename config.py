import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hotel-secret-2024')
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://localhost/HotelManagement?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    INVOICE_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'invoices')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    HOTEL_NAME = 'Grand Azure Hotel'
    HOTEL_ADDRESS = '1 Harbor Boulevard'
    HOTEL_CITY = 'Miami, FL 33101'
    HOTEL_PHONE = '+1 (305) 555-0100'
    HOTEL_EMAIL = 'info@grandazure.com'
    HOTEL_WEBSITE = 'www.grandazure.com'
    TAX_RATE = 0.12
