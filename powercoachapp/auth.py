import functools, datetime, jwt, os
from flask import Blueprint, g, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from powercoachapp.extensions import db, logger
from powercoachapp.sqlmodels import User

SECRET_KEY = os.environ.get("SECRET_KEY")

authbp = Blueprint('auth', __name__, url_prefix='/auth')

# Defining access protection decorator:
def login_required(view):
    """
    Decorator for API routes that require user authentication.

    This decorator checks if the user's JWT is valid and if a user object
    has been loaded into the 'g' global context.
    If not, it returns a JSON response with a 401 Unauthorized status code.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # The g.user object is set by the before_app_request function below.
        if g.user is None:
            logger.info("Access denied: User not authenticated.")
            return jsonify({
                "error_message": "Unauthorized. Please log in."
            }), 401
        
        # If g.user is set, proceed to the protected view.
        return view(**kwargs)
    return wrapped_view

# This function runs before every request to check for a token
# and load the user into the 'g' object if it's valid.
@authbp.before_app_request
def load_user_from_token():
    """
    Loads a user from a JWT in the Authorization header before each request.
    """
    # Initialize g.user to None for every request
    g.user = None
    
    # Get the token from the Authorization header
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token.split(' ')[1]
        try:
            # Decode the token using the secret key and verify its signature and expiration
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # Look up the user in the database and store them in g.user
            if user_id:
                g.user = User.query.get(user_id)
            
            logger.info(f"User loaded from token: {g.user.username if g.user else 'None'}")
            
        except jwt.ExpiredSignatureError:
            # This handles cases where the token is valid but has expired
            logger.info("Token has expired.")
            g.user = None
        except jwt.InvalidTokenError as e:
            # This handles cases where the token is malformed or invalid
            logger.info(f"Invalid token: {e}")
            g.user = None

# Login Route:
@authbp.route('/login', methods=['POST'])
def login():
    """
    Authenticates a user and returns a JSON Web Token (JWT).
    NEXT UPGRADE: MAKE THIS JSON WEB TOKEN REFRESH SO IT KEEPS PERSISTING.
    """
    login_data = request.get_json()
    
    username = login_data.get('username')
    password = login_data.get('password')
    
    if not username or not password:
        return jsonify({
            'login_message': 'Username and password are required.',
            "token": None
        }), 400

    user = User.query.filter_by(username=username).first()
    
    # Check if the user exists and if the provided password matches the stored hash.
    # We use check_password_hash for secure password verification.
    if user is None or not check_password_hash(user.password, password):
        return jsonify({
            "login_message": "Invalid username or password",
            "token": None
        }), 401
    
    # If authentication is successful, generate a JWT.
    # The payload includes the user ID and an expiration time.
    payload = {
        'user_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    logger.info(f"User logged in successfully: {user.username}. JWT generated.")
    
    return jsonify({
        "login_message": "Login successful",
        "token": token
    }), 200

# Logout Route:
@authbp.route('/logout')
def logout():
    """
    For stateless token-based authentication, logout simply returns a success message.
    The client is responsible for discarding the token.
    """
    # The client simply needs to discard the token. No server-side action is needed.
    return jsonify({
        "logout_message": "Logout successful"
    }), 200

# Register view:
@authbp.route('/signup', methods=['POST'])
def signup():
    """
    Registers a new user and securely stores their password.
    """
    signup_data = request.get_json()
    
    signup_username = signup_data.get('signUpUsername')
    signup_password = signup_data.get('signUpPassword')
    
    if not signup_username or not signup_password:
        return jsonify({'signup_message': 'Username and password are required.'}), 400
    
    if User.query.filter_by(username=signup_username).first():
        return jsonify({
            "signup_message": "Username is already taken"
        }), 409
    
    try:
        hashed_password = generate_password_hash(signup_password)
        
        new_user = User(
            username=signup_username,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"New user signed up successfully: {signup_username}")
        
        return jsonify({
            "signup_message": "Signup successful"
        }), 201
    except Exception as e:
        logger.error(f"Signup failed: {e}")
        return jsonify({
            "signup_message": "Signup failed due to an unexpected error."
        }), 500
        
        
        
#OLD SESSION-BASED IMPLEMENTATION:
# import functools
# from flask import Blueprint, g, redirect, request, session, url_for, jsonify
# from werkzeug.security import check_password_hash, generate_password_hash
# from powercoachapp.extensions import db, logger
# from powercoachapp.sqlmodels import User

# authbp = Blueprint('auth', __name__, url_prefix='/auth')

# #Defining access protection decorator:
# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             logger.info("g.user not set. Token is missing or invalid.")
#             return jsonify({
#                 "error_message": "Unauthorized. Please log in."
#             }), 401
#         return view(**kwargs)
#     return wrapped_view

# # This function runs before every request to check for a token
# # and load the user into the 'g' object if it's valid.
# @authbp.before_app_request
# def load_user_from_token():
#     # Initialize g.user to None for every request
#     g.user = None
    
#     # Get the token from the Authorization header
#     token = request.headers.get('Authorization')
#     if token and token.startswith('Bearer '):
#         token = token.split(' ')[1]
#         try:
#             # Decode the token using the secret key
#             payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
#             user_id = payload.get('user_id')
            
#             # Look up the user in the database and store them in g.user
#             if user_id:
#                 g.user = User.query.get(user_id)
            
#             logger.info(f"User loaded from token: {g.user.username if g.user else 'None'}")
            
#         except jwt.ExpiredSignatureError:
#             logger.info("Token has expired.")
#             g.user = None
#         except jwt.InvalidTokenError as e:
#             logger.info(f"Invalid token: {e}")
#             g.user = None

# #Login Route:
# @authbp.route('/login', methods=['POST'])
# def login():
#     login_data = request.get_json()
    
#     username = login_data['username']
#     password = login_data['password']
    
#     if not username:
#         return jsonify({'login_message': 'Username is required.'})
#     elif not password:
#         return jsonify({'login_message': 'Password is required.'})
    
#     user = User.query.filter_by(username=username).first()
#     session['user_id'] = user.id
#     logger.info(f"USER LOGGED IN WITH ID: {session['user_id']}")
    
#     if user is None or user.password != password:
#         return jsonify({"login_message": "Please enter a valid username and password"}), 401
    
#     return jsonify({
#         "login_message": "Login successful",
#         "token": f"mock-jwt"
#     }), 200
    
# @authbp.route('/logout')
# @login_required
# def logout():
#     session.clear()
#     return jsonify({
#         "logout_message": "Logout successful"
#     }), 200

# #Register view:
# @authbp.route('/signup', methods=['POST'])
# def signup():
#     signup_data = request.get_json()
    
#     signup_username = signup_data['signUpUsername']
#     signup_password = signup_data['signUpPassword']
    
#     if not signup_username:
#         return jsonify({'signup_message': 'Username is required.'})
#     elif not signup_password:
#         return jsonify({'signup_message': 'Password is required.'})
    
#     try:
#         if not User.query.filter_by(username=signup_username).first():            
#             new_user = User(
#                 username=signup_username,
#                 password=signup_password  # or whatever password you want
#             )
#             db.session.add(new_user)
#             db.session.commit()
            
#             return jsonify({
#                 "signup_message": "Signup successful"
#             }), 201
#         else:
#             return jsonify({
#                 "signup_message": "Username is taken"
#             }), 409
#     except:
#         return jsonify({
#             "signup_message": "Please enter a valid username (32 chars max) and password (32 chars max)"
#         }), 500