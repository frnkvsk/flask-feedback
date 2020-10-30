from unittest import TestCase
from app import app
from models import db, User, Feedback
from flask_bcrypt import Bcrypt 

bcrypt = Bcrypt()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///user_feedback'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    
    # ---------------Set up---------------------
    def setUp(self):
        User.query.delete()
        hashed = bcrypt.generate_password_hash("TestPassword")
        hashed_utf8 = hashed.decode("utf8")
        user = User(username="TestUser", password=hashed_utf8, email="TestEmail@email.com", first_name="TestFirstName", last_name="TestFirstName")
        db.session.add(user)
        db.session.commit()
        self.user_password = "TestPassword"
    def tearDown(self):
        db.session.rollback()
        
    # ------------Test Models-------------------
    # ------------Test User---------------------
    def test_register_user(self):
        user1 = User.register_user("TestUser2", "TestPassword2", "TestEmail2@email.com", "TestFirstName2", "TestLastName2")
        # try to register with same username
        user2 = User.register_user("TestUser2", "TestPassword3", "TestEmail3@email.com", "TestFirstName3", "TestLastName3")
        # try to register with same email
        user3 = User.register_user("TestUser3", "TestPassword3", "TestEmail2@email.com", "TestFirstName3", "TestLastName3")
        self.assertTrue(user1)
        self.assertFalse(user2)
        self.assertFalse(user3)
    
    def test_authenticate(self):
        user = db.session.query(User).first()
        auth = User.authenticate(user.username, self.user_password)
        self.assertTrue(auth)
        
    def test_get_user_by_username(self):
        user = db.session.query(User).first()
        username = user.username
        user = User.get_user_by_username(username)
        self.assertEqual(username, user.username)
    
    def test_update_user(self):
        # test changing only username
        from_user = db.session.query(User).first()
        test_username = from_user.username
        test_email = from_user.email
        test_first = from_user.first_name
        test_last = from_user.last_name
        to_user = User(username="NewUsername1", password="TestPassword", email=from_user.email, first_name=from_user.first_name, last_name=from_user.last_name)
        user = User.update_user(from_user, to_user)
        self.assertNotEqual(test_username, user.username)
        self.assertTrue(bcrypt.check_password_hash(user.password, "TestPassword"))
        self.assertEqual(test_email, user.email)
        self.assertEqual(test_first, user.first_name)
        self.assertEqual(test_last, user.last_name)
        
        # test changing everything but username
        from_user = db.session.query(User).first()
        test_username = from_user.username
        hashed = bcrypt.generate_password_hash("newpw2")
        newpw1 = hashed.decode("utf8")
        test_password = from_user.password
        test_email = from_user.email
        test_first = from_user.first_name
        test_last = from_user.last_name
        to_user = User(username=test_username, password=newpw1, email="newemail@email.com", first_name="NewFirst", last_name="NewLast")
        user = User.update_user(from_user, to_user)
        self.assertEqual(test_username, user.username)
        self.assertNotEqual(test_password, user.password)
        self.assertNotEqual(test_email, user.email)
        self.assertNotEqual(test_first, user.first_name)
        self.assertNotEqual(test_last, user.last_name)
        
    def test_delete_user(self):
        before = db.session.query(User).count()
        user = db.session.query(User).first()
        User.delete_user(user.username)
        after = db.session.query(User).count()
        self.assertEqual(before - 1, after)
        
    # ------------Test Feedback-----------------
    def test_create_feedback(self):
        before = db.session.query(Feedback).count()
        user = db.session.query(User).first()
        feedback = Feedback.create_feedback("NewFeedbackTitle", "NewFeedbackContent", user.username)
        after = db.session.query(Feedback).count()
        test_feedback = db.session.query(Feedback).first()
        self.assertEqual(before + 1, after)
        self.assertEqual(feedback.title, test_feedback.title)
        self.assertEqual(feedback.content, test_feedback.content)
        self.assertEqual(feedback.username, test_feedback.username)
        
    def test_get_feedback_by_username(self):
        user = db.session.query(User).first()
        feedback = Feedback.create_feedback("NewFeedbackTitle", "NewFeedbackContent", user.username)
        test_feedback = Feedback.get_feedback_by_username(user.username)
        self.assertEqual(user.username, test_feedback[0].username)
    
    def test_get_feedback_by_id(self):
        user = db.session.query(User).first()        
        feedback = Feedback.create_feedback("NewFeedbackTitle", "NewFeedbackContent", user.username)
        test_feedback = Feedback.get_feedback_by_id(feedback.id)
        self.assertEqual(feedback.id, test_feedback.id)
    
    def test_authenticate_feedback(self):
        user = db.session.query(User).first()
        feedback = Feedback.create_feedback("NewFeedbackTitle", "NewFeedbackContent", user.username)
        auth = Feedback.authenticate(str(feedback.id), user.username)
        self.assertTrue(auth)
     
    def test_update_feedback(self):
        user = db.session.query(User).first()
        feedback = Feedback.create_feedback("NewFeedbackTitle", "NewFeedbackContent", user.username)
        test_title = feedback.title
        test_content = feedback.content
        Feedback.update_feedback(feedback.id, "UpdatedTitle", "UpdatedContent")
        test_feedback = db.session.query(Feedback).first()
        self.assertEqual(feedback.id, test_feedback.id)
        self.assertNotEqual(test_title, test_feedback.title)
        self.assertNotEqual(test_content, test_feedback.content)
        
    def test_delete_feedback(self):        
        user = db.session.query(User).first()
        feedback = Feedback.create_feedback("NewFeedbackTitle", "NewFeedbackContent", user.username)
        before = db.session.query(Feedback).count()
        feedback = db.session.query(Feedback).first()
        Feedback.delete_feedback(feedback.id)
        after = db.session.query(Feedback).count()
        self.assertEqual(before - 1, after)