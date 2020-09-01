from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length
from project.models import Group


class GroupMembershipForm(FlaskForm):
    new_group_name = StringField('New Group Name: ', validators=[DataRequired(), Length(max=64)])
    select_group = SelectMultipleField('Select Groups: ', validators=[DataRequired()])

    def set_choices(self):
        self.select_group.choices = [(group.id, group.name) for group in Group.query.all()]
