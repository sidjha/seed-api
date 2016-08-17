# models.py

class Circle:
    # center: coordinate of center point (lat/long)
    # radius: length of radius (meters)
    # city: city where circle is in
    # seeds: list of seeds
    # metadata: other optional metadata
    # create table circle(circle_id integer, center_lat real, center_lng real, radius integer, city varchar(30), seeds integer, metadata varchar(1000));
    pass

class Seed:
    # title: Descriptive title of seed
    # link: URL of seed content
    # circle: circle in which seed belongs
    # seeder: username of seeder
    # isActive: True if seed has not expired. False, otherwise.
    # metadata: other optional metadata
    # create table seed(seed_id integer, link varchar(65535), user_id integer, isActive integer, metadata varchar(1000));
    pass

class User:
    # first_name
    # last_initial
    # username
    # notifications: boolean indicating whether notifications are ON or OFF
    # seeds: list of Seeds (seed_ids) this user has seeded
    # metadata: other optional metadata
    # create table user(user_id integer, first_name varchar(20), last_initial varchar(3), username varchar(20), metadata varchar(1000));
    pass

class Seedbag:
    pass

