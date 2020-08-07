from project import db
from project import bcrypt


class Device(db.Model):

    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(50), nullable=False, unique=True)
    device_serial = db.Column(db.String(20), nullable=False)
    net_id = db.Column(db.Integer, db.ForeignKey('networks.id'))

    def __init__(self, device_name, device_serial):
        self.device_name = device_name
        self.device_serial = device_serial

    def __repr__(self):
        return '<device_name {}'.format(self.device_name)

class Network(db.Model):

    __tablename__ = "networks"

    id = db.Column(db.Integer, primary_key=True)
    net_name = db.Column(db.String(50), nullable=False, unique=True)
    net_type = db.Column(db.String(30), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    devices = db.relationship("Device", backref="network", lazy=True)

    def __init__(self, net_name):
        self.net_name = net_name

    def __repr__(self):
        return '<net_name {}'.format(self.net_name)


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    networks = db.relationship("Network", backref="user", lazy=True)

    def __init__(self, username, password, email, name, surname):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email
        self.name = name
        self.surname = surname

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<name {}'.format(self.username)



