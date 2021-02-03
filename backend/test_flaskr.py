import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://rootuser:rootuser@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    
    def test_get_question(self):
        result = self.client().get('/questions?page=0')
        self.assertEqual(result.status_code, 200)
    
    def test_get_question_error(self):
        result = self.client().get('/questions?page=1000')
        self.assertEqual(result.status_code, 404)
    
    def test_get_categories(self):
        result = self.client().get('/categories')
        self.assertEqual(result.status_code, 200)

    def test_get_categories(self):
        result = self.client().get('/categs')
        self.assertEqual(result.status_code, 404)

    def test_delete_question(self):
        result = self.client().delete('/questions/20')
        self.assertEqual(result.status_code, 200)

    def test_delete_question_error(self):
        result = self.client().delete('/questions/2555555')
        self.assertEqual(result.status_code, 404)

    def test_add_question(self):
        result = self.client().post('/questions', json={"question": "are you alive?", "answer": "yes", "difficulty": 1, "category": 4})
        self.assertEqual(result.status_code, 200)
    def test_add_question_error(self):
        result = self.client().post('/questions', json={"question": "are you alive?"})
        self.assertEqual(result.status_code, 404)

    def test_search(self):
        result = self.client().post('/questions', json={"searchTerm": "are "})
        self.assertEqual(result.status_code, 200)

    def test_search_error(self):
        result = self.client().post('/questions', json={"searchterm": "are "})
        self.assertEqual(result.status_code, 404)

    def test_get_questions_cat_based(self):
        result = self.client().get('/categories/1/questions')
        self.assertEqual(result.status_code, 200)

    def test_get_questions_cat_based_error(self):
        result = self.client().get('/categories/10000/questions')
        self.assertEqual(result.status_code, 404)

    def test_get_play_question(self):
        result = self.client().post('/quizzes', json={"previous_questions":[], "quiz_category": {"type": "Art", "id":"4"}})
        self.assertEqual(result.status_code, 200)

    def test_get_play_question_error(self):
        result = self.client().post('/quizzes', json={"previous_questions":[], "quiz_category": {'type': 'Art', 'id':'514'}})
        self.assertEqual(result.status_code, 404)
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()