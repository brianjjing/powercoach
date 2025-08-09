import functools
from flask import Blueprint, g, redirect, request, session, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from powercoachapp.extensions import db, logger
from powercoachapp.sqlmodels import User

authbp = Blueprint('auth', __name__, url_prefix='/auth')

#Defining access protection decorator:
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            logger.info("g.user not set")
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

#Login Route:
@authbp.route('/login', methods=['POST'])
def login():
    login_data = request.get_json()
    
    username = login_data['username']
    password = login_data['password']
    
    if not username:
        return jsonify({'login_message': 'Username is required.'})
    elif not password:
        return jsonify({'login_message': 'Password is required.'})
    
    user = User.query.filter_by(username=username).first()
    session['user_id'] = user.id
    logger.info(f"USER LOGGED IN WITH ID: {session['user_id']}")
    
    if user is None or user.password != password:
        return jsonify({"login_message": "Please enter a valid username and password"}), 401
    
    return jsonify({
        "login_message": "Login successful",
        "token": f"mock-jwt"
    }), 200
    
@authbp.route('/logout')
@login_required
def logout():
    session.clear()
    return jsonify({
        "logout_message": "Logout successful"
    }), 200

#Register view:
@authbp.route('/signup', methods=['POST'])
def signup():
    signup_data = request.get_json()
    
    signup_username = signup_data['signUpUsername']
    signup_password = signup_data['signUpPassword']
    
    if not signup_username:
        return jsonify({'signup_message': 'Username is required.'})
    elif not signup_password:
        return jsonify({'signup_message': 'Password is required.'})
    
    try:
        if not User.query.filter_by(username=signup_username).first():            
            new_user = User(
                username=signup_username,
                password=signup_password  # or whatever password you want
            )
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                "signup_message": "Signup successful"
            }), 201
        else:
            return jsonify({
                "signup_message": "Username is taken"
            }), 409
    except:
        return jsonify({
            "signup_message": "Please enter a valid username (32 chars max) and password (32 chars max)"
        }), 500