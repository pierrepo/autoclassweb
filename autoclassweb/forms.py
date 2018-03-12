from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, RadioField, FloatField, SubmitField
from wtforms.validators import Required, DataRequired, Length, Regexp

from autoclassweb import config
app_conf = config.BaseConfig()

class InputDataUpload(FlaskForm):
    submit = SubmitField('Run autoclass@web',
                         render_kw={"class": "btn btn-info", "id": "submit-button"}
                         )
    # real scalar data fields
    scalar_input_file = FileField("Input data file",
                           validators=[]
                           )
    scalar_error = FloatField("Error",
                       default='0.01',
                       render_kw={"placeholder": "default is 0.01"}
                       )
    location_input_file = FileField("Input data file",
                           validators=[]
                           )
    location_error = FloatField("Error",
                       default='0.01',
                       render_kw={"placeholder": "default is 0.01"}
                       )
    discrete_input_file = FileField("Input data file",
                           validators=[]
                           )

class GetJobResults(FlaskForm):
    submit = SubmitField('Get results',
                         render_kw={"class": "btn btn-info btn-lg", "id": "submit-button"}
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
