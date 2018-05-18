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


def send_results_mail(host, port, SSL, login, password, sender,
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
            mailserver.login(login,password)
            mailserver.sendmail(login, mail_address, msg_str)
            mailserver.quit()
        else:
            mailserver = smtplib.SMTP(host, port, timeout=timeout)
            mailserver.sendmail(sender, mail_address, msg_str)
            mailserver.quit()
        logger.info("Successfully sent email.")
    except:
        logger.error("Error: unable to send email.")





logger = logging.getLogger("autoclasswrapper")
logger.setLevel(logging.DEBUG)
# create a file handler
handler = logging.FileHandler('output.log')
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
results = wrapper.Output()
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



try:
    mail_address = sys.argv[1]
    logger.info("E-mail address is: {}".format(mail_address))
except:
    mail_address = ""
    logger.info("E-mail address not defined. Results cannot be send")


if os.environ.get("FLASK_RES_MAIL", "False") == "True" \
    and mail_address != "" \
    and os.environ.get("FLASK_MAIL_HOST", "") != "" \
    and os.environ.get("FLASK_MAIL_PORT", "") != "0" \
    and os.environ.get("FLASK_MAIL_SENDER", "") != "":

    job_id = os.getcwd().split(".")[-1]

    if os.environ["FLASK_MAIL_SSL"] == "True":
        SSL = True
    else:
        SSL = False
    send_results_mail(os.environ["FLASK_MAIL_HOST"],
                      int(os.environ["FLASK_MAIL_PORT"]),
                      SSL,
                      os.environ["FLASK_MAIL_LOGIN"],
                      os.environ["FLASK_MAIL_PASSWORD"],
                      os.environ["FLASK_MAIL_SENDER"],
                      mail_address,
                      os.getcwd().split(".")[-1],
                      outputzip)

logger.info("Results export done!")
