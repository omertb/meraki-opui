from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from project.models import Group, User


class GroupMembershipForm(FlaskForm):
    new_group_name = StringField('New Group Name: ', validators=[DataRequired(), Length(min=4, max=32)])
    select_group = SelectMultipleField('Select Groups: ', validators=[DataRequired()])
    select_user = SelectMultipleField('Select Groups: ', validators=[DataRequired()])

    def set_choices(self):
        self.select_group.choices = [(group.id, group.name) for group in Group.query.all()]
        self.select_user.choices = [(user.id, user.name) for user in User.query.all()]
