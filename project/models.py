from project import db
from project import bcrypt
import ldap, datetime, os


LDAP_SERVER = os.environ['USERDNSDOMAIN']
LDAP_PORT = "389"


membership_table = db.Table('membership',
                            db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                            db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True)
                            )

ownership_table = db.Table('ownership',
                           db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
                           db.Column('network_id', db.Integer, db.ForeignKey('networks.id'), primary_key=True)
                           )


group_tag_table = db.Table('grptag',
                           db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
                           db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
                           )


network_tag_table = db.Table('nettag',
                             db.Column('net_id', db.Integer, db.ForeignKey('networks.id'), primary_key=True),
                             db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
                             )


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    alt_id = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    networks = db.relationship("Network", backref="user", lazy=True)
    reg_date = db.Column(db.DateTime, nullable=False)
    operator = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    groups = db.relationship("Group", secondary=membership_table, back_populates='users')

    def __init__(self, username, password, email, name, surname, admin=False, operator=False):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email
        self.name = name
        self.surname = surname
        self.admin = admin
        self.operator = operator
        self.reg_date = datetime.datetime.now()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.alt_id)

    @staticmethod
    def ldap_login(email, password):
        ld = ldap.initialize("ldap://{}:{}".format(LDAP_SERVER, LDAP_PORT))
        return ld.simple_bind_s(email, password)

    def __repr__(self):
        return '<username: {}>'.format(self.username)


class Group(db.Model):

    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    users = db.relationship("User", secondary=membership_table, back_populates='groups')
    networks = db.relationship("Network", secondary=ownership_table, back_populates='groups')
    tags = db.relationship("Tag", secondary=group_tag_table, back_populates='groups')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<group: {}>'.format(self.name)


class Network(db.Model):

    __tablename__ = "networks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    meraki_id = db.Column(db.String(64), unique=True)
    type = db.Column(db.String(32), nullable=False)
    committed = db.Column(db.Boolean, nullable=False)
    reg_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bound_template = db.Column(db.String(64), db.ForeignKey('templates.meraki_id'))
    source_network = db.Column(db.Integer, db.ForeignKey('networks.id'))
    source_network_rel = db.relationship("Network", backref=db.backref("copied_from", remote_side=[id]), lazy=True)
    devices = db.relationship("Device", backref="network", lazy=True)
    groups = db.relationship("Group", secondary=ownership_table, back_populates='networks')
    net_tags = db.Column(db.String(256))
    tags = db.relationship("Tag", secondary=network_tag_table, back_populates='networks')

    def __init__(self, net_name, net_type, user_id=None, meraki_id=None,
                 net_tags=None, bound_template=None, source_network=None, committed=False):
        self.name = net_name
        self.type = net_type
        self.committed = committed
        self.reg_date = datetime.datetime.now()
        self.user_id = user_id
        self.bound_template = bound_template
        self.source_network = source_network
        self.net_tags = net_tags
        self.meraki_id = meraki_id

    def update(self, net_name, net_type, user_id=None, meraki_id=None,
               net_tags=None, bound_template=None, committed=False):
        self.name = net_name
        self.type = net_type
        self.committed = committed
        self.reg_date = datetime.datetime.now()
        self.user_id = user_id
        self.bound_template = bound_template
        self.net_tags = net_tags
        self.meraki_id = meraki_id

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
    name = db.Column(db.String(64))
    serial = db.Column(db.String(32), nullable=False)
    devmodel = db.Column(db.String(32))
    reg_date = db.Column(db.DateTime, nullable=False)
    committed = db.Column(db.Boolean, nullable=False)
    rebooted = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    status = db.Column(db.String(8))
    network_id = db.Column(db.Integer, db.ForeignKey('networks.id'))

    def __init__(self, device_name, device_serial, network_id, committed=False, status=None, last_seen=None):
        self.name = device_name
        self.serial = device_serial
        self.reg_date = datetime.datetime.now()
        self.committed = committed
        self.network_id = network_id
        self.status = status
        self.last_seen = last_seen

    def update(self, device_name, device_serial, network_id, device_model=None, committed=False):
        self.name = device_name
        self.serial = device_serial
        self.devmodel = device_model
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
    name = db.Column(db.String(64), nullable=False, unique=True)
    meraki_id = db.Column(db.String(64), unique=True)
    reg_date = db.Column(db.DateTime, nullable=False)
    networks = db.relationship("Network", backref="template", lazy=True)

    def __init__(self, template_name, template_n_id):
        self.name = template_name
        self.meraki_id = template_n_id
        self.reg_date = datetime.datetime.now()

    def update(self, template_name, template_n_id):
        self.name = template_name
        self.meraki_id = template_n_id
        self.reg_date = datetime.datetime.now()

    def __repr__(self):
        return '<template_name: {}>'.format(self.name)


class Tag(db.Model):

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    groups = db.relationship("Group", secondary=group_tag_table, back_populates='tags')
    networks = db.relationship("Network", secondary=network_tag_table, back_populates='tags')

    def __init__(self, tag_name):
        self.name = tag_name

    def __repr__(self):
        return '<tag_name: {}>'.format(self.name)