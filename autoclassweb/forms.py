from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, RadioField, FloatField, SubmitField
from wtforms.validators import Required, DataRequired, Length, Regexp

from autoclassweb import config 
app_conf = config.BaseConfig()

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


class GetJobResults(FlaskForm):
    print("size", app_conf.JOB_NAME_LENGTH)
    submit = SubmitField('Get results',
                         render_kw={"class": "btn btn-info btn-lg", "id": "submit-button"}
                         )
    # get job name
    name = StringField("Name:",
                           validators=[Required(), 
                                       Length(min=app_conf.JOB_NAME_LENGTH, 
                                              max=app_conf.JOB_NAME_LENGTH,
                                              message="Name must have exactly %(min)d characters."), 
                                       Regexp('^\w+$', 
                                              message="Name must contain only letters and numbers")]
                            )
    # get job password
    password = StringField("Password:",
                               validators=[Required(), 
                                           Length(min=app_conf.JOB_PASSWD_LENGTH, 
                                                  max=app_conf.JOB_PASSWD_LENGTH, 
                                                  message="Password must have exactly %(min)d characters."),
                                           Regexp('^\w+$', 
                                                  message="Password must contain only letters and numbers")]
                              )