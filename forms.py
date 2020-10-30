from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, PasswordField, IntegerField, TextAreaField, validators, HiddenField


class LoginForm(FlaskForm):
    username = StringField("Username", [validators.required(), validators.length(max=20)])
    password = PasswordField("Password", [validators.required()])
    
class RegisterForm(FlaskForm):
    username = StringField("Username", [validators.required(), validators.length(max=20)])
    password = PasswordField("Password", [validators.required()])
    email = StringField("Email", [validators.required(), validators.length(max=50)])
    first_name= StringField("First name", [validators.required(), validators.length(max=30)])
    last_name= StringField("Last name", [validators.required(), validators.length(max=30)])

class FeedbackForm(FlaskForm):
    title = StringField("Title", [validators.required(), validators.length(max=100)])
    content = TextAreaField("Content", [validators.required()])
