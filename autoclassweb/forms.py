from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, RadioField, FloatField, SubmitField
from wtforms.validators import Required, DataRequired, Length


class InputDataUpload(FlaskForm):
    job_name = StringField("Enter your job name:",
                            validators=[Required(), Length(min=5, max=30)],
                            )
    input_file = FileField("Input data file:", 
                           validators=[FileRequired()]
                           )
    has_header = RadioField("Is a header present in the input data file?", 
                            choices = [('True','Yes'),('False','No')], 
                            default='False', 
                            validators=[DataRequired()]
                            )
    error = FloatField("Error", 
                       default='0.01', 
                       render_kw={"placeholder": "default is 0.01"}
                       )
    submit = SubmitField('Run autoclass@web', 
                         render_kw={"class": "btn btn-info btn-lg", "id": "submit-button"}
                         )

