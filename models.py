from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from flask_bcrypt import Bcrypt 

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    
    __tablename__ = 'users'
    
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    feedback = db.relationship('Feedback', backref='users', passive_deletes=True)
    
    @classmethod
    def register_user(cls, usr, pwd, email, first, last):
        
        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode("utf8")
        reg_usr = cls.query.filter_by(username=usr).first()
        reg_pwd = cls.query.filter_by(password=hashed_utf8).first()
        reg_email= cls.query.filter_by(email=email).first()
        if reg_usr or reg_pwd or reg_email:
            return False
        user = User(username=usr, password=hashed_utf8, email=email, first_name=first, last_name=last)
        db.session.add(user)
        db.session.commit()
        return user
        
    @classmethod
    def authenticate(cls, usr, pwd):        
        user = User.query.filter_by(username=usr).first()                
        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else: 
            return False
    
    @classmethod
    def get_user_by_username(cls, usr):
        user = User.query.filter_by(username=usr).first()
        return user
    
    @classmethod
    def update_user(cls, from_user, to_user):
        """This function is not in use. It is just for future enhancements if needed."""
        if from_user.username != to_user.username:
            """User is changing username"""
            cls.delete_user(from_user.username)
            user = cls.register_user(to_user.username, to_user.password, to_user.email, to_user.first_name, to_user.last_name)            
            return user
        else:
            from_user.password = to_user.password
            from_user.email = to_user.email
            from_user.first_name = to_user.first_name
            from_user.last_name = to_user.last_name
            db.session.commit()
            return from_user           
        
    @classmethod
    def delete_user(cls, usr):
        user = cls.query.filter_by(username=usr).first()
        db.session.delete(user)
        db.session.commit()
        
            
class Feedback(db.Model):
    
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username', ondelete='CASCADE'))
    
    # ---------Create------------------------
    @classmethod
    def create_feedback(cls, title, content, usr):
        feedback = Feedback(title=title, content=content, username=usr)
        db.session.add(feedback)
        db.session.commit()
        return feedback
    
    # ---------Read--------------------------
    @classmethod
    def get_feedback_by_username(cls, usr):
        user = User.get_user_by_username(usr)
        if user.is_admin:
            return cls.query.all()
        
        return cls.query.filter_by(username=usr).all()
    
    @classmethod
    def get_feedback_by_id(cls, id):
        feedback = cls.query.filter_by(id=id).first()
        return feedback
    
    @classmethod
    def authenticate(cls, id, usr):
        user = User.get_user_by_username(usr)
        if user.is_admin:
            return True
        feedback = Feedback.get_feedback_by_username(usr)
        return str(id) in [str(Feedback.id) for Feedback in feedback]
        
    # ---------Update------------------------
    @classmethod
    def update_feedback(cls, id, title, content):
        feedback = Feedback.query.filter_by(id=id).first()
        feedback.title = title
        feedback.content = content
        db.session.commit()
        
    # ---------Delete------------------------
    @classmethod
    def delete_feedback(cls, id):
        feedback = Feedback.query.filter_by(id=id).first()
        db.session.delete(feedback)
        db.session.commit()