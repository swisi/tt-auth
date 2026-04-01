from wtforms import Form, StringField, PasswordField, SelectField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, URL, NumberRange


class LoginForm(Form):
    username = StringField('Benutzername', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Passwort', validators=[DataRequired()])


class UserForm(Form):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Passwort', validators=[Optional(), Length(min=8, max=128)])
    role = SelectField('Rolle', choices=[('user', 'Benutzer'), ('admin', 'Administrator')])
    is_active = BooleanField('Aktiv', default=True)


class ServiceForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(max=255)])
    icon = StringField('Bootstrap Icon', validators=[Optional(), Length(max=64)], default='grid')
    description = TextAreaField('Beschreibung', validators=[Optional(), Length(max=255)])
    required_role = SelectField('Mindestrolle', choices=[('user', 'Benutzer'), ('admin', 'Administrator')])
    is_active = BooleanField('Aktiv', default=True)
    sort_order = IntegerField('Reihenfolge', validators=[Optional(), NumberRange(min=0)], default=0)
