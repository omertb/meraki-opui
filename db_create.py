#!/usr/bin/env python3
from project.models import *


# create the database and the db table
db.drop_all()
db.create_all()

# insert data
# admin_user = User("admin", "admin", "admin@example.com", "admin", "admin", True, True)
# operator_user = User("operator", "operator", "operator@example.com", "operator", "operator", False, True)
admin_group = Group("administrators")
operator_group = Group("operators")

#admin_group.users.append(admin_user)
#operator_group.users.append(operator_user)

# db.session.add(admin_user)
# db.session.add(operator_user)
db.session.add(admin_group)
db.session.add(operator_group)

# db.session.add(Network("Test-Wireless"))
# db.session.add(Network("Test-Switch"))


# commit the changes
db.session.commit()
