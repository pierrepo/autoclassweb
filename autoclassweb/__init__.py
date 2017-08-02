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
    # create form 
    input_form = forms.InputDataUpload()


    # list current jobs (running and completed)
    job_manager = model.JobManager(app.config['UPLOAD_FOLDER'], 4)
    job_manager.autodiscover()
    jobs={"running": [], "completed": [], "max": 4}
    for job in job_manager.jobs:
        if job.is_running:
            jobs["running"].append(job.name)
        else:
            jobs["completed"].append(job.name)

    # handle form data after POST
    # flash(input_form.errors)
    if input_form.validate_on_submit():
        print("input form validated!")
        # get job name and create directory
        name = input_form.job_name.data
        job = model.Job(app.config['UPLOAD_FOLDER'], name=name)
        print(job.folder, job.name)
        # get scalar input data
        filename = secure_filename(input_form.scalar_input_file.data.filename)
        input_form.scalar_input_file.data.save(os.path.join(job.root, job.folder, filename))
        scalar = {}
        scalar['file'] = filename
        scalar['header'] = input_form.scalar_has_header.data
        scalar['error'] = input_form.scalar_error.data
        # prepare data to be stored in session
        session['job_name'] = job.name
        session['scalar'] = scalar
        return redirect(url_for('startjob'))

    return render_template('index.html', form=input_form, jobs=jobs)


@app.route('/startjob', methods=['GET'])
def startjob():
    if 'job_name' in session:
        name = session['job_name']
        job = model.Job(app.config['UPLOAD_FOLDER'], name=name)
        scalar = session['scalar']
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], job.folder)
        scalar_input = io.AutoclassInput('scalar', full_path, scalar['file'], scalar['header'], scalar['error'])
        return render_template('startjob.html', msg=scalar_input.log.msg.split('\n'))
        #return "Create a new job {} in {} with param {}".format(job.name, job.folder, scalar)
    else:
        return "No job found!"


@app.route('/status', methods=['GET'])
def status():
    job_manager = model.JobManager(app.config['UPLOAD_FOLDER'], 4)
    job_manager.autodiscover()

    return render_template('status.html', jobs=job_manager.jobs)