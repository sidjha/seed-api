from flask import Flask, render_template, request, g, jsonify, abort
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

# pragma mark - API methods

@app.route("/")
def index():
    return "seed v1.0"

@app.route("/circles", methods=["GET"])
def api_circle():
    """
    Returns a matching circle if the specified latitude and longitude fall within a defined circle. 
    Otherwise, returns a list of nearby circles based on specified latitude and longitude.
    """

    if "lat" in request.args and "lng" in request.args:
        # Parse arguments, extract latitude and longitude
        try:
            lat = float(request.args.get("lat", ''))
            lng = float(request.args.get('lng', ''))

            if (lat and lng) and (-90 <= lat <= 90) and (-180 <= lng <= 180):
                pass
            else:
                raise ValueError("Invalid arguments")
        except:
            abort(400, "Invalid arguments")

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
    else:
        abort(400, "Missing arguments")

@app.route("/seeds", methods=["GET"])
def api_seeds():
    """
    Returns a list of seeds in the circle with the specified circle_id.
    """
    circle_id = request.args.get('circle_id')
    if circle_id:
        circle = Circle.query.filter_by(id=circle_id).first()

        if circle:
            return jsonify({"seeds": [i.serialize for i in circle.seeds]}), 200
        else:
            abort(404, "Circle does not exist.")
    else:
        abort(400, "Invalid or missing arguments")


# pragma mark - helper functions
def populate_GIS():
    circle1 = Circle(center_lat=37.332376, center_lng=-122.030754, point='POINT(-122.030754 37.332376)', radius='150', name='infinite loop', city='Cupertino')
    circle2 = Circle(center_lat=37.414172, center_lng=-122.038672, point='POINT(-122.038672 37.414172)', radius='200', name='airbase', city='Cupertino')
    circle4 = Circle(center_lat=37.777025, center_lng=-122.416583, point='POINT(-122.416583 37.777025)', radius='200', name='twitter hq', city='San Francisco')
    circle3 = Circle(center_lat=40.748636, center_lng=-73.985654, point='POINT(-73.985654 40.748636)', radius='100', name='empire state', city='Empire State Bldg')

def populate_seeds():
    seed1 = Seed(title="Dropbox looking to IPO in 2017.",
                 link="http://www.bloomberg.com/news/articles/2016-08-15/dropbox-said-to-discuss-possible-2017-ipo-in-talks-with-advisers",
                 circle_id=4,
                 seeder_id=1,
                 isActive=True)

    seed2 = Seed(title="Uber just losing lots of money.",
                 link="http://www.nytimes.com/2016/08/26/technology/how-uber-lost-more-than-1-billion-in-the-first-half-of-2016.html?ref=technology",
                 circle_id=4,
                 seeder_id=1,
                 isActive=True)

    db.session.add(seed1)
    db.session.commit()

def populate_users():
    user1 = User(first_name="Siddharth",
                 last_initial="J",
                 username="sidjha",
                 notifications=True)

    db.session.add(user1)
    db.session.commit()

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


if __name__ == "__main__":
    app.run()