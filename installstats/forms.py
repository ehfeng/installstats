from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

from installstats.models import SourceLanguage

class SourceForm(FlaskForm):
    language = SelectField('language', choices=[(s.name, s.value) for s in list(SourceLanguage)],
        validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
