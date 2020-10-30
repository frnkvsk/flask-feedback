from unittest import TestCase
from app import app
from models import db, User, Feedback
from forms import LoginForm, RegisterForm, FeedbackForm
from flask import session
app.config['SQLALCHEMY_DATATBASE_URI'] = 'postgresql:///feedback_test'
app.config['SQLALCHEMY_ECHO'] = False



db.drop_all()
db.create_all()

class AppTestCase(TestCase):
    """
    Note: models.py unittest has been conducted and all passed. Use model.py functions for simplicity.
    """
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        """Create Mock data"""
        self.mockLoginForm = {"username": "TestUsername1", "password": "Password1"}
        
        self.mockRegisterForm = {"username": "TestUsername1", "password": "Password1", "email": "Test@test.com", "first_name": "TestFirstname", "last_name": "TestLastname"}
        
        self.mockFeedbackForm = {"title": "TestTitle", "content": "TestContent"}
        
        """Clean up any unwanted data"""
        User.query.delete()
        Feedback.query.delete()
        
        """Create a user for testing"""
        user = User.register_user("TestUsername1","Password1", "Test@test.com", "TestFirstname", "TestLastname")
        self.username = user.username
        
        feedback = Feedback.create_feedback("TestFeedback1", "TestTitle1", self.username)
        self.feedback_id = feedback.id
        
    def tearDown(self):
        db.session.rollback()
        
    # -------------Test app.py-----------------------
    
    def test_do_home(self):
        with app.test_client() as client:
            """Test with no session username set"""
            resp = client.get("/", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('h1 class="display-4">Register</h1>', html)
            
    def test_register(self):
        with app.test_client() as client:
            """Test GET"""
            resp = client.get("/register", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('h1 class="display-4">Register</h1>', html)            
            """
            Test POST 
            Set session variable by logging in the user
            """
            client.post("/login", data=self.mockLoginForm)
            resp = client.post("/register", data=self.mockRegisterForm, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-4">Welcome', html)
            
            """Clean up logout"""
            client.get("/logout")
            
    def test_login(self):
        with app.test_client() as client:
            """Test GET"""
            resp = client.get("/login", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p class="lead">Welcome! Please log in.</p>', html)
             
            """Test POST"""
            resp = client.post("/login", data=self.mockLoginForm, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-4">Welcome', html)
            
            """Test GET while logged in - should redirect to secret.html instead of login.html"""
            resp = client.get("/login", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-4">Welcome', html)
            
            """Clean up logout"""
            client.get("/logout")
            
    def test_secret(self):
        with app.test_client() as client:
            """Test while not logged in - should redirect to register page"""
            resp = client.get(f"/users/{self.username}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p class="lead">Register for our site.</p>', html)
            
            """Test while logged in - should render template secret.html"""
            client.post("/login", data=self.mockLoginForm)
            resp = client.get(f"/users/{self.username}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-4">Welcome', html)
            
            """Clean up logout"""
            client.get("/logout")
            
    def test_delete_user(self):
        with app.test_client() as client:            
            """Set the session variable to be deleted then test delete"""
            client.post("/login", data=self.mockLoginForm)
            before = db.session.query(User).count()
            resp = client.post(f"/users/{self.username}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            after = db.session.query(User).count()
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p class="lead">Register for our site.</p>', html)
            self.assertEqual(before - 1, after)
            
    def test_add_feedback(self):
        with app.test_client() as client:
            """Test GET"""
            client.post("/login", data=self.mockLoginForm)
            resp = client.get(f"/users/{self.username}/feedback/add", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-4">Add Feedback</h1>', html)
            
            """Test POST"""
            before = db.session.query(Feedback).count()
            resp = client.post(f"/users/{self.username}/feedback/add", data=self.mockFeedbackForm, follow_redirects=True)
            html = resp.get_data(as_text=True)
            after = db.session.query(Feedback).count()
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-4">Welcome', html)
            self.assertEqual(before + 1, after)
            
            """Clean up logout"""
            client.get("/logout")
            
    def test_update_feedback(self):
        with app.test_client() as client:
            """Test GET"""
            client.post("/login", data=self.mockLoginForm)
            resp = client.get(f"/feedback/{self.feedback_id}/update", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-4">Update Feedback</h1>', html)
            
            """Test POST"""
            before = db.session.query(Feedback).first()
            before_title = before.title
            self.mockFeedbackForm["title"] = "ChangedTitle"
            resp = client.post(f"/feedback/{self.feedback_id}/update", data=self.mockFeedbackForm, follow_redirects=True)
            html = resp.get_data(as_text=True)
            after = db.session.query(Feedback).first()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(before.id, after.id)
            self.assertNotEqual(before.title, after.title)
            
            """Clean up logout"""
            client.get("/logout")
            
    def test_delete_feedback(self):
        with app.test_client() as client:
            client.post("/login", data=self.mockLoginForm)
            feedback = db.session.query(Feedback).first()
            before = db.session.query(Feedback).count()
            resp = client.post(f"/feedback/{feedback.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            after = db.session.query(Feedback).count()
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-4">Welcome', html)
            self.assertEqual(before - 1, after)