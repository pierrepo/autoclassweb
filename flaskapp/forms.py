from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, RadioField, FloatField, SubmitField
from wtforms.validators import Required, DataRequired, Length

class InputDataUpload(FlaskForm):
    mail_address = StringField("Mail address",
                               validators=[]
                              )
    submit = SubmitField('Run autoclass@web',
                         render_kw={"class": "btn btn-info", "id": "submit-button"}
                         )
    # real scalar data fields
    scalar_input_file = FileField("Input data file",
                           validators=[]
                           )
    scalar_error = FloatField("Error",
                       default='0.01'
                       )
    location_input_file = FileField("Input data file",
                           validators=[]
                           )
    location_error = FloatField("Error",
                       default='0.01'
                       )
    discrete_input_file = FileField("Input data file",
                           validators=[]
                           )
