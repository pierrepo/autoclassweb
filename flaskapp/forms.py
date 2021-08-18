from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import FloatField, SubmitField

class InputDataUpload(FlaskForm):
    submit = SubmitField("Run AutoClassWeb",
                         render_kw={"class": "btn btn-info", "id": "submit-button"}
                         )
    # real scalar data fields
    scalar_input_file = FileField("Input data file",
                           validators=[]
                           )
    scalar_error = FloatField("Error",
                       default="0.01"
                       )
    location_input_file = FileField("Input data file",
                           validators=[]
                           )
    location_error = FloatField("Error",
                       default="0.01"
                       )
    discrete_input_file = FileField("Input data file",
                           validators=[]
                           )
