import os
import sys
import io
import logging
from pathlib import Path
import psutil
import shutil
import time
import datetime

from flask import Flask, jsonify, render_template, url_for, redirect, request, flash, session, send_from_directory
from werkzeug.utils import secure_filename

from flaskapp import app
from flaskapp import forms
from flaskapp import model

import autoclasswrapper as wrapper

FILE_FOR_FAILURE = "autoclass-run-failure"

# Get Flask app logger.
logger = logging.getLogger("flaskapp")

@app.route('/config', methods=['GET'])
def show_me_config():
    logger.info("Printing app config.")
    return jsonify({
        "FLASK_RESULTS_BY_EMAIL": app.config["FLASK_RESULTS_BY_EMAIL"],
        "FLASK_MAX_JOBS": app.config["FLASK_MAX_JOBS"],
        "FLASK_JOB_TIMEOUT": app.config["FLASK_JOB_TIMEOUT"],
        "FLASK_RESULTS_DURATION": app.config["FLASK_RESULTS_DURATION"],
        "AutoClass C path": app.config["AUTOCLASSC_PATH"],
        "AutoClass C version": app.config["AUTOCLASSC_VERSION"],
        "AutoClassWrapper version": app.config["AUTOCLASSWRAPPER_VERSION"],
        "AutoClassWeb version": app.config["VERSION"]
    })


@app.route('/', methods=('GET', 'POST'))
def index():
    # print error if bad iniatilization
    if app.config["FLASK_INIT_ERROR"]:
        return render_template("error.html")

    # change directory
    os.chdir(os.environ['FLASK_HOME'])
    logger.debug(f"We are in: {os.getcwd()}")

    # create form
    input_form = forms.InputDataUpload()
    # list current jobs (running and completed)
    job_manager = model.JobManager(app.config["RESULTS_FOLDER"],
                                   job_duration=app.config["FLASK_RESULTS_DURATION"])
    job_manager.autodiscover()

    # handle form data after POST request
    # go back to form if no data
    if not input_form.validate_on_submit():
        return render_template("index.html",
                               form=input_form,
                               job_m=job_manager)

    # go back to form if no input file is uploaded
    if not (input_form.scalar_input_file.data
            or input_form.location_input_file.data
            or input_form.discrete_input_file.data):
        flash("Missing files input data! Provide at least one type of data",
              "error")
        return render_template("index.html",
                               form=input_form,
                               job_m=job_manager)

    # go back to form if not email is provided (but required)
    if app.config["FLASK_RESULTS_BY_EMAIL"] \
    and not input_form.mail_address.data:
        flash("Missing e-mail address!", "error")
        return render_template("index.html",
                               form=input_form,
                               job_m=job_manager)

    # eventually create job and process form data
    # create job directory
    job = model.Job()
    job.create_new(app.config["RESULTS_FOLDER"], app.config['JOB_NAME_LENGTH'])
    logger.debug(f"New job name: {job.name}")
    # get e-mail address
    if input_form.mail_address.data:
        mail_address = input_form.mail_address.data
    else:
        mail_address = ""
    # get 'real scalar' input data
    scalar = {"file": None, "error": None}
    if input_form.scalar_input_file.data:
        filename = secure_filename(input_form.scalar_input_file.data.filename)
        input_form.scalar_input_file.data.save(os.path.join(job.path, filename))
        scalar["file"] = filename
        scalar["error"] = input_form.scalar_error.data
    # get 'real location' input data
    location = {"file": None, "error": None}
    if input_form.location_input_file.data:
        filename = secure_filename(input_form.location_input_file.data.filename)
        input_form.location_input_file.data.save(os.path.join(job.path, filename))
        location["file"] = filename
        location["error"] = input_form.location_error.data
    # get 'discrete' input data
    discrete = {"file": None, "error": None}
    if input_form.discrete_input_file.data:
        filename = secure_filename(input_form.discrete_input_file.data.filename)
        input_form.discrete_input_file.data.save(os.path.join(job.path, filename))
        discrete["file"] = filename
        discrete["error"] = None
    # prepare data to be stored in session
    session["job_name"] = job.name
    session["job_path"] = job.path
    session["mail_address"] = mail_address
    session["scalar"] = scalar
    session["location"] = location
    session["discrete"] = discrete
    return redirect(url_for("start"))


@app.route("/start", methods=['GET'])
def start():
    if "job_name" not in session:
            flash("Enter input data first!", "error")
            return redirect(url_for('index'))
    # "job_name" is in session,
    # so we prepare input data and run job
    logger.debug(session)
    # keep value of job_name for further use
    job_name = session["job_name"]
    os.chdir(session["job_path"])
    # re-create job and update summary file
    job = model.Job()
    job.create_from_path(session["job_path"])
    job.write_summary(f"reference: {job_name}")
    job.write_summary(
         "date-start: "
        f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    job.write_summary(f"email: {session['mail_address']}")
    # Call logger from autoclasswrapper.
    wrapper_logger = logging.getLogger("autoclasswrapper")
    wrapper_logger.setLevel(logging.DEBUG)
    # Create a file handler.
    # delay=True only opens file at first writing
    # https://docs.python.org/3/library/logging.handlers.html
    handler = logging.FileHandler("autoclass_in.log", delay=True)
    handler.setLevel(logging.INFO)
    # create a stream handler
    log_capture_string = io.StringIO()
    handler_stream = logging.StreamHandler(log_capture_string)
    handler_stream.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter(("%(asctime)s :: "
                                   "%(levelname)-8s :: "
                                   "%(message)s"
                                   ), datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    handler_stream.setFormatter(formatter)
    # add handlers to the logger
    wrapper_logger.addHandler(handler)
    wrapper_logger.addHandler(handler_stream)
    # initiate autoclass wrapper input
    clust = wrapper.Input()
    # load scalar data if any
    scalar = session['scalar']
    if scalar['file']:
        clust.add_input_data(scalar['file'],
                             "real scalar",
                             scalar['error'])
    # load location data if any
    location = session['location']
    if location['file']:
        clust.add_input_data(location['file'],
                             "real location",
                             location['error'])
    # load discrete data if any
    discrete = session['discrete']
    if discrete['file']:
        clust.add_input_data(discrete['file'],
                             "discrete")
    # prepare input files
    clust.prepare_input_data()
    clust.create_db2_file()
    clust.create_hd2_file()
    clust.create_model_file()
    clust.create_sparams_file(
        max_duration=app.config["FLASK_JOB_TIMEOUT"]*3600)
    clust.create_rparams_file()
    # check ERROR in log
    log_content = log_capture_string.getvalue()
    session["log"] = log_content
    if "ERROR" in log_content:
        session["status"] = "failed"
        job.write_summary("status: failed\nrunning-time: 0")
        # Remove "job_name" from session
        # to avoid running twice the same job upon refresh.
        session.pop("job_name")
        return render_template("start.html",
                               job_name=job_name)
    # No ERROR, then keep going.
    session["status"] = "running"
    nb_line, nb_col = clust.full_dataset.df.shape
    job.write_summary(f"data-size: {nb_line} lines x {nb_col+1} columns")
    # Initiate autoclass wrapper run.
    run = wrapper.Run()
    # prepare master script to run autoclass.
    run.create_run_file()
    # Add scripts to export and send results.
    shutil.copy("../../export_results.py", "./")
    shutil.copy("../../send_results.py", "./")
    with open(run.root_name + ".sh", "a") as script_file:
        script_file.write("# added by autoclassweb\n")
        script_file.write("python3 export_results.py\n")
        if app.config["FLASK_RESULTS_BY_EMAIL"]:
            script_file.write(
                "python3 send_results.py "
                f"{session['mail_address']}\n")
    # Run AutoClass C.
    run.run(job_name)
    # Wait that the job starts.
    time.sleep(2)
    if Path(Path.cwd(), FILE_FOR_FAILURE).exists():
        log_file = Path(Path.cwd(), "autoclass-search.log")
        if log_file.exists():
            session["log"] = log_file.read_text()
        log_file_2 = Path(Path.cwd(), "autoclass.log")
        if log_file_2.exists():
            session["log"] += "\n" + "=" * 80 + "\n"
            session["log"] += log_file_2.read_text()
        session["status"] = "failed"
        job.write_summary("status: failed\nrunning-time: 0")
        # Remove "job_name" from session
        # to avoid running twice the same job upon refresh.
        session.pop("job_name")
        return render_template("start.html",
                               job_name=job_name)

    # Remove "job_name" from session
    # to avoid running twice the same job upon refresh.
    session.pop("job_name")
    return render_template("start.html",
                           job_name=job_name)


@app.route('/status', methods=['GET', 'POST'])
def status():
    os.chdir(os.environ['FLASK_HOME'])
    job_manager = model.JobManager(app.config["RESULTS_FOLDER"],
                                   job_duration=app.config["FLASK_RESULTS_DURATION"])
    job_manager.autodiscover()
    return render_template('status.html', job_m=job_manager)


@app.route('/download/', methods=['GET'])
@app.route('/download/<job_name>', methods=['GET'])
def download(job_name=None):
    if not job_name:
        flash("You need to specify job name.", "error")
        return redirect(url_for('status'))

    # retrieve all jobs
    job_manager = model.JobManager(app.config["RESULTS_FOLDER"],
                                              job_duration=app.config["FLASK_RESULTS_DURATION"])
    job_manager.autodiscover()
    # find wanted job
    job_selected = None
    for job in job_manager.stopped:
        if job_name == job.name:
            job_selected = job

    if job_selected is None:
        msg = (f"Job '{job_name}' not found, failed or not completed yet. "
                "Cannot get results.")
        flash(msg, "error")
        return redirect(url_for('status'))
    fullpath = os.path.join(os.environ['FLASK_HOME'], job_selected.path)
    return send_from_directory(fullpath,
                               os.path.basename(job_selected.results_file),
                               as_attachment=True)


@app.route("/help", methods=["GET"])
def help():
    return render_template("help.html")
