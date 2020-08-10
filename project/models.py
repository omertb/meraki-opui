from project import db
from project import bcrypt
import ldap, datetime, os


LDAP_SERVER = os.environ['USERDNSDOMAIN']
LDAP_PORT = "389"


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
    reg_date = db.Column(db.DateTime, nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, password, email, name, surname, admin=False, verified=False):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email
        self.name = name
        self.surname = surname
        self.admin = admin
        self.verified = verified
        self.reg_date = datetime.datetime.now()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def ldap_login(email, password):
        ld = ldap.initialize("ldap://{}:{}".format(LDAP_SERVER, LDAP_PORT))
        try:
            ld.simple_bind_s(email, password)
        except (ldap.INVALID_CREDENTIALS, ldap.SERVER_DOWN) as e:
            return False
        return True

    def __repr__(self):
        return '<name {}'.format(self.username)



