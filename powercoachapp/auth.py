import functools
from flask import Blueprint, flash, g, redirect, request, session, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from powercoachapp.extensions import db
from powercoachapp.sqlmodels import User


authbp = Blueprint('auth', __name__, url_prefix='/auth')

#Defining access protection decorator:
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
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

    if user is None or not user.check_password(password):
        return jsonify({"login_message": "Please enter a valid username and password"}), 401
    
    return jsonify({
        "login_message": "Login successful",
        "token": f"mock-jwt"
    }), 200

#KNOW HOW THESE TWO VIEWS WORK LATER:
#Register view:
@authbp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            return jsonify({'login_message': 'Username is required.'})
        elif not password:
            return jsonify({'login_message': 'Password is required.'})

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return jsonify(...)

@authbp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        
@authbp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))