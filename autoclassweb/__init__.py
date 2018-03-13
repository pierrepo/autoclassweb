import os
import logging

from flask import Flask, jsonify, render_template, url_for, redirect, request, flash, session
from werkzeug import secure_filename

import sys
sys.path.insert(0,'..')
import autoclasswrapper as wrapper

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
    print("We are in: {}".format(os.getcwd()))
    print("Flask is in : {}".format(os.environ['FLASK_HOME']))
    os.chdir(os.environ['FLASK_HOME'])
    print("We are in: {}".format(os.getcwd()))

    # create form
    input_form = forms.InputDataUpload()

    # list current jobs (running and completed)
    job_manager = model.JobManager(app.config['UPLOAD_FOLDER'], 4, alive=4)
    job_manager.autodiscover()

    # handle form data after POST
    # flash(input_form.errors)
    if input_form.validate_on_submit():
        if not (input_form.scalar_input_file.data or input_form.location_input_file.data or input_form.discrete_input_file.data):
            return render_template('index.html', form=input_form, job_m=job_manager)
            print("Missing files in input form!")
        print("input form validated!")
        # create job directory
        job = model.Job()
        job.create_new(app.config['UPLOAD_FOLDER'], app.config['JOB_NAME_LENGTH'])
        print(job.path, job.name)
        # get 'real scalar' input data
        scalar = {}
        if input_form.scalar_input_file.data:
            filename = secure_filename(input_form.scalar_input_file.data.filename)
            input_form.scalar_input_file.data.save(os.path.join(job.path, filename))
            scalar['file'] = filename
            scalar['error'] = input_form.scalar_error.data
        else:
            scalar['file'] = None
            scalar['error'] = None
        # get 'real location' input data
        location = {}
        if input_form.location_input_file.data:
            filename = secure_filename(input_form.location_input_file.data.filename)
            input_form.location_input_file.data.save(os.path.join(job.path, filename))
            location['file'] = filename
            location['error'] = input_form.location_error.data
        else:
            location['file'] = None
            location['error'] = None
        # get 'discrete' input data
        discrete = {}
        if input_form.discrete_input_file.data:
            filename = secure_filename(input_form.discrete_input_file.data.filename)
            input_form.discrete_input_file.data.save(os.path.join(job.path, filename))
            discrete['file'] = filename
            discrete['error'] = None
        else:
            discrete['file'] = None
            discrete['error'] = None
        # prepare data to be stored in session
        session['job_name'] = job.name
        session['job_path'] = job.path
        session['scalar'] = scalar
        session['location'] = location
        session['discrete'] = discrete
        return redirect(url_for('startjob'))

    return render_template('index.html', form=input_form, job_m=job_manager)


@app.route('/startjob', methods=['GET'])
def startjob():
    if 'job_name' in session:
        job_name = session['job_name']
        job_path = session['job_path']
        os.chdir(job_path)
        # create logger
        logger = logging.getLogger("autoclasswrapper")
        logger.setLevel(logging.INFO)
        # create a file handler
        handler = logging.FileHandler('input.log')
        handler.setLevel(logging.INFO)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(handler)
        logger.info("Let's go!")
        # initiate autoclass autoclass wrapper
        clust = wrapper.Input(job_path)
        # load scalar data if any
        scalar = session['scalar']
        if scalar['file']:
            clust.add_input_data(scalar['file'], "real scalar", scalar['error'])
        # load location data if any
        location = session['location']
        if location['file']:
            clust.add_input_data(location['file'], "real location", scalar['location'])
        # load discrete data if any
        discrete = session['discrete']
        if discrete['file']:
            clust.add_input_data(discrete['file'], "real discrete")
        # prepare input files
        clust.merge_dataframes()
        clust.create_db2_file()
        clust.create_hd2_file()
        clust.create_model_file()
        clust.create_sparams_file()
        clust.create_rparams_file()
        clust.create_run_file()
        ## TODO: run clustering
        job = model.Job()
        access_token = job.create_password(app.config['JOB_PASSWD_LENGTH'])
        run_status = "running"
        with open("input.log", "r") as inputfile:
            logcontent = inputfile.read()
        print(run_status, access_token)
        return render_template('startjob.html',
                               job_name=job_name,
                               log_msg=logcontent,
                               run_status=run_status,
                               access_token=access_token)
        #return "Create a new job {} in {} with param {}".format(job.name, job.folder, scalar)
    else:
        return "No job found!"


@app.route('/status', methods=['GET', 'POST'])
def status():
    print("We are in: {}".format(os.getcwd()))
    print("Flask is in : {}".format(os.environ['FLASK_HOME']))
    os.chdir(os.environ['FLASK_HOME'])
    print("We are in: {}".format(os.getcwd()))

    job_manager = model.JobManager(app.config['UPLOAD_FOLDER'], 4, alive=4)
    job_manager.autodiscover()

    return render_template('status.html', job_m=job_manager)


@app.route('/download/<job_name>', methods=['GET', 'POST'])
def download(job_name):
    print("Looking for job {}".format(job_name))

    # create form
    job_form = forms.GetJobResults()
    msg = {}

    job_manager = model.JobManager(app.config['UPLOAD_FOLDER'], 4, alive=4)
    job_manager.autodiscover()

    job_selected = None
    for job in job_manager.completed:
        if job_name == job.name:
            job_selected = job


    if job_selected is None:
        msg['error'] = "Job {} not found or not completed yet. Cannot get results.".format(job_name)
        return render_template('download.html', name=job_name, form=job_form, message=msg)

    if job_form.validate_on_submit():
        print("job form validated!")
        # get password and enforce capital letter
        password = job_form.password.data.upper()
        if password != job_selected.password:
            msg['error'] = "Wrong password! Try again."
            return render_template('download.html', name=job_name, form=job_form, message=msg)
        else:
            msg['download'] = "sdsdsdsdsd"
        return render_template('download.html', name=job_name, form=job_form, message=msg)

    return render_template('download.html', name=job_name, form=job_form, message=msg)
