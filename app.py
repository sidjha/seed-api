from flask import Flask, render_template, request, json, g
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
APP_SETTINGS="config.DevConfig"
app.config.from_object(APP_SETTINGS)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Circle, Seed, User

@app.route("/")
def index():
    return "seed v1.0"

@app.route("/circles", methods=["GET"])
def api_circle():
    """
    Returns a matching circle if the specified latitude and longitude fall within a defined circle. 
    Otherwise, returns a list of nearby circles based on specified latitude and longitude.
    """

    # Parse arguments, extract latitude and longitude
    lat = request.args.get("lat", '')
    lng = request.args.get('lng', '')

    # TODO: Query database for circles with nearby centres
    
    # Check list to see whether point is inside existing circle

    # for each point in list
    # 1. convert point to radians
    # 2. calculate geodesic
    # a = (math.sin(lat)*math.sin(p_lat)+math.cos(lat)*math.cos(p_lat)*math.cos(lng - p_lng))
    # dist = (math.acos(a))*6371
    # 3. if distance <= radius, point is inside. convert to JSON and return.

    # convert 5 items from list to JSON-formatted list


def is_in_circle(latitude, longitude):
    # problem: need an algorithm that determines whether these coords are within a defined circle
    # solution: 
    #  the database needs to store the center coordinates of every circle, and the radius.
    #  so each record in the Circles db will be a (coordinates, radius) pair
    #  now we have available as input coordinates and we need to determine whether these coordinates
    #  are equal to any one circle's all possible interior coordinates. that's a very time-consuming
    #  computation as there will be an infinite # of coordinates.

    # solution 2:
    # take the input coordinates A.
    # do a search of coordinates in (coordinates, radius) pairs to find all coordinates less than 1000m from A.
    # for every coordinate C in S:
    #  if geodesic distance between A and C is less than C's radius:
    #   that's the circle A belongs to.
    #   return.
    # if no match, then there are no circles closeby.
    pass

if __name__ == "__main__":
    app.run()