from project import db
from project import bcrypt
import ldap, datetime, os


LDAP_SERVER = os.environ['USERDNSDOMAIN']
LDAP_PORT = "389"


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
    templates = db.relationship("Template", backref="user", lazy=True)

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
        return '<username: {}>'.format(self.username)


class Network(db.Model):

    __tablename__ = "networks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    type = db.Column(db.String(30), nullable=False)
    n_id = db.Column(db.String(32), unique=True)
    committed = db.Column(db.Boolean, nullable=False)
    reg_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bound_template = db.Column(db.Integer, db.ForeignKey('templates.id'))
    devices = db.relationship("Device", backref="network", lazy=True)

    def __init__(self, net_name, net_type, user_id, bound_template=None, committed=False):
        self.name = net_name
        self.type = net_type
        self.committed = committed
        self.reg_date = datetime.datetime.now()
        self.user_id = user_id
        self.bound_template = bound_template

    def __repr__(self):
        return '<net_name: {}>'.format(self.name)

    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'type' : self.type,
            'committed' : self.committed,
            'bound_template' : self.bound_template
        }


class Device(db.Model):

    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    serial = db.Column(db.String(20), nullable=False)
    n_id = db.Column(db.String(32), unique=True)
    reg_date = db.Column(db.DateTime, nullable=False)
    committed = db.Column(db.Boolean, nullable=False)
    network_id = db.Column(db.Integer, db.ForeignKey('networks.id'))

    def __init__(self, device_name, device_serial, network_id, committed=False):
        self.name = device_name
        self.serial = device_serial
        self.reg_date = datetime.datetime.now()
        self.committed = committed
        self.network_id = network_id

    def __repr__(self):
        return '<device_name: {}>'.format(self.name)

    def serialize(self):
        return {
            'name' : self.name,
            'serial' : self.serial,
            'committed' : self.committed
        }


class Template(db.Model):

    __tablename__ = "templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    n_id = db.Column(db.String(32), unique=True)
    reg_date = db.Column(db.DateTime, nullable=False)
    networks = db.relationship("Network", backref="template", lazy=True)
    template_user = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, template_name, n_id, template_user=None):
        self.name = template_name
        self.n_id = n_id
        self.reg_date = datetime.datetime.now()
        self.template_user = template_user

    def __repr__(self):
        return '<template_name: {}>'.format(self.name)