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
    if len(targeted_questions) == 0:
      abort(404)
    else:
      results= {
                "Success": True,
                "questions" : [question.format() for question in targeted_questions],
                "total_questions" : len(all_questions),
                "categories" : all_categories,
                "current_category" : [question.category for question in targeted_questions]
                }
      return jsonify(results)

  @app.route('/questions/<int:question_id>', methods=["DELETE"])
  def delete_question(question_id):
    question = Question.query.filter_by(id=question_id).one_or_none()
    if question:
      question.delete()
      return jsonify({"Success": True, 'Message': f'item {id} deleted!'})
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
                'currentCategory': None 
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
                          category = 1+int(category),
                          difficulty= difficulty)
      QUESTION.insert()
      return jsonify({
                      "Success": True,
                      "Message": "Question Added!"
                      })


  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def get_questions_cat_based(cat_id):
    category = Category.query.get(cat_id + 1)
    if not category:
      abort(404)
    questions_in_cat = Question.query.filter_by(category=category.id).all()
    questions_in_cat = [question.format() for question in questions_in_cat]
    result = {'Success': True,
              'questions': questions_in_cat,
              'total_questions': len(questions_in_cat),
              'current_category': category.type
              }
    return jsonify(result)

  @app.route('/quizzes', methods=["POST"])
  def get_play_question():
    data = request.get_json()
    previous_questions = data.get('previous_questions', [])
    quiz_category = (data.get('quiz_category')['id'])
    if data.get('quiz_category')['type'] == "click":
      all_question = Question.query.all()
    else:
      is_none = Category.query.filter_by(id=quiz_category).one_or_none()
      quiz_category = 1 + int(quiz_category)
      if not is_none:
        abort(404)
      all_question = Question.query.filter_by(category=quiz_category).all()
    to_choose = [item.format() for item in all_question \
                if not (item.question in previous_questions)]
    if len(to_choose) != 0:
      result = {
              'Success': True,
              "question": random.choice(to_choose),
              }
    else:
      result = {
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
  @app.errorhandler(500)
  def get_unprocessable_entity(error):
    return jsonify({"Success": False,
                    "Error": 500,
                    "message": "internal server error!"}), 500
  @app.errorhandler(400)
  def get_unprocessable_entity(error):
    return jsonify({"Success": False,
                    "Error": 400,
                    "message": "Bad Request!"}), 400
  return app