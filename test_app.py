import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from database.models import setup_db, db, Month, User, UserHistory, Secret

# Travel Cockpit endpoints test class
class TravelCockpitTestCase(unittest.TestCase):

    def setUp(self):
        # Define test variable and initialize app
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "travel_cockpit_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'postgres', 'secret', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        # Binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        pass


    """Endpoint testing (without login/logout)"""


    def test_start_page(self):
        res = self.client().get('/')
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('https://www.reise-klima.de/urlaub/', str(data))

    def test_404_start_page(self):
        res = self.client().get('/_')

        self.assertEqual(res.status_code, 404)

    def test_vision(self):
        res = self.client().get('/vision')
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('Vision', str(data))

    def test_404_vision(self):
        res = self.client().get('/vision_')

        self.assertEqual(res.status_code, 404)

    def test_contact(self):
        res = self.client().get('/contact')
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('Contact', str(data))

    def test_404_contact(self):
        res = self.client().get('/contact_')

        self.assertEqual(res.status_code, 404)

    def test_get_home(self):
        res = self.client().get('/home')
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('https://www.reise-klima.de/urlaub/', str(data))

    


    """CRUD endpoint testing"""






# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
