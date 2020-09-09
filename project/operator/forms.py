from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from flask_login import current_user


class NewNetworkForm(FlaskForm):
    net_name = StringField('Network Name: ', validators=[Length(max=64)])
    net_template = SelectField('Template: ', choices=[])
    net_type = SelectField('Network Type: ', choices=["appliance", "switch", "wireless"])
    new_or_existing = SelectField("New", choices=[("new", "New Network"), ("existing", "Existing Network")], )
    net_tag_mselect = SelectMultipleField("Select Tags:", validators=[DataRequired()])

    def set_choices(self):
        tag_list = []
        for group in current_user.groups:
            tag_list.extend(group.tags)
        self.net_tag_mselect.choices = [(tag.id, tag.name) for tag in tag_list]


class AddDevicesForm(FlaskForm):
    serial_nos = TextAreaField('Serial Numbers, one per line: ', validators=[DataRequired(), Length(max=2000)])
    registered_nets = SelectField('Network: ', choices=[])
