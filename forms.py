from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class LevelForm(Form):
   name = StringField('level1', validators=[DataRequired()])
