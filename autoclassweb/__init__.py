import os

from flask import Flask, jsonify, render_template, url_for, redirect, request, flash, session
from werkzeug import secure_filename


# instantiate the app
app = Flask(__name__)

# set config
app.config.from_object('autoclassweb.config.TestingConfig')


@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@app.route('/', methods=('GET', 'POST'))
def index():
    input_form = forms.InputDataUpload()

    if request.method == 'POST':
        flash(input_form.errors)
        if input_form.validate_on_submit():
            print("input form validated!")
            name = input_form.job_name.data
            job = model.Job(app.config['UPLOAD_FOLDER'], name=name)
            print(job.folder, job.name)
            filename = secure_filename(input_form.input_file.data.filename)
            input_form.input_file.data.save(os.path.join(job.root, job.folder, filename))
            return redirect(url_for('startjob'))
        else:
            print("Form not validated")
            flash(input_form.errors)

    return render_template('index.html', form=input_form)


@app.route('/startjob', methods=['GET'])
def startjob():
    return "OK"