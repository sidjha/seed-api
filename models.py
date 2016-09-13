from sqlalchemy.dialects.postgresql import JSON
from geoalchemy2 import Geography

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Circle(db.Model):
    # center_lat: latitude of center point
    # center_lng: longitude of center point
    # point: PostGIS Geography rep of center point (long lat)
    # radius: length of radius (meters)
    # city: city where circle is in
    # seeds: list of seeds
    
    __tablename__ = 'circles'
    id = db.Column(db.Integer, primary_key=True)
    center_lat = db.Column(db.Float)
    center_lng = db.Column(db.Float)
    point = db.Column(Geography(geometry_type='POINT', srid=4326))
    radius = db.Column(db.Integer)
    name = db.Column(db.String())
    city = db.Column(db.String())
    #seeds = db.relationship('Seed', backref='circle', lazy='dynamic')

    def __init__(self, center_lat, center_lng, point, radius, name, city):
        self.center_lat = center_lat
        self.center_lng = center_lng
        self.point = point
        self.radius = radius
        self.name = name
        self.city = city

    def __repr__(self):
        return '<Circle %r>' % self.id

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'center_lat': self.center_lat,
            'center_lng': self.center_lng,
            'radius': self.radius,
            'name': self.name,
            'city': self.city
            #'seeds': 'seeds'
        }

class Seed(db.Model):
    # title: Descriptive title of seed
    # link: URL of seed content
    # circle_id: circle in which seed belongs
    # seeder: username of seeder
    # isActive: True if seed has not expired. False, otherwise.

    __tablename__ = 'seeds'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    link = db.Column(db.String())
    #circle_id = db.Column(db.Integer, db.ForeignKey('circles.id'))
    point = db.Column(Geography(geometry_type='POINT', srid=4326))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    seeder_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    seeder_name = db.Column(db.String())
    original_seeder_id = db.Column(db.Integer)
    isActive = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)

    def __init__(self, title, link, point, lat, lng, seeder_id, seeder_name, original_seeder_id, isActive, timestamp):
        self.title = title
        self.link = link
        #self.circle_id = circle_id
        self.point = point
        self.lat = lat
        self.lng = lng
        self.seeder_id = seeder_id
        self.original_seeder_id = original_seeder_id
        self.isActive = isActive
        self.timestamp = timestamp
        self.seeder_name = seeder_name

    def __repr__(self):
        return '<Seed %r>' % self.id

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'title' : self.title,
            'link' : self.link,
            'lat' : self.lat,
            'lng' : self.lng,
            'seeder_id' : self.seeder_id,
            'original_seeder_id': self.original_seeder_id,
            'isActive' : self.isActive,
            'timestamp': self.timestamp,
            'seeder_name': self.seeder_name
        }

class User(db.Model):
    # first_name
    # last_initial
    # username
    # notifications: boolean indicating whether notifications are ON or OFF
    # seeds: list of Seeds (seed_ids) this user has seeded
    
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40))
    last_initial = db.Column(db.String(40))
    username = db.Column(db.String(40), unique=True)
    notifications = db.Column(db.Boolean)
    seeds = db.relationship('Seed', backref='user', lazy='dynamic')

    def __init__(self, first_name, last_initial, username, notifications):
        self.first_name = first_name
        self.last_initial = last_initial
        self.username = username
        self.notifications = notifications

    def __repr__(self):
        return '<User %r>' % self.id

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'first_name' : self.first_name,
            'last_initial' : self.last_initial,
            'username': self.username,
            'notifications': self.notifications,
            'seeds': 'seeds'
        }

class Seedbag():
    pass