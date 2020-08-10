from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, AnyOf


class NetworkDeviceForm(FlaskForm):
    net_name = StringField('Network Name: ', validators=[DataRequired()])
    template_name = SelectField('Template: ', choices=[])
    serial_nos = TextAreaField('Serial Numbers, one per line: ', validators=[DataRequired()])
    reg_nets = SelectMultipleField('Network: ', choices=[], validate_choice=True)
