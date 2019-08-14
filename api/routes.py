"""we_connect/routes.py."""
from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from datetime import timedelta
from functools import wraps
import jwt
import re

# local imports
from .models import User
from .models import Business
from .models import Review
from .validators import Validator
from .run import app
from .models import db

validator = Validator()


def token_required(f):
    """Decorate a function to use a jwt token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({
                'msg': 'Token is missing, login to get a token'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.get_user(data['username'])
            if not current_user.logged_in_token:
                current_user = None
        except:
            return jsonify({
                'msg': 'Token is invalid, login to get another token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


def check_for_login(f):
    """Return errors if user logged out."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not args[0]:
            return jsonify({
                'msg': 'Token is malformed, login to get another token'}), 400
        else:
            return f(*args, **kwargs)
    return decorated


def check_json(f):
    """Return errors if json is absent or wrongly formated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            content = request.get_json()
        except:
            return jsonify({'json error': 'Failed to decode JSON object'}), 400
        if not content:
            res = jsonify(
                {'json error': 'JSON object was not found in your request'})
            res.status_code = 400
            return res
        return f(content, *args, **kwargs)
    return decorated


@app.route('/api/v2/auth/register', methods=['POST'])
@check_json
def create_user(content):
    """Register a user into the API."""
    err_msg = validator.validate(content, 'user_reg')
    if err_msg:
        return jsonify(err_msg), 400
    if User.get_user(content['email'].strip()):
        return jsonify({'msg': 'Email already registered!'}), 400
    if User.get_user(content['username'].strip()):
        return jsonify({'msg': 'Username not available!'}), 400
    new_user = User(name=content['name'].strip(),
                    username=content['username'].strip(),
                    email=content['email'].strip(),
                    password=generate_password_hash(
                    content['password'].strip()))
    db.session.add(new_user)
    db.session.commit()
    created_user = User.get_user(content['email'].strip())
    print(created_user)
    message = {
        'details': {
            'name': created_user.name,
            'username': created_user.username,
            'email': created_user.email
        },
        'msg': "User {} created successfully on {}".format(
            created_user.username,
            created_user.date_created)
    }
    return jsonify(message), 201


@app.route('/api/v2/auth/login', methods=['POST'])
@check_json
def login_user(content):
    """Log in a user."""
    if 'username' not in content and 'email' not in content:
        return jsonify({
            'msg': 'Missing username or email in JSON'}), 400
    if 'password' not in content:
        return jsonify({
            'msg': 'Missing password in JSON'}), 400
    if 'username' in content:
        user = User.get_user(content['username'].strip())
    if 'email' in content:
        user = User.get_user(content['email'].strip())
    if not user:
        return jsonify({
            'msg': 'Email or username provided does not match any user'}), 400
    if check_password_hash(user.password, content['password']):
        token = jwt.encode({
            'username': user.username,
            'exp': datetime.now() + timedelta(minutes=300)},
            app.config['SECRET_KEY'])
        if user.logged_in_token:
            user.logged_in_token = token
            db.session.commit()
            return jsonify({
                'user': user.username,
                'token': token.decode('UTF-8'),
                'msg': 'Log in successful'}), 200
        user.logged_in_token = token
        db.session.commit()
        return jsonify({
            'user': user.username,
            'token': token.decode('UTF-8'),
            'msg': 'Log in successful'}), 200
    return jsonify({
        'msg': 'Wrong email or username/password combination'}), 400


@app.route('/api/v2/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Log out a user."""
    if not current_user:
        return jsonify({'msg': 'User is not logged in'}), 400
    current_user.logged_in_token = None
    db.session.commit()
    return jsonify({'msg': 'User log out successfull'}), 200


@app.route('/api/v2/auth/reset-password', methods=['POST'])
@check_json
@token_required
@check_for_login
def reset_password(current_user, content):
    """Change a password for a user."""
    to_reset = current_user
    if 'new_password' not in content:
        return jsonify({'msg': 'Missing new password'}), 400
    error = {}
    if len(str(content['new_password'].strip())) < 6:
        error['msg'] = 'Password cannot be less than 6 characters'
    if not re.compile('[0-9]').search(content['new_password'].strip()):
        error['msg'] = 'Strong password must have at least one number character'
    if not re.compile('[^\w\s]').search(content['new_password'].strip()):
        error['msg'] = 'Strong password must have at least one special character'
    if error:
        return jsonify(error), 400
    User.query.filter_by(username=current_user.username).update(
        {'password': generate_password_hash(content['new_password'].strip())})
    db.session.commit()
    message = {
        'msg': 'Password for {} changed successfully'.format(to_reset.username)
    }
    return jsonify(message), 200


@app.route('/api/v2/get-reset-token', methods=['POST'])
@check_json
def return_token(content):
    """Return a token to use to change password."""
    if 'email' in content:
        user = User.get_user(content['email'].strip())
    if not user:
        return jsonify({
            'msg': 'Email provided does not match any user'}), 400
    token = jwt.encode({
        'username': user.username,
        'exp': datetime.now() + timedelta(minutes=1440)},
        app.config['SECRET_KEY'])
    user.logged_in_token = token
    db.session.commit()
    return jsonify({
        'token': token.decode('UTF-8'),
        'email': user.email,
        'msg': 'Use this token within 24 hours to reset password'}), 200


@app.route('/api/v2/businesses', methods=['POST'])
@check_json
@token_required
@check_for_login
def register_business(current_user, content):
    """Register a business for a user."""
    err_msg = validator.validate(content, 'business_reg')
    if err_msg:
        return jsonify(err_msg), 400
    new_business = Business(name=content['name'].strip(),
                            category=content['category'].strip(),
                            description=content['description'].strip(),
                            location=content['location'].strip(),
                            owner=current_user
                            )
    db.session.add(new_business)
    db.session.commit()
    message = {'msg': "Business id {} created for owner {}".format(
        new_business.id, new_business.business_owner),
        'details': {'name': new_business.name,
                    'category': new_business.category,
                    'description': new_business.description,
                    'location': new_business.location,
                    'owner': new_business.business_owner
                    }}
    return jsonify(message), 201


@app.route('/api/v2/businesses/<business_id>', methods=['PUT'])
@check_json
@token_required
@check_for_login
def update_business(current_user, content, business_id):
    """Update an existing business."""
    message = validator.validate(content, 'business_reg')
    if message:
        return jsonify(message), 400
    to_update = Business.query.filter_by(id=business_id).first()
    if not to_update:
        return jsonify({'msg': 'Business id is incorrect'}), 400
    if not to_update.business_owner == current_user.username:
        return jsonify(
            {'msg': 'You are not allowed to edit this business'}), 403
    Business.query.filter_by(id=business_id).update(
        {
            'name': content['name'].strip(),
            'category': content['category'].strip(),
            'description': content['description'].strip(),
            'location': content['location'].strip(),
        })
    db.session.commit()
    updated_bs = Business.query.filter_by(id=business_id).first()
    message = {'msg': "Business id {} modified for owner {}".format(
        updated_bs.id, updated_bs.business_owner),
        'details': {'name': updated_bs.name,
                    'category': updated_bs.category,
                    'description': updated_bs.description,
                    'location': updated_bs.location,
                    'owner': updated_bs.business_owner,
                    'id': updated_bs.id
                    }}
    return jsonify(message), 201


@app.route('/api/v2/businesses/<business_id>', methods=['DELETE'])
@token_required
@check_for_login
def delete_business(current_user, business_id):
    """Remove an existing business."""
    to_delete = Business.query.filter_by(id=business_id).first()
    if not to_delete:
        return jsonify({'msg': 'Business id is incorrect'}), 400
    if not to_delete.business_owner == current_user.username:
        return jsonify(
            {'msg': 'You are not allowed to delete this business'}), 403
    db.session.delete(to_delete)
    db.session.commit()
    message = {'msg': 'Business id {} for owner {} deleted successfully'.
               format(to_delete.id, to_delete.business_owner),
               'details': {'name': to_delete.name,
                           'category': to_delete.category,
                           'description': to_delete.description,
                           'location': to_delete.location,
                           'owner': to_delete.business_owner,
                           'id': to_delete.id
                           }}
    return jsonify(message), 200


@app.route('/api/v2/businesses/')
def get_all_businesses():
    """Retrieve a list of all registered businesses."""
    page = 1
    limit = 5
    if 'page' in request.args:
        page = request.args.get('page', 1, type=int)
    if 'limit' in request.args:
        limit = request.args.get('limit', 5, type=int)
    businesses = Business.query.filter_by().paginate(
        page, limit, True)
    if not businesses.items:
        return jsonify({'msg': 'No businesses yet'}), 400
    message = {'businesses': [{'name': business.name,
                               'category': business.category,
                               'description': business.description,
                               'id': business.id,
                               'location': business.location,
                               'owner': business.business_owner}
                              for business in businesses.items],
               "per_page": businesses.per_page, "page": businesses.page,
               "total_pages": businesses.pages,
               "total_results": businesses.total}
    return jsonify(message), 200


@app.route('/api/v2/businesses/search', methods=['GET'])
def search_businesses():
    """Retrieve the list of all businesses."""
    name = ""
    location = ""
    category = ""
    page = 1
    limit = 5
    if 'q' in request.args:
        name = request.args.get('q')
    if 'location' in request.args:
        location = request.args.get('location')
    if 'category' in request.args:
        category = request.args.get('category')
    if 'page' in request.args:
        page = request.args.get('page', 1, type=int)
    if 'limit' in request.args:
        limit = request.args.get('limit', 5, type=int)
    businesses = db.session.query(Business).filter(
        Business.name.ilike('%{0}%'.format(name)),
        Business.location.ilike('%{0}%'.format(location)),
        Business.category.ilike('%{0}%'.format(category))).paginate(
        page, limit, True)
    if name == "" and location == "" and category == "":
        businesses = Business.query.filter_by().paginate(
            page, limit, True)
        if not businesses.items:
            return jsonify({'msg': 'No businesses yet'}), 400
    if not len(list(businesses.items)):
        return jsonify({'msg': 'No businesses match this search'}), 400
    message = {'businesses': [{'name': business.name,
                               'category': business.category,
                               'description': business.description,
                               'location': business.location,
                               'id': business.id,
                               'owner': business.business_owner}
                              for business in businesses.items],
               "per_page": businesses.per_page, "page": businesses.page,
               "total_pages": businesses.pages,
               "total_results": businesses.total}
    return jsonify(message), 200


@app.route('/api/v2/businesses/<business_id>', methods=['GET'])
def get_business(business_id):
    """Retrieve a single business."""
    business = Business.query.filter_by(id=business_id).first()
    if not business:
        return jsonify({'msg': 'Business id is incorrect'}), 400
    message = {'msg': 'Business id {} owned by {} retrieved successfully'.
               format(business.id, business.business_owner),
               'details': {'name': business.name,
                           'category': business.category,
                           'description': business.description,
                           'location': business.location,
                           'id': business.id,
                           'owner': business.business_owner
                           }}
    return jsonify(message), 200


@app.route('/api/v2/businesses/<business_id>/reviews',
           methods=['POST'])
@check_json
@token_required
@check_for_login
def add_review_for(current_user, content, business_id):
    """Add a review for a business."""
    message = validator.validate(content, 'review_reg')
    if message:
        return jsonify(message), 400
    to_review = Business.query.filter_by(id=business_id).first()
    if not to_review:
        return jsonify({'msg': 'Business id is incorrect'}), 400
    if to_review.business_owner == current_user.username:
        return jsonify({'msg': 'Reviewing own business not allowed'}), 400
    review = Review(rating=int(str(content['rating']).strip()),
                    body=content['body'].strip(),
                    owner=current_user,
                    review_for=to_review)
    db.session.add(review)
    db.session.commit()
    message = {'msg': 'Review for business id {} by user {} created'.format(
        review.business_id, review.review_owner),
        'details': {'rating': review.rating,
                    'body': review.body}}
    return jsonify(message), 201


@app.route('/api/v2/businesses/<business_id>/reviews',
           methods=['GET'])
def get_reviews_for(business_id):
    """Retrieve all reviews for a single business."""
    business = Business.query.filter_by(id=business_id).first()
    if not business:
        return jsonify({'msg': 'Business id is incorrect'}), 400
    reviews = Review.query.filter_by(business_id=business_id)
    if not reviews.count():
        return jsonify({'msg': 'No reviews for this business'}), 400
    message = {'reviews': [{'rating': review.rating,
                            'body': review.body,
                            'review_by': review.review_owner}
                           for review in reviews],
               'business_id': business.id,
               'business_owner': business.business_owner}
    return jsonify(message), 200
