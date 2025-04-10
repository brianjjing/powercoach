#FIXING THE NO MODULE NAMED POWERCOACHAPP ERROR:
import sys
import os

#Powerjudge blueprint (AI is in powercoachalg):
from flask import (
    Blueprint, g, render_template, request, Response, url_for
)
from werkzeug.exceptions import abort

from powercoachapp.auth import login_required
from powercoachapp.database import get_db
from powercoachapp.powercoachalgs import powercoachalg
import cv2

#A blueprint is essentially a code module
powercoachbp = Blueprint('powercoach', __name__)

"""
def generate_frames():
    camera = cv2.VideoCapture(0)  # Open webcam (0 for default camera)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield ... #yield the json response??
            
            #FOR COMPUTER BACKEND TESTING:
            # Use the frame as part of the HTTP response
            #yield (b'--frame\r\n'
                  #b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
"""

#'/powercoach' is the route (path in the url)
@powercoachbp.route('/powercoach')
def powercoach():
    #You don't need this api endpoint for the streaming functionality anymore.
    #This page can still be necessary for page rendering and static content though.
    #This return statement below is just for testing the output on the Flask backend:
    return powercoachalg() #The context which defines the variables to be available - you can change this to be an instance of powercoach()
    #return powercoachalg()