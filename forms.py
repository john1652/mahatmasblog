from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import re

def validate_password_strength(form, field):
    """Custom validator for password strength"""
    password = field.data
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one number')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character')

def validate_username(form, field):
    """Custom validator for username"""
    username = field.data
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError('Username can only contain letters, numbers, and underscores')
    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters long')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20),
        validate_username
    ])
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        validate_password_strength
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=5, max=100)
    ])
    blog_category = SelectField('Category', choices=[
        ('Top 10s', 'Top 10s'),
        ('John\'s Journeys', 'John\'s Journeys'),
        ('Moments to Memories', 'Moments to Memories'),
        ('Reviews', 'Reviews')
    ], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    body = TextAreaField('Content', validators=[
        DataRequired(),
        Length(min=10, message='Blog post must be at least 10 characters long')
    ])
    blog_type = SelectField('Type', choices=[
        ('published', 'Published'),
        ('draft', 'Draft'),
        ('private', 'Private')
    ], validators=[DataRequired()])

class EditBlogPostForm(FlaskForm):
    user_id = SelectField('Select User', coerce=int, validators=[
        DataRequired(message='Please select a user')
    ])
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=5, max=100, message='Title must be between 5 and 100 characters long')
    ])
    blog_category = SelectField('Category', choices=[
        ('Top 10s', 'Top 10s'),
        ('John\'s Journeys', 'John\'s Journeys'),
        ('Moments to Memories', 'Moments to Memories'),
        ('Reviews', 'Reviews')
    ], validators=[DataRequired(message='Please select a category')])
    date = DateField('Date', validators=[DataRequired(message='Please select a date')])
    body = TextAreaField('Content', validators=[
        DataRequired(),
        Length(min=10, message='Blog post must be at least 10 characters long')
    ])
    blog_type = SelectField('Type', choices=[
        ('published', 'Published'),
        ('draft', 'Draft'),
        ('private', 'Private')
    ], validators=[DataRequired(message='Please select a post type')]) 