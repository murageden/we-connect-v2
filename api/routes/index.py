"""Handle requests on index"""

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
