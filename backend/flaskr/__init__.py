import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from werkzeug.exceptions import HTTPException

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  setup_db(app)
  cors = CORS(app, resources={r'/api/*': {"origins": "*"}})
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response
        

  @app.route('/categories', methods=['GET'])
  def get_categories():
    all_categories = [category.format() for category in Category.query.all()]
    return jsonify({"Success": True, "categories": all_categories})


  @app.route('/questions', methods=['GET'])
  def get_questions():
    data = request.args.get('page', 0, type=int)
    start = data * QUESTIONS_PER_PAGE 
    end = (data+1) * QUESTIONS_PER_PAGE
    all_questions = Question.query.all()
    targeted_questions = all_questions[start: end]
    all_categories = [category.type for category in Category.query.all()]
    if len(all_categories) == 0:
      abort(404)
    else:
      results= {
                "Success": True,
                "questions" : [question.format() for question in targeted_questions],
                "total_questions" : len(all_questions),
                "categories" : all_categories,
                "current_category" : None # What Does this field mean!
                }
      return jsonify(results)

  @app.route('/questions/<int:question_id>', methods=["DELETE"])
  def delete_question(question_id):
    question = Question.query.filter_by(id=question_id).one_or_none()
    if question:
      question.delete()
      return jsonify({"Success": True, 'Message': 'item deleted!'})
    else:
      abort(404)


  @app.route('/questions', methods=["POST"])
  def add_question():
    data = request.get_json()
    if 'searchTerm' in data:
      search_term = data['searchTerm']
      all_question = Question.query.filter(Question.question.ilike("%" + search_term + "%")).all()
      result = {'Success': True,
                'questions': [question.format() for question in all_question],
                'totalQuestions': Question.query.count(),
                'currentCategory': None # What!
                }
      return jsonify(result)
    else:
      if 'question' in data:
        question = data.get('question')
      else: 
        abort(404)
      if 'answer' in data:
        answer = data.get('answer')
      else:
        abort(404)
      if 'difficulty' in data:
        difficulty = data.get('difficulty')
      else:
        abort(404)
      if 'category' in data:
        category = data.get('category')
      else:
        abort(404)
      QUESTION = Question(question = question,
                          answer = answer,
                          category = category,
                          difficulty= difficulty)
      QUESTION.insert()
      return jsonify({
                      "Success": True,
                      "Message": "Question Added!"
                      })


  @app.route('/categories/<int:cat_id>/questions')
  def get_questions_cat_based(cat_id):
    questions_in_cat = Question.query.filter_by(category=cat_id).all()
    result = {'Success': True,
              'questions': [question.format() for question in questions_in_cat],
              'total_questions': Question.query.count(),
              'current_category': Category.query.filter_by(id=cat_id).one().type
              }
    return jsonify(result)

  @app.route('/quizzes', methods=["POST"])
  def get_play_question():
    data = request.get_json()
    previous_questions = data.get('previous_questions', [])
    quiz_category = data.get('quiz_category')['id']
    if quiz_category == "All":
      all_question = Question.query.all()
    else:
      all_question = Question.query.filter_by(category=quiz_category)
    to_choose = [item.format() for item in all_question if not (item.question in previous_questions)]
    if len(to_choose) != 0:
      result ={
              'Success': True,
              "question": random.choice(to_choose),
              }
    else:
      result ={
              'Success': True,
              "question": None,
              }
    return jsonify(result)

  @app.errorhandler(404)
  def get_not_found(error):
    return jsonify({"Success": False, "Error": 404, "message": "resource not found"}), 404
  @app.errorhandler(422)
  def get_unprocessable_entity(error):
    return jsonify({"Success": False,
                    "Error": 422,
                    "message": "unaccesable entity"}), 422
  return app

  

    