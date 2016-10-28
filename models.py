from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography
from sqlalchemy import Integer

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Circle(db.Model):
    
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

    __tablename__ = 'seeds'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    link = db.Column(db.String())
    #circle_id = db.Column(db.Integer, db.ForeignKey('circles.id'))
    point = db.Column(Geography(geometry_type='POINT', srid=4326))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    seeder_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(40))
    isActive = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)
    report_count = db.Column(db.Integer)
    upvotes = db.Column(db.Integer)

    def __init__(self, title, link, point, lat, lng, seeder_id, username, isActive, timestamp):
        self.title = title
        self.link = link
        #self.circle_id = circle_id
        self.point = point
        self.lat = lat
        self.lng = lng
        self.seeder_id = seeder_id
        self.username = username
        self.isActive = isActive
        self.timestamp = timestamp
        self.report_count = 0
        self.upvotes = 0

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
            'username' : self.username,
            'isActive' : self.isActive,
            'timestamp': self.timestamp,
            'upvotes': str(self.upvotes)
        }

class User(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    apple_vendor_id = db.Column(db.String(60), unique=True)
    real_name = db.Column(db.String(40))
    username = db.Column(db.String(40))
    notifications = db.Column(db.Boolean)
    seeds = db.relationship('Seed', backref='user', lazy='dynamic')
    upvoted_seeds = db.Column(postgresql.ARRAY(Integer))

    def __init__(self, real_name, username, apple_vendor_id, notifications):
        self.real_name = real_name
        self.username = username
        self.apple_vendor_id = apple_vendor_id
        self.notifications = notifications

    def __repr__(self):
        return '<User %r>' % self.id

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'apple_vendor_id': self.apple_vendor_id,
            'real_name': self.real_name,
            'username': self.username,
            'notifications': self.notifications,
            'seeds': 'seeds'
        }


class ReportedSeed(db.Model):
    __tablename__ = 'reportedseeds'
    id = db.Column(db.Integer, primary_key=True)
    reporter = db.Column(db.Integer, db.ForeignKey('users.id'))
    seed = db.Column(db.Integer, db.ForeignKey('seeds.id'))
    reason = db.Column(db.String())

    def __init__(self, reporter, seed, reason):
        self.reporter = reporter
        self.seed = seed
        self.reason = reason

    def __repr__(self):
        return '<ReportedSeed %r>' % self.id

    @property
    def serialize(self):
        return {
            'id': self.id,
            'reporter': self.reporter,
            'seed': self.seed,
            'reason': self.reason
        }


class Seedbag():
    pass