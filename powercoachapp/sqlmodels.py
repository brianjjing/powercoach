from powercoachapp.extensions import db
from flask_login import UserMixin #Defaults a lot of the parameters you need to manually set
# powercoachapp/models.py
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(40), nullable=False)