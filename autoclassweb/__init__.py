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
        print("input form validated!")
        # create job directory
        job = model.Job()
        job.create_new(app.config['UPLOAD_FOLDER'], app.config['JOB_NAME_LENGTH'])
        print(job.path, job.name)
        # get scalar input data
        filename = secure_filename(input_form.scalar_input_file.data.filename)
        input_form.scalar_input_file.data.save(os.path.join(job.path, filename))
        scalar = {}
        scalar['file'] = filename
        scalar['error'] = input_form.scalar_error.data
        # prepare data to be stored in session
        session['job_name'] = job.name
        session['job_path'] = job.path
        session['scalar'] = scalar
        return redirect(url_for('startjob'))

    return render_template('index.html', form=input_form, job_m=job_manager)


@app.route('/startjob', methods=['GET'])
def startjob():
    if 'job_name' in session:
        job_name = session['job_name']
        job_path = session['job_path']
        scalar = session['scalar']
        scalar_clust= autoclass.Autoclass('scalar', job_path, scalar['file'], scalar['error'])
        scalar_clust.prepare_input_files()
        run_status = scalar_clust.run()
        access_token = scalar_clust.set_password(app.config['JOB_PASSWD_LENGTH'])
        content_files = scalar_clust.print_files()
        print(run_status, access_token)
        return render_template('startjob.html',
                               job_name=job_name, 
                               msg=scalar_clust.log.msg.split('\n'),
                               run_status=run_status,
                               access_token=access_token,
                               content_files=content_files)
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

    # create form 
    job_form = forms.GetJobResults()

    if job_form.validate_on_submit():
        print("job form validated!")
        name = job_form.name.data
        password = job_form.password.data
        print(name, password)
        print(job_manager.completed)
        """
        # create job directory
        job = model.Job()
        job.create_new(app.config['UPLOAD_FOLDER'], app.config['JOB_NAME_LENGTH'])
        print(job.path, job.name)
        # get scalar input data
        filename = secure_filename(input_form.scalar_input_file.data.filename)
        input_form.scalar_input_file.data.save(os.path.join(job.path, filename))
        scalar = {}
        scalar['file'] = filename
        scalar['error'] = input_form.scalar_error.data
        # prepare data to be stored in session
        session['job_name'] = job.name
        session['job_path'] = job.path
        session['scalar'] = scalar
        return redirect(url_for('startjob'))
        """

    return render_template('status.html', form=job_form, job_m=job_manager)