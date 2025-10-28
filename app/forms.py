from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    PasswordField, 
    BooleanField, 
    SubmitField, 
    TextAreaField,  # Added for EventForm
    DateField,      # Added for EventForm
    TimeField       # Added for EventForm
)
from wtforms.validators import (
    DataRequired, 
    Length, 
    Email, 
    EqualTo, 
    ValidationError
)
from app.models import User  # Needed for RegistrationForm


class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# --- This is the new class you added ---
class EventForm(FlaskForm):
    title = StringField('Event Title', 
                        validators=[DataRequired(), Length(min=3, max=140)])
    description = TextAreaField('Description', 
                                validators=[DataRequired()])
    # format matches the HTML5 date picker
    date = DateField('Event Date', 
                     format='%Y-%m-%d', 
                     validators=[DataRequired()])
    # format matches the HTML5 time picker
    start_time = TimeField('Start Time', 
                           format='%H:%M', 
                           validators=[DataRequired()])
    end_time = TimeField('End Time', 
                         format='%H:%M', 
                         validators=[DataRequired()])
    location = StringField('Location', 
                           validators=[DataRequired(), Length(min=3, max=200)])
    submit = SubmitField('Submit Event')