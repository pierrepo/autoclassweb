import os
import sys
import io
import logging
import psutil
import shutil
from flask import Flask, jsonify, render_template, url_for, redirect, request, flash, session, send_from_directory
from werkzeug import secure_filename

sys.path.insert(0,'.')
import autoclasswrapper as wrapper

os.environ["FLASK_RES_LINK"] = "True"
os.environ["FLASK_RES_MAIL"] = "False"

import config
import forms
import model

#  set Flask base directory
os.environ["FLASK_HOME"] = os.getcwd()
print("FLASK_HOME is {}".format(os.environ["FLASK_HOME"]))

# instantiate Flask app
app = Flask(__name__)

# search autoclass executable in path
autoclass_path = shutil.which("autoclass")
if autoclass_path:
    print("autoclass found in {}".format(autoclass_path))
else:
    print("autoclass not found in path!")
    print("Exiting autoclassweb")
    sys.exit(1)


# load user Parameters
config.read_ini("autoclassweb.ini")

# set config
app.config.from_object('config.TestingConfig')
if "MAX_JOB" not in app.config:
    app.config["MAX_JOB"] = psutil.cpu_count() - 1
    print("MAX JOB defined as {}".format(app.config["MAX_JOB"]))

@app.route('/ping', methods=['GET'])
def ping_pong():
    print(app.config)
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@app.route('/', methods=('GET', 'POST'))
def index():
    print("We are in: {}".format(os.getcwd()))

    session["flask_res_mail"] = False
    if os.environ["FLASK_RES_MAIL"] == "True":
        session["flask_res_mail"] = True
    # create form
    input_form = forms.InputDataUpload()

    # list current jobs (running and completed)
    job_manager = model.JobManager(app.config['UPLOAD_FOLDER'],
                                   app.config["MAX_JOB"],
                                   alive=4)
    job_manager.autodiscover()

    # handle form data after POST
    if input_form.validate_on_submit():

        if not (input_form.scalar_input_file.data
                or input_form.location_input_file.data
                or input_form.discrete_input_file.data):
            flash("Missing files input data! Provide at least one type of data", "error")
            return render_template('index.html', form=input_form, job_m=job_manager)

        if os.environ["FLASK_RES_MAIL"] == "True" \
           and not input_form.mail_address.data:
            flash("Missing e-mail address!", "error")
            return render_template('index.html', form=input_form, job_m=job_manager)

        # create job directory
        job = model.Job()
        job.create_new(app.config['UPLOAD_FOLDER'], app.config['JOB_NAME_LENGTH'])
        print(job.path, job.name)
        # get e-mail address
        if input_form.mail_address.data:
            mail_address = input_form.mail_address.data
        else:
            mail_address = ""
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
        session['mail_address'] = mail_address
        session['scalar'] = scalar
        session['location'] = location
        session['discrete'] = discrete
        return redirect(url_for('startjob'))

    return render_template('index.html',
                           form=input_form,
                           job_m=job_manager)


@app.route('/startjob', methods=['GET'])
def startjob():
    if 'job_name' in session:
        print(session)
        mail_address = session["mail_address"]
        job_name = session['job_name']
        job_path = session['job_path']
        os.chdir(job_path)
        # create logger
        logger = logging.getLogger("autoclasswrapper")
        logger.setLevel(logging.DEBUG)
        # create a file handler
        handler = logging.FileHandler('input.log')
        handler.setLevel(logging.INFO)
        # create a stream handler
        log_capture_string = io.StringIO()
        handler_stream = logging.StreamHandler(log_capture_string)
        handler_stream.setLevel(logging.INFO)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s :: %(levelname)-8s :: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        handler_stream.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(handler)
        logger.addHandler(handler_stream)
        # initiate autoclass autoclass wrapper
        clust = wrapper.Input()
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
        # prepare results export and send
        import shutil
        shutil.copy("../../export_results.py", "./")
        with open("clust.sh", "a") as f:
            f.write("python3 export_results.py {}".format(mail_address))
        # run autoclass
        clust.run(job_name)
        # add password
        job = model.Job()

        #with open("input.log", "r") as inputfile:
        #    logcontent = inputfile.read()
        log_content = log_capture_string.getvalue()
        log_capture_string.close()

        if "ERROR" not in log_content:
            status = "running"
        else:
            status = "failed"
        return render_template('startjob.html',
                               job_name=job_name,
                               status=status,
                               log=log_content)
    else:
        return "No job found!"


@app.route('/status', methods=['GET', 'POST'])
def status():
    os.chdir(os.environ['FLASK_HOME'])
    session["link_results"] = False
    if os.environ["FLASK_RES_LINK"] == "True":
        session["link_results"] = True
    job_manager = model.JobManager(app.config['UPLOAD_FOLDER'], 4, alive=4)
    job_manager.autodiscover()
    return render_template('status.html', job_m=job_manager)


@app.route('/download/<job_name>', methods=['GET'])
def download(job_name):
    print(job_name)
    if not session["link_results"]:
        msg = "Results download is not allowed."
        print(msg)
        flash(msg, "error")
        return redirect(url_for('status'))

    # retrieve all jobs
    job_manager = model.JobManager(app.config['UPLOAD_FOLDER'], 4, alive=4)
    job_manager.autodiscover()
    # find wanted job
    job_selected = None
    for job in job_manager.stopped:
        if job_name == job.name:
            job_selected = job

    if job_selected is None:
        msg = ("Job {} not found, failed or not completed yet."
               "Cannot get results.").format(job_name)
        flash(msg, "error")
        return redirect(url_for('status'))
    fullpath = os.path.join(os.environ['FLASK_HOME'], job_selected.path)
    return send_from_directory(fullpath,
                               os.path.basename(job_selected.results_file),
                               as_attachment=True)
