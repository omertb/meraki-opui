from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from flask_login import current_user
from project.models import Network


class NewNetworkForm(FlaskForm):
    net_name = StringField('Network Name: ', validators=[DataRequired(), Length(max=64)])
    net_template = SelectField('Template: ', choices=[])
    net_type = SelectField('Network Type: ', choices=["appliance", "switch", "wireless"])
    # new_or_existing = SelectField("New", choices=[("new", "New Network"), ("existing", "Existing Network")], )
    net_tag_mselect = SelectMultipleField("Select Tags:", validators=[DataRequired()])
    net_to_copy = SelectField('Select Network: ')

    def set_choices(self):
        tag_list = []
        for group in current_user.groups:
            tag_list.extend(group.tags)
        self.net_tag_mselect.choices = [(tag.id, tag.name) for tag in tag_list]


class AddDevicesForm(FlaskForm):
    serial_nos = TextAreaField('Serial Numbers, one per line: ', validators=[DataRequired(), Length(max=2000)])
    registered_nets = SelectField('Network: ', choices=[])

    def set_choices(self):
        user_networks = Network.query.filter_by(user_id=current_user.id)
        user_groups = current_user.groups
        all_networks = []
        for user_group in user_groups:
            if user_group.networks:
                group_networks = user_group.networks
                all_networks.extend(group_networks)
        all_networks.extend(user_networks)
        all_networks = set(all_networks)
        self.registered_nets.choices = [(network.id, network.name) for network in all_networks]


class CloneSwitchForm(FlaskForm):
    switch_nets = SelectField('Switch Network: ', choices=[])
    source_switch = SelectField('Select Switch:')
    destination_nets = SelectField('Select Destination Switch:', choices=[])
    new_switch = SelectField('New Switch:')

    def set_choices(self):
        user_networks = current_user.networks
        user_groups = current_user.groups
        all_networks = []
        for user_group in user_groups:
            if user_group.networks:
                group_networks = user_group.networks
                all_networks.extend(group_networks)
        all_networks.extend(user_networks)
        all_networks = set(all_networks)
        self.switch_nets.choices = [(network.id, network.name) for network in all_networks if network.type == 'switch']
        self.destination_nets.choices = self.switch_nets.choices
