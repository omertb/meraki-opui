#!/usr/bin/env python3
from project.models import *


# create the database and the db table
db.create_all()

# insert data
db.session.add(User("admin", "admin", "admin@example.com", "admin", "admin", True, True))
db.session.add(User("operator", "operator", "operator@example.com", "operator", "operator", False, True))
# db.session.add(Network("Test-Wireless"))
# db.session.add(Network("Test-Switch"))


# commit the changes
db.session.commit()
