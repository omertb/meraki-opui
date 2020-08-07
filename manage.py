from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from project import app, db

app.config.from_object('config.DevelopmentConfig')
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

# previous code
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate, MigrateCommand
# from flask_script import Manager
#
# app = Flask(__name__)
# app.config.from_object('config.DevelopmentConfig')
#
# db = SQLAlchemy(app)
#
# migrate = Migrate(app, db)
# manager = Manager(app)
#
# manager.add_command('db', MigrateCommand)
#
# # INSERT MODELS HERE
# from project.models import *
#
# if __name__ == '__main__':
#     manager.run()
