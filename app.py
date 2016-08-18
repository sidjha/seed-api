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

    if not request.json or not "lat" in request.json or not "lng" in request.json:
        abort(400, "Missing parameter")

    lat = request.json["lat"]
    lng = request.json["lng"]

    #TODO: query database for matching circle


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