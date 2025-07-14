from flask import (
    Blueprint, g, render_template, request, Response, url_for
)
from werkzeug.exceptions import abort

from powercoachapplocal.bbellplaceholdermodeltest import powercoachalg
import cv2

#A blueprint is essentially a code module
powercoachbp = Blueprint('powercoach', __name__)

#'/powercoach' is the route (path in the url)
@powercoachbp.route('/powercoach')
def powercoach():
    powercoachalg() #The context which defines the variables to be available - you can change this to be an instance of powercoach()