import smtplib
import os
import io
import sys
import autoclasswrapper as wrapper
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders


def get_job_name(summary_name="summary.txt"):
    """Extract job name from summary file
    """
    job_name = ""
    if os.path.exists(summary_name):
        with open(summary_name, "r") as summary_file:
            for line in summary_file:
                if "reference" in line:
                    job_name = line.split()[1]
                    return job_name
    return job_name


def send_results_mail(host, port, SSL, username, password, sender,
                      mail_address, job_id, results_file, timeout=5):
    """Send mail with results

    Docs:
    http://naelshiab.com/tutorial-send-email-python/
    https://stackoverflow.com/questions/3362600/how-to-send-email-attachments
    """
    # build message
    message = """Hello,

your autoclass job is now completed.

Your results are attached. Let's hope your data clustered nicely ;-)

Regards.

AutoclassWeb Bot
"""
    msg = MIMEMultipart()
    msg['From'] = "AutoclassWeb Bot <{}>".format(sender)
    msg['To'] = mail_address
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Your autoclass-web job {} is ready".format(job_id)

    msg.attach(MIMEText(message))
    part = MIMEBase('application', "octet-stream")
    with open(results_file, 'rb') as f:
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    'attachment; filename="{}"'.format(results_file))
    msg.attach(part)
    msg_str = msg.as_string()
    try:
        if SSL:
            mailserver = smtplib.SMTP_SSL(host, port, timeout=timeout)
            if os.environ["FLASK_ENV"] == "development":
                mailserver.set_debuglevel(1)
            mailserver.login(username,password)
            sender = username
        else:
            mailserver = smtplib.SMTP(host, port, timeout=timeout)
            if os.environ["FLASK_ENV"] == "development":
                mailserver.set_debuglevel(1)
        response = mailserver.sendmail(sender, mail_address, msg_str)
        mailserver.quit()
        logger.info("Successfully sent email to {}.".format(mail_address))
    except:
        logger.exception("Error: unable to send results by e-mail.")


logger = logging.getLogger("autoclasswrapper")
logger.setLevel(logging.DEBUG)
# create a file handler
handler = logging.FileHandler("output.log")
handler.setLevel(logging.INFO)
# create a stream handler
log_capture_string = io.StringIO()
handler_stream = logging.StreamHandler(log_capture_string)
handler_stream.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter("%(asctime)s :: %(levelname)-8s :: %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
handler_stream.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
logger.addHandler(handler_stream)

# prepare results
results = wrapper.Output()
logger.info("autoclasswrapper {}".format(wrapper.__version__))
results.extract_results()
results.aggregate_input_data()
results.write_cdt()
results.write_cdt(with_proba=True)
results.write_cluster_stats()
outputzip = results.wrap_outputs()
log_content = log_capture_string.getvalue()
# write 'job-completed' file upon success
if "ERROR" not in log_content:
    with open("job-completed", "w") as f:
        f.write("\n")
#log_capture_string.close()
# get job name from 'summary.txt'
job_name = get_job_name()
# rename result file with job name
outputzip_new = "{}-{}.zip".format(outputzip[:-4], job_name)
os.rename(outputzip , outputzip_new)
logger.info("Renamed {} into {}".format(outputzip, outputzip_new))

try:
    mail_address = sys.argv[1]
    logger.info("E-mail address is: {}".format(mail_address))
except:
    mail_address = ""
    logger.warning("E-mail address not defined. Results cannot be send")


if os.environ.get("FLASK_RESULTS_BY_EMAIL", "False") == "True" \
    and mail_address != "" \
    and os.environ.get("MAIL_SERVER", "") != "" \
    and os.environ.get("MAIL_PORT", "0") != "0":

    if os.environ["MAIL_USE_TLS"] == "True":
        SSL = True
    else:
        SSL = False
    send_results_mail(os.environ["MAIL_SERVER"],
                      int(os.environ["MAIL_PORT"]),
                      SSL,
                      os.environ.get("MAIL_USERNAME", ""),
                      os.environ.get("MAIL_PASSWORD", ""),
                      "autoclass-bot@no-reply.net",
                      mail_address,
                      job_name,
                      outputzip_new)

logger.info("Results export done!")
