import os

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.environ.get('APP_ENV', 'development')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-me')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', '')
DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '5000'))

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')

IS_PRODUCTION = APP_ENV == 'production'
