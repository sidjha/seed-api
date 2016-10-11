from flask import Flask, render_template, request, g, jsonify, abort
import os, math
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from models import Circle, Seed, User, db
from datetime import datetime

app = Flask(__name__)
APP_SETTINGS=os.environ.get('APP_SETTINGS')
app.config.from_object(APP_SETTINGS)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

NEARBY_CIRCLES_THRESHOLD_DIST = 2000.0 # in meters.
NUM_NEARBY_CIRCLES_LIMIT = 5 # number of nearby circles to search

NEARBY_SEEDS_THRESHOLD_DIST = 500.0 # in meters.

# pragma mark - API methods

@app.route("/")
def index():
    return "seed v1.0"


@app.route("/seeds", methods=["GET"])
def api_get_seeds():
    """
    Returns a list of seeds near the latitude and longitude.
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

        # call PostGIS function ST_DWithin to find nearby seeds
        nearby = db.session.query(Seed) \
                    .filter(func.ST_DWithin(point, Seed.point, NEARBY_SEEDS_THRESHOLD_DIST)) \
                    .order_by(func.ST_Distance(point, Seed.point))

        num_seeds_found = nearby.count()

        return jsonify({"seeds": [i.serialize for i in nearby.all()]}), 200

    else:
        abort(400, "Invalid or missing arguments")


@app.route("/seed/create", methods=["POST"])
def api_create_seed():
    """
    Create a new seed with the specified title and link and specified location.
    If user with vendor_id exists, then associate the seed with that user.
    If user with vendor_id does not exist, then create new user first, then
    create seed and associate the seed with the new user.
    """
    if request.method == "POST":
        for item in ["title", "link", "lat", "lng", "vendor_id_str", "username"]:
            if not item in request.form:
                abort(400, "Missing arguments.")

        # TODO: validate title and link
        title = request.form["title"].strip()
        link = request.form["link"].strip()
        lat = request.form["lat"].strip()
        lng = request.form["lng"].strip()
        username = request.form["username"].strip()
        vendor_id = request.form["vendor_id_str"].strip()

        seeder = User.query.filter_by(apple_vendor_id=vendor_id).first()
        point = func.ST_GeogFromText('SRID=4326;POINT(%f %f)' % (float(lng), float(lat)))

        new_seed = None
        if seeder:
            # Save new seed and connect it to existing user
            new_seed = Seed(title=title, link=link,
                point=point, lat=lat, lng=lng,
                seeder_id=seeder.id, username=username, 
                timestamp=datetime.utcnow(), isActive=True)
        else:
            # Create new user
            new_user = User(real_name="",
                        apple_vendor_id=vendor_id,
                        username=username,
                        notifications=False)
            try:
                db.session.add(new_user)
                db.session.commit()
            except Exception as e:
                abort(500, "Something went wrong in setting up new user.")

            # Save new seed and connect it to newly created user
            new_seed = Seed(title=title, link=link,
                point=point, lat=lat, lng=lng,
                seeder_id=new_user.id, username=username, 
                timestamp=datetime.utcnow(), isActive=True)
        try:
            db.session.add(new_seed)
            db.session.commit()
            return jsonify({"seed": new_seed.serialize}), 200
        except:
            abort(500, "Something went wrong. Could not create seed.")
    else:
        abort(400, "This type of request is not supported.")


@app.route("/seed", methods=["GET"])
def api_get_seed():
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


@app.route("/seed/delete", methods=["POST"])
def api_delete_seed():
    """
    Delete the specified seed.
    """
    if request.method == "POST":
        try:
            seed_id = int(request.form.get("seed_id"))
            vendor_id = request.form.get("vendor_id_str").strip()
        except:
            abort(400, "Invalid arguments")

        seed = Seed.query.filter_by(id=seed_id).first()
        user = User.query.filter_by(apple_vendor_id=vendor_id)

        # TODO: check if this user is allowed to delete the seed
        if seed and seed.seeder_id == user.id:
            try:
                db.session.delete(seed)
                db.session.commit()
                return jsonify({"seed": ""}), 200
            except:
                abort(500, "Something went wrong. Could not delete seed.")
        else:
            abort(400, "Not allowed to delete seed.")
    else:
        abort(400, "This type of request is not supported.")


@app.route("/user", methods=["GET"])
def api_get_user():
    """
    Returns the user with the specified username or user_id.
    """
    vendor_id = request.args.get("vendor_id_str")

    if vendor_id:
        vendor_id = vendor_id.strip()
        user = User.query.filter_by(apple_vendor_id=vendor_id).first()

        if user:
            return jsonify({"user": user.serialize}), 200
        else:
            abort(404, "User does not exist.")

    abort(400, "Invalid or missing arguments.")


@app.route("/user/update", methods=["POST"])
def api_update_user():
    """
    Change settings for a user.
    """
    if request.method == "POST":
        vendor_id = request.form.get("vendor_id_str", None)

        if not vendor_id:
            abort(400, "User credentials missing.")

        vendor_id = vendor_id.strip()

        real_name = request.form.get("real_name", "")
        username = request.form.get("username", "")
        notifications = request.form.get("notifications", "")

        if real_name and not validate_realname(real_name):
            abort(400, "Invalid arguments - real name can only be max 40 letters.")

        if username and not validate_username(username):
            abort(400, "Invalid username.")

        user = User.query.filter_by(apple_vendor_id=vendor_id).first()

        if user:
            field_updated = False

            if notifications and notifications != user.notifications:
                user.notifications = notifications
                field_updated = True

            if real_name and real_name != user.real_name:
                user.real_name = real_name
                field_updated = True

            if username and username != user.username:
                user.username = username
                field_updated = True

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


@app.route("/user/delete", methods=["POST"])
def api_delete_user():
    """
    Delete the specified user and all their seeds.
    """
    if request.method == "POST":
        vendor_id = request.form.get("vendor_id_str", None)

        if vendor_id:
            vendor_id = vendor_id.strip()
            user = User.query.filter_by(apple_vendor_id=vendor_id).first()
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


""" 
********************************
Deprecated API methods (For now)
********************************
"""
# @app.route("/circles", methods=["GET"])
def api_get_circle():
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

#@app.route("/reseed", methods=["POST"])
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

#@app.route("/user/create", methods=["POST"])
def api_create_user():
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
        vendor_id = request.form["vendorIDStr"].strip()

        if first_name and last_initial and username and vendor_id:

            if not validate_first_name(first_name) or not validate_last_initial(last_initial):
                abort(400, "Invalid arguments - name can only be max 40 letters each. Last initial can be max 5 letters with no spaces or numbers.")

            if not validate_username(username):
                abort(400, "Invalid username.")

            if not validate_vendorID(vendor_id):
                abort(400, "Invalid vendor ID.")

            try:
                new_user = User(first_name=first_name,
                            last_initial=last_initial,
                            username=username,
                            apple_vendor_id=vendor_id,
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


"""
****************
Helper Functions
****************
"""
def validate_realname(name):
    return 0 < len(name) <= 40

def validate_username(username):
    if 0 < len(username) <= 40:
        return True

def validate_vendorID(vendor_id):
    existing_user = User.query.filter_by(apple_vendor_id=vendor_id).first()
    if not existing_user:
        return True
    return False

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