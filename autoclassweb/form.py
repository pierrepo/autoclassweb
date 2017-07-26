from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, RadioField, FloatField, SubmitField
from wtforms.validators import DataRequired


class InputDataUpload(FlaskForm):
    input_file = FileField("Data file", validators=[FileRequired()])
    has_header = RadioField("Is a header present in the input file?", choices = [('True','Yes'),('False','No')], default='False', validators=[DataRequired()])
    error = FloatField("Error", render_kw={"placeholder": "default is 0.01"})
    submit = SubmitField('Run autoclass@web', render_kw={"class": "btn btn-info btn-lg", "id": "submit-button"})