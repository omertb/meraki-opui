from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from project.models import Group, User, Network, Tag


class GroupMembershipForm(FlaskForm):
    new_group_name = StringField('New Group Name: ', validators=[DataRequired(), Length(min=4, max=32)])
    select_group = SelectMultipleField('Select Groups: ', validators=[DataRequired()])
    select_user = SelectMultipleField('Select Users: ', validators=[DataRequired()])
    select_network = SelectMultipleField('Select Networks: ', validators=[DataRequired()])

    def set_choices(self):
        self.select_group.choices = [(group.id, group.name) for group in Group.query.all()]
        self.select_user.choices = [(user.id, user.name) for user in User.query.all()]


class NetworkOwnershipForm(FlaskForm):
    # select_network = SelectMultipleField('Select Networks: ', validators=[DataRequired()])
    select_group = SelectMultipleField('Select Groups: ', validators=[DataRequired()])
    select_tag = SelectMultipleField('Select Tags: ', validators=[DataRequired()])

    def set_choices(self):
        self.select_group.choices = [(group.id, group.name) for group in Group.query.all()]
        self.select_tag.choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        # self.select_network.choices = [(network.id, network.name) for network in Network.query.all()]
