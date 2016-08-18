import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db

APP_SETTINGS="config.DevConfig"
app.config.from_object(APP_SETTINGS)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()