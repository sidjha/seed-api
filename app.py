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
            lat = float(request.args.get("lat", ""))
            lng = float(request.args.get("lng", ""))

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
    try:
        circle_id = int(request.args.get("circle_id"))
    except:
        abort(400, "Invalid arguments.")

    if circle_id:
        circle = Circle.query.filter_by(id=circle_id).first()

        if circle:
            return jsonify({"seeds": [i.serialize for i in circle.seeds]}), 200
        else:
            abort(404, "Circle does not exist.")
    else:
        abort(400, "Invalid or missing arguments")

@app.route("/seeds/create", methods=["POST"])
def api_create_seed():
    """
    Create a new seed with the specified title and link in the specified circle.
    """
    if request.method == "POST":
        for item in ["title", "link", "circle", "user_id"]:
            if not item in request.form:
                abort(400, "Missing arguments.")

        try:
            circle_id = int(request.form["circle"].strip())
            user_id = int(request.form["user_id"].strip())
        except:
            abort(400, "Invalid arguments.")

        title = request.form["title"].strip()
        link = request.form["link"].strip()
        # TODO: validate title and link

        seeder = User.query.filter_by(id=user_id).first()
        circle = Circle.query.filter_by(id=circle_id).first()

        if seeder and circle:
            new_seed = Seed(title=title, link=link, circle_id=circle_id, seeder_id=user_id, isActive=True)
        else:
            abort(404, "Did not find circle or user.")

        try:
            db.session.add(new_seed)
            db.session.commit()
            return jsonify({"seed": new_seed.serialize}), 200
        except:
            abort(500, "Something went wrong. Could not create seed.")
    else:
        abort(400, "This type of request is not supported.")

@app.route("/seed", methods=["GET"])
def api_seed():
    """
    Returns a Seed with the specified seed_id.
    """
    try:
        seed_id = int(request.args.get("seed_id"))
    except:
        abort(400, "Invalid arguments")

    if seed_id:
        seed = Seed.query.filter_by(id=seed_id).first()

        if seed:
            return jsonify({"seed": seed.serialize}), 200
        else:
            abort(404, "Seed does not exist.")
    else:
        abort(400, "Invalid or missing arguments.")

@app.route("/reseed", methods=["POST"])
def api_reseed():
    """
    Reseed an existing seed in a new specified circle from the specified seedbag of user. 
    Return error if the circle_id is the same as the original circle of seed.
    """
    if request.method == "POST":
        try:
            #import pdb; pdb.set_trace()
            user_id = int(request.form.get("user_id", None))
            circle_id = int(request.form.get("circle_id", None))
            seed_id = int(request.form.get("seed_id", None))
        except:
            abort(404, "Missing or invalid arguments.")

        seed = Seed.query.filter_by(id=seed_id).first()

        if seed:
            if seed.circle_id == circle_id:
                abort(400, "You can't reseed in the same circle.")

            user = User.query.filter_by(id=user_id).first()
            circle = Circle.query.filter_by(id=circle_id).first()

            if user and circle:
                # TODO: validate title and link
                # Create new seed in new circle 
                new_seed = Seed(title=seed.title, link=seed.link, circle_id=circle_id, seeder_id=user_id, original_seeder_id=seed.seeder_id, isActive=True)

                try:
                    db.session.add(new_seed)
                    db.session.commit()
                    return jsonify({"seed": new_seed.serialize}), 200
                except:
                    abort(500, "Something went wrong. Could not re-seed.")
            else:
                abort(400, "Invalid arguments.")
    else:
        abort(400, "This type of request is not supported.")

@app.route("/users", methods=["GET"])
def api_users():
    """
    Returns the user with the specified username or user_id.
    """
    username = request.args.get("username")
    user_id = request.args.get("user_id")

    if username:
        user = User.query.filter_by(username=username).first()

        if user:
            return jsonify({"user": user.serialize}), 200
        else:
            abort(404, "User does not exist.")
    if user_id:
        user = User.query.filter_by(id=user_id).first()

        if user:
            return jsonify({"user": user.serialize}), 200
        else:
            abort(404, "User does not exist.")

    abort(400, "Invalid or missing arguments")

@app.route("/users/update", methods=["POST"])
def api_users_update():
    """
    Toggle notifications off or on for the specified user.
    """
    if request.method == "POST":
        user_id = request.form.get("user_id", None)

        if not user_id:
            abort(400, "User ID missing.")

        notifications = request.form.get("notifications", "")
        first_name = request.form.get("first_name", "")
        last_initial = request.form.get("last_initial", "")
        username = request.form.get("username", "")

        if not validate_first_name(first_name) or not validate_last_initial(last_initial):
            abort(400, "Invalid arguments - name and username can only be max 40 letters each. Last initial can be max 5 letters with no spaces or numbers.")

        if not validate_username(username):
            abort(400, "That username is taken.")

        user = User.query.filter_by(id=user_id).first()

        if user:
            field_updated = False

            if notifications and notifications != user.notifications:
                user.notifications = notifications
                field_updated = True

            if first_name and first_name != user.first_name:
                user.first_name = first_name
                field_updated = True

            if last_initial and last_initial != user.last_initial:
                user.last_initial = last_initial
                field_updated = True

            if username and username != user.username:
                existing_user = User.query.filter_by(username=username).first()

                if not existing_user:
                    user.username = username
                    field_updated = True
                else:
                    abort(400, "Username already exists.")

            if field_updated:
                try:
                    db.session.commit()
                    return jsonify({"user": user.serialize}), 200
                except:
                    abort(500, "Something went wrong.")
            else:
                return jsonify({"user": user.serialize}), 200
        else:
            abort(404, "User not found.")
    else:
        abort(400, "This type of request is not supported.")

@app.route("/accounts/create", methods=["POST"])
def api_create_account():
    """
    Create a new account with the specified first name, last initial and username. 
     first_name (required): 1-40 characters.
     last_initial (required): 1-5 characters, no numbers.
     username (required): 1-40 characters.
    Returns: JSON rep of user.
    """
    if request.method == "POST":
        first_name = request.form["first_name"].strip()
        last_initial = request.form["last_initial"].strip()
        username = request.form["username"].strip()

        if first_name and last_initial and username:

            if not validate_first_name(first_name) or not validate_last_initial(last_initial):
                abort(400, "Invalid arguments - name can only be max 40 letters each. Last initial can be max 5 letters with no spaces or numbers.")

            if not validate_username(username):
                abort(400, "Invalid username.")

            try:
                new_user = User(first_name=first_name,
                            last_initial=last_initial,
                            username=username,
                            notifications=False)
            except:
                abort(400, "Invalid arguments.")

            try:
                db.session.add(new_user)
                db.session.commit()
                return jsonify({"user": new_user.serialize}), 200
            except Exception as e:
                abort(500, "Something went wrong. Could not create new user.")

        else:
            abort(400, "Invalid or missing arguments")

    else:
        abort(400, "This type of request is not supported.")

@app.route("/users/delete", methods=["POST"])
def api_delete_user():
    """
    Delete the specified user and all their seeds.
    """
    if request.method == "POST":
        user_id = request.form.get("user_id", None)

        try:
            user_id = int(user_id)
        except:
            abort(400, "Invalid arguments.")

        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                try:
                    Seed.query.filter_by(seeder_id=user.id).delete()
                    db.session.delete(user)
                    db.session.commit()
                    return jsonify({"user": ""}), 200
                except:
                    abort(500, "Something went wrong. Could not delete user.")
            else:
                abort(400, "No such user found.")
        else:
            abort(400, "Missing arguments.")
    else:
        abort(400, "This type of request is not supported.")

# pragma mark - helper functions
def validate_first_name(first_name):
    return 0 < len(first_name) <= 40

def validate_last_initial(last_initial):
    if 0 < len(last_initial) <= 5:
        if last_initial.isalpha():
            return True
    return False

def validate_username(username):
    if 0 < len(username) <= 40:
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            return True
    return False

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