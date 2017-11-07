from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, RadioField, FloatField, SubmitField
from wtforms.validators import Required, DataRequired, Length


class InputDataUpload(FlaskForm):
    submit = SubmitField('Run autoclass@web', 
                         render_kw={"class": "btn btn-info btn-lg", "id": "submit-button"}
                         )
    # real scalar data fields
    scalar_input_file = FileField("Input data file:", 
                           validators=[FileRequired()]
                           )
    scalar_error = FloatField("Error", 
                       default='0.01', 
                       render_kw={"placeholder": "default is 0.01"}
                       )


