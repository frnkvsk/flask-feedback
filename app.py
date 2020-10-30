from flask import Flask, request, redirect, render_template, url_for, session, flash
from models import db, connect_db, User, Feedback
from forms import LoginForm, RegisterForm, FeedbackForm
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///user_feedback')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '123default456key')

connect_db(app)

@app.errorhandler(404)
def error404(error):
    return "<h1>Feedback not found</h1>", 404

@app.errorhandler(401)
def error401(error):
    return "<h1>User not authorized</h1>", 401

@app.route("/")
def do_home():   
    # session.pop("user_id") 
    return redirect(url_for("register"))
    
@app.route("/register", methods=['GET', 'POST'])
def register():
    """Register a new user"""
    loggedin = session.get("user_id")
    if loggedin != None:
        return redirect(url_for("secret", username=loggedin))
    
    form = RegisterForm()    
    if form.validate_on_submit():
        usr = form.username.data
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        reg = User.register_user(usr, pwd, email, first_name, last_name)
        if reg:
            session["user_id"] = first_name
            return redirect(url_for("secret", username=first_name))
        else:
            flash("Username and email must be unique")
    return render_template("register.html", form=form, user=False)            
        
@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login a user"""
    loggedin = session.get("user_id")
    if loggedin != None:
        return redirect(url_for("secret", username=loggedin))
    form = LoginForm()
    if form.validate_on_submit():
        usr = form.username.data
        pwd = form.password.data
        login = User.authenticate(usr, pwd)
        if login:
            session["user_id"] = login.username
            return redirect(url_for("secret", username=login.username))
        
        flash(u"username and password don't match", "error")
    return render_template("login.html", form=form, user=False)
        
@app.route("/users/<username>")
def secret(username):
    loggedin = session.get("user_id")
    if loggedin == username:
        user = User.get_user_by_username(username)
        feedback = Feedback.get_feedback_by_username(username)
        return render_template("secret.html", user=user, feedback=feedback)
    else:
        return redirect(url_for("register"))    

@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    """Remove the user from the database and make sure to also delete all of their feedback. Remove the user from the database and make sure to also delete all of their feedback. Clear any user information in the session and redirect to /. Make sure that only the user who is logged in can successfully delete their account"""
    session.pop("user_id")
    User.delete_user(username)
    return redirect(url_for("do_home"))

@app.route("/users/<username>/feedback/add", methods=['GET', 'POST'])
def add_feedback(username):
    """
    GET - Display a form to add feedback Make sure that only the user who is logged in can see this form
    POST - Add a new piece of feedback and redirect to /users/<username> — Make sure that only the user who is logged in can successfully add feedback
    """
    loggedin = session.get("user_id")
    if loggedin != username:
        return redirect(url_for("do_home"))
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback.create_feedback(title, content, username)
        return redirect(url_for("do_home"))
    else:
        return render_template("add_feedback.html", form=form, username=username)

@app.route("/feedback/<feedback_id>/update", methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """
    GET - Display a form to edit feedback — **Make sure that only the user who has written that feedback can see this form **
    POST - Update a specific piece of feedback and redirect to /users/<username> — Make sure that only the user who has written that feedback can update it
    """
    username = session.get("user_id")    
    if Feedback.authenticate(feedback_id, username) == False:
        return redirect(url_for("do_home"))
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback.update_feedback(feedback_id, title, content)
        return redirect(url_for("do_home"))
    else:
        feedback = Feedback.get_feedback_by_id(feedback_id)
        return render_template("update_feedback.html", form=form, feedback=feedback)    
        
@app.route("/feedback/<feedback_id>/delete", methods=['POST'])
def delete_feedback(feedback_id):
    """
    POST - Delete a specific piece of feedback and redirect to /users/<username> — Make sure that only the user who has written that feedback can delete it
    """    
    username = session.get("user_id")
    if Feedback.authenticate(feedback_id, username) == False:
        return redirect(url_for("do_home"))
    
    if request.method == 'POST':
        Feedback.delete_feedback(feedback_id)
    return redirect(url_for("do_home"))

@app.route("/logout")
def logout():
    session.pop("user_id")
    return redirect(url_for("register"))


