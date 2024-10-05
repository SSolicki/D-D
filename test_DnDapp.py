import unittest
from flask_testing import TestCase
from DnDapp import app, db, User, Character, Campaign

class DnDappTestCase(TestCase):
    """Test Case for the DnDapp Flask application."""

    def create_app(self):
        """Configure the Flask application for testing."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        """Set up the test database and client before each test."""
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        """Tear down the test database after each test."""
        db.session.remove()
        db.drop_all()

    def test_home(self):
        """Test the home page."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        """Test user registration."""
        # Successful registration
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful. Please log in.', response.data)

        # Attempt to register with the same email
        response = self.client.post('/register', data={
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.assertIn(b'Email is already registered. Please log in or use a different email.', response.data)

    def test_login(self):
        """Test user login."""
        # First, register a user
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

        # Test correct login
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.assertIn(b'Login successful.', response.data)

        # Test login with wrong password
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Login failed. Please check your email and password.', response.data)

    def test_logout(self):
        """Test user logout."""
        # Register and login a user
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out.', response.data)

    def test_character_creation(self):
        """Test accessing the character creation page."""
        # Register and login
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

        # Access character creation page
        response = self.client.get('/character_creation')
        self.assertEqual(response.status_code, 200)

    def test_save_character(self):
        """Test saving a character."""
        # Register and login
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

        # Save a valid character
        response = self.client.post('/save_character', data={
            'name': 'Test Character',
            'class': 'Warrior',
            'race': 'Elf',
            'strength': 15,
            'dexterity': 14,
            'intelligence': 13
        }, follow_redirects=True)
        self.assertIn(b'Character saved successfully', response.data)

        # Attempt to save a character with invalid strength
        response = self.client.post('/save_character', data={
            'name': 'Test Character',
            'class': 'Warrior',
            'race': 'Elf',
            'strength': 25,  # Assuming max strength is 20
            'dexterity': 14,
            'intelligence': 13
        }, follow_redirects=True)
        self.assertIn(b'Error saving character', response.data)

    def test_view_characters(self):
        """Test viewing characters."""
        # Register and login
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

        # View characters
        response = self.client.get('/characters')
        self.assertEqual(response.status_code, 200)

    def test_create_campaign(self):
        """Test creating a campaign."""
        # Register and login
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

        # Create a campaign
        response = self.client.post('/create_campaign', data={
            'name': 'Test Campaign',
            'description': 'A test campaign'
        }, follow_redirects=True)
        self.assertIn(b'Campaign created successfully', response.data)

    def test_join_campaign(self):
        """Test joining a campaign."""
        # Register and login
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

        # Create a campaign
        with self.app.app_context():
            campaign = Campaign(owner_id=1, name='Test Campaign', description='A test campaign')
            db.session.add(campaign)
            db.session.commit()

        # Join the campaign
        response = self.client.get(f'/join_campaign/{campaign.id}', follow_redirects=True)
        self.assertIn(b'Successfully joined the campaign.', response.data)

    def test_dice_roll(self):
        """Test dice rolling functionality."""
        # Register and login
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

        # Perform a dice roll
        response = self.client.get('/dice_roll?type=d20')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'result', response.data)

    def test_update_battle_map(self):
        """Test updating the battle map."""
        # Register and login
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

        # Update battle map
        response = self.client.post('/update_battle_map', json={
            'map_data': 'test_data'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Battle map updated successfully', response.data)

    def test_participating_campaigns(self):
        """Test viewing participating campaigns."""
        # Register and login
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

        # View participating campaigns
        response = self.client.get('/participating_campaigns')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
