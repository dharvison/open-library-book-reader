from unittest import TestCase
from app import app

class AnonFormTest(TestCase):
    """These are mostly smoke tests to confirm the anon links are working"""

    def setUp(self):
        """setup for each test"""
        self.client = app.test_client()

    def test_home(self):
        """Test the home page"""

        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('<h2 class="join-message">', html)
            self.assertNotIn('<h2 class="welcome">', html)
    
    def test_signup(self):
        """Test the signup page"""

        with self.client:
            response = self.client.get('/signup')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('<form method="POST" id="user_form">', html)
    
    def test_login(self):
        """Test the login page"""

        with self.client:
            response = self.client.get('/login')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('<form method="POST" id="user_form">', html)
    
    def test_trending(self):
        """Test the browse page"""

        with self.client:
            response = self.client.get('/trending')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('<div id="trending-recent"', html)
            self.assertIn('<div id="trending-popular"', html)
            self.assertIn('<div id="trending-monthly"', html)

    def test_search(self):
        """Test the search page"""

        with self.client:
            response = self.client.get('/search?term=watchmen')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('<div id="search-results">', html)
            self.assertIn('watchmen', html)
