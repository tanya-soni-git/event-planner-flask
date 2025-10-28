import os
basedir = os.path.abspath(os.path.dirname(__file__))

db_url = os.environ.get('DATABASE_URL')

# --- NEW ROBUST FIX ---
# Render's DB URL might be 'postgres://' OR 'PostgreSQL://'
# SQLAlchemy's driver requires 'postgresql://' (with 'ql')
if db_url:
    if db_url.startswith('PostgreSQL://'):
        # Replace uppercase
        db_url = db_url.replace('PostgreSQL://', 'postgresql://', 1)
    elif db_url.startswith('postgres://'):
        # Replace lowercase
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
# --- END OF FIX ---

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-fallback-key'

    # Use the fixed db_url, or fall back to your local MySQL
    SQLALCHEMY_DATABASE_URI = db_url or \
        'mysql+pymysql://root:tanya25soni%40@localhost/event_planner'

    SQLALCHEMY_TRACK_MODIFICATIONS = False