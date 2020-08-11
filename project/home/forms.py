from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length


class NetworkDeviceForm(FlaskForm):
    net_name = StringField('Network Name: ', validators=[DataRequired(), Length(max=64)])
    net_template = SelectField('Template: ', choices=[])
    net_type = SelectField('Network Type: ', choices=["appliance", "switch", "wireless"])
    serial_nos = TextAreaField('Serial Numbers, one per line: ', validators=[DataRequired(), Length(max=2000)])
    reg_nets = SelectField('Network: ', choices=[])
