"""Handle requests on user routes"""
import os
from api import create_app, db

app = create_app(config_name=os.getenv('APP_CONFIGURATION'))

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
