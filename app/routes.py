from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from app import db
from app.forms import LoginForm, RegistrationForm, EventForm
from app.models import User, Event, RSVP
from sqlalchemy import func
import datetime
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps

main = Blueprint('main', __name__)

# --- Admin Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Admin':
            abort(403) 
        return f(*args, **kwargs)
    return decorated_function

# --- Error Handler ---
@main.app_errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

# --- Authentication Routes ---
@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, role='User')
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('register.html', title='Register', form=form)


@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    form = LoginForm()
    
    if form.validate_on_submit():
        # --- POST LOGIC ---
        # Get the intended role from the hidden form field
        submitted_role = request.form.get('role', 'user')
        
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):
            
            # NOW, check if their actual role matches their intended role
            if (submitted_role == 'admin' and user.role == 'Admin') or \
               (submitted_role == 'user' and user.role == 'User'):
                
                # Success! Log them in.
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash('Login Successful!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                # Role mismatch error
                flash(f"You do not have permission to log in via the '{submitted_role}' portal.", 'danger')
        else:
            # Bad email/password error
            flash('Login Unsuccessful. Please check email and password', 'danger')
        
        # If any login part fails, re-render the page with the submitted_role
        return render_template('login.html', title='Login', form=form, role=submitted_role)

    # Get the intended role from the URL (e.g., /login?role=admin)
    intended_role = request.args.get('role', 'user')
    return render_template('login.html', title='Login', form=form, role=intended_role)

@main.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# --- Welcome Page ---
@main.route("/")
@main.route("/welcome")
def welcome():
    # If user is already logged in, just send them to the main app
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    # Otherwise, show the new welcome page
    return render_template('welcome.html', title='Welcome')


# --- Main Home Route ---
@main.route("/home")
@login_required
def home():
    # Query all *upcoming* events, sorted by date
    today = datetime.date.today()
    events = Event.query.filter(Event.date >= today).order_by(Event.date.asc()).all()
    
    return render_template('home.html', title='Home', events=events)

@main.route("/event/<int:event_id>")
@login_required
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    current_rsvp = RSVP.query.filter_by(
        user_id=current_user.id,
        event_id=event.id
    ).first()
    
    # Pass today's date to the template
    return render_template('event_detail.html', 
                            title=event.title, 
                            event=event, 
                            current_rsvp=current_rsvp, 
                            today=datetime.date.today())

@main.route("/event/<int:event_id>/rsvp", methods=['POST'])
@login_required
def rsvp(event_id):
    event = Event.query.get_or_404(event_id)
    status = request.form.get('status') # Gets 'Going', 'Maybe', or 'Decline'

    if not status or status not in ['Going', 'Maybe', 'Decline']:
        flash('Invalid RSVP status.', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))

    # Check if event date has already passed
    if event.date < datetime.date.today():
        flash('This event has already passed. You can no longer RSVP.', 'info')
        return redirect(url_for('main.event_detail', event_id=event_id))

    # Find if an RSVP already exists
    existing_rsvp = RSVP.query.filter_by(
        user_id=current_user.id,
        event_id=event.id
    ).first()
    
    if existing_rsvp:
        # Update existing RSVP
        existing_rsvp.status = status
        flash('Your RSVP has been updated!', 'success')
    else:
        # Create new RSVP
        new_rsvp = RSVP(
            user_id=current_user.id,
            event_id=event.id,
            status=status
        )
        db.session.add(new_rsvp)
        flash('Thank you for your RSVP!', 'success')
        
    db.session.commit()
    return redirect(url_for('main.event_detail', event_id=event_id))


@main.route("/my_rsvps")
@login_required
def my_rsvps():
    # Query all RSVPs for the current user
    # Join with the Event model to allow sorting by the event's date
    rsvps = RSVP.query.join(Event).filter(
        RSVP.user_id == current_user.id
    ).order_by(Event.date.asc()).all()
    
    return render_template('my_rsvps.html', title='My RSVPs', rsvps=rsvps)


# --- Admin Routes ---
@main.route("/event/new", methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            location=form.location.data,
            admin_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Your event has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_event.html', title='New Event', form=form)

@main.route("/event/<int:event_id>/update", methods=['GET', 'POST'])
@login_required
@admin_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    # Ensure only the admin who created it can update it
    if event.admin.id != current_user.id:
        abort(403)
        
    form = EventForm()
    if form.validate_on_submit():
        # Update event fields
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.location = form.location.data
        db.session.commit()
        flash('Your event has been updated!', 'success')
        return redirect(url_for('main.home')) # Or event detail page
    elif request.method == 'GET':
        # Pre-populate form with existing data
        form.title.data = event.title
        form.description.data = event.description
        form.date.data = event.date
        form.start_time.data = event.start_time
        form.end_time.data = event.end_time
        form.location.data = event.location
        
    return render_template('create_event.html', title='Update Event', form=form)

@main.route("/event/<int:event_id>/delete", methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.admin.id != current_user.id:
        abort(403)
    
    # cascade='all, delete-orphan' in models.py will auto-delete RSVPs
    db.session.delete(event)
    db.session.commit()
    flash('The event has been deleted.', 'success')
    return redirect(url_for('main.home'))

@main.route("/event/<int:event_id>/summary")
@login_required
@admin_required
def event_summary(event_id):
    event = Event.query.get_or_404(event_id)
    if event.admin.id != current_user.id:
        abort(403)
        
    # Query to count RSVPs grouped by status
    rsvp_summary = db.session.query(
        RSVP.status, func.count(RSVP.id)
    ).filter(RSVP.event_id == event_id).group_by(RSVP.status).all()

    # Convert to a simple dictionary for the template
    summary_counts = {status: count for status, count in rsvp_summary}
    
    counts = {
        'Going': summary_counts.get('Going', 0),
        'Maybe': summary_counts.get('Maybe', 0),
        'Decline': summary_counts.get('Decline', 0)
    }
    
    return render_template('event_summary.html', title='RSVP Summary', event=event, counts=counts)