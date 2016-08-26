from flask import Flask, render_template, request, g, jsonify
import os, math
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from models import Circle, Seed, User, db

app = Flask(__name__)
APP_SETTINGS="config.DevConfig"
app.config.from_object(APP_SETTINGS)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

NEARBY_CIRCLES_THRESHOLD_DIST = 2000.0 # in meters.
NUM_NEARBY_CIRCLES_LIMIT = 5 # number of nearby circles to search

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
    lat = float(request.args.get("lat", ''))
    lng = float(request.args.get('lng', ''))

    if lat and lng:
        # convert current coordinates to a Geography object
        point = func.ST_GeogFromText('SRID=4326;POINT(%f %f)' % (lng, lat)) 

        # call PostGIS function ST_DWithin to find 5 nearby points
        nearby = db.session.query(Circle) \
                    .filter(func.ST_DWithin(point, Circle.point, NEARBY_CIRCLES_THRESHOLD_DIST)) \
                    .order_by(func.ST_Distance(point, Circle.point)) \
                    .limit(NUM_NEARBY_CIRCLES_LIMIT)

        num_circles_found = nearby.count()
        
        if num_circles_found > 0:
            for a_circle in nearby:
                p_lat = math.radians(a_circle.center_lat)
                p_lng = math.radians(a_circle.center_lng)
                lat_r = math.radians(lat)
                lng_r = math.radians(lng)
                temp_dist = (math.sin(lat_r)*math.sin(p_lat)+math.cos(lat_r)*math.cos(p_lat)*math.cos(lng_r - p_lng))
                geodesic_dist = (math.acos(temp_dist))*6371000

                if geodesic_dist <= a_circle.radius:
                    return jsonify({"in_circle": True, "circles": a_circle.serialize}), 200
                else:
                    return jsonify({"in_circle": False, "circles": [i.serialize for i in nearby.all()]}), 200
        else:
            return jsonify({"in_circle": False, "circles": []}), 200

def alternative_circle_search():
    # This one does it with max 2 queries instead of comparing geodesics of nearby set

    # Query 1: Check if you're within a circle
    nearby = db.session.query(Circle) \
                .filter(func.ST_DWithin(point, Circle.point, Circle.radius)) \
                .order_by(func.ST_Distance(point, Circle.point)) \
                .limit(NUM_NEARBY_CIRCLES_LIMIT)

    if nearby.count() > 0:
        return "You are within the circle: %s" % nearby.first().name
    else:
        # Query 2: Find nearby circles
        nearby = db.session.query(Circle) \
                .filter(func.ST_DWithin(point, Circle.point, NEARBY_CIRCLES_THRESHOLD_DIST)) \
                .order_by(func.ST_Distance(point, Circle.point)) \
                .limit(NUM_NEARBY_CIRCLES_LIMIT)

        if nearby.count() > 0:
            # TODO: determine whether point is WITHIN any circle
            # TODO: convert returned data to JSON
            return "Not in circle, but found %d nearby circles!" % nearby.count()
        else:
            return "Sorry, no nearby circles found."

def is_in_circle(latitude, longitude):
    # problem: need an algorithm that determines whether these coords are within a defined circle

    # solution 2:
    # take the input coordinates A.
    # do a search of coordinates in (coordinates, radius) pairs to find all coordinates less than 1000m from A.
    # for every coordinate C in S:
    #  if geodesic distance between A and C is less than C's radius:
    #   that's the circle A belongs to.
    #   return.
    # if no match, then there are no circles closeby.

    # TODO: implementation of solution 2
    # Check list to see whether point is inside existing circle
    # for each point in list
    # 1. convert point to radians
    # 2. calculate geodesic
    # a = (math.sin(lat)*math.sin(p_lat)+math.cos(lat)*math.cos(p_lat)*math.cos(lng - p_lng))
    # dist = (math.acos(a))*6371
    # 3. if distance <= radius, point is inside. convert to JSON and return.
    pass

def populate_GIS():
    circle1 = Circle(center_lat=37.332376, center_lng=-122.030754, point='POINT(-122.030754 37.332376)', radius='150', name='infinite loop', city='Cupertino')
    circle2 = Circle(center_lat=37.414172, center_lng=-122.038672, point='POINT(-122.038672 37.414172)', radius='200', name='airbase', city='Cupertino')
    circle4 = Circle(center_lat=37.777025, center_lng=-122.416583, point='POINT(-122.416583 37.777025)', radius='200', name='twitter hq', city='San Francisco')
    circle3 = Circle(center_lat=40.748636, center_lng=-73.985654, point='POINT(-73.985654 40.748636)', radius='100', name='empire state', city='Empire State Bldg')


if __name__ == "__main__":
    app.run()