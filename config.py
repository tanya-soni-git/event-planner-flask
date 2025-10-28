import os
basedir = os.path.abspath(os.path.dirname(__file__))

db_url = os.environ.get('DATABASE_URL')

if db_url:
    if db_url.startswith('PostgreSQL://'):
        db_url = db_url.replace('PostgreSQL://', 'postgresql://', 1)
    elif db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-fallback-key'
    SQLALCHEMY_DATABASE_URI = db_url or \
        'mysql+pymysql://root:tanya25soni%40@localhost/event_planner'

    SQLALCHEMY_TRACK_MODIFICATIONS = False