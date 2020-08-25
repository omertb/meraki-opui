from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length


class NetworkDeviceForm(FlaskForm):
    net_name = StringField('Network Name: ', validators=[Length(max=64)])
    net_template = SelectField('Template: ', choices=[])
    net_type = SelectField('Network Type: ', choices=["firewall", "switch", "wireless"])
    serial_nos = TextAreaField('Serial Numbers, one per line: ', validators=[DataRequired(), Length(max=2000)])
    registered_nets = SelectField('Network: ', choices=[])
    new_or_existing = SelectField("New", choices=[("new", "New Network"), ("existing", "Existing Network")], )
