import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Get the database URL from the environment
db_url = os.environ.get('DATABASE_URL')

# FIX: Replace 'postgres://' with 'postgresql://' for Render
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-fallback-key'

    # Use the fixed db_url, or fall back to your local MySQL
    SQLALCHEMY_DATABASE_URI = db_url or \
        'mysql+pymysql://root:tanya25soni%40@localhost/event_planner'

    SQLALCHEMY_TRACK_MODIFICATIONS = False