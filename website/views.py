from flask import Blueprint, render_template, request
from stravalib import Client

views = Blueprint('views', __name__)

# setup routes
@views.route("/home")
def home():
    return render_template('home.html')
