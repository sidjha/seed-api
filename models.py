# models.py

class Circle:
    # center: coordinate of center point (lat/long)
    # radius: length of radius (meters)
    # city: city where circle is in
    # seeds: list of seeds
    # metadata: other optional metadata
    pass

class Seed:
    # title: Descriptive title of seed
    # link: URL of seed content
    # circle: circle in which seed belongs
    # seeder: username of seeder
    # isActive: True if seed has not expired. False, otherwise.
    # metadata: other optional metadata
    pass

class User:
    # first_name
    # last_initial
    # username
    # notifications: boolean indicating whether notifications are ON or OFF
    # seeds: list of Seeds (seed_ids) this user has seeded
    # metadata: other optional metadata
    pass

class Seedbag:
    pass

