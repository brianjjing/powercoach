from flask import Blueprint, render_template

homepagebp = Blueprint("homepage", __name__)

@homepagebp.route("/")
def homepage():
    return render_template('home/homepage.html')