import glob
import io
import logging
import os
from pathlib import Path
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders


FILE_FOR_SUCCESS = "autoclass_run_success"


def get_email():
    """Get email address to send results toself.

    Email adress is provided as argument in the command line.
    """
    email_address = None
    try:
        email_address = sys.argv[1]
    except:
        pass
    return email_address


def get_job_name():
    """Extract job name from summary file."""
    summary_found = glob.glob("*summary.txt")
    if summary_found:
        summary_name = summary_found[0]
        if os.path.exists(summary_name):
            with open(summary_name, "r") as summary_file:
                for line in summary_file:
                    if "reference" in line:
                        job_name = line.split()[1]
                        return job_name
    return None


def send_results_mail(host, port, SSL, username, password, sender,
                      mail_address,
                      server_url, job_id,
                      timeout=5):
    """Send mail with results

    Docs:
    http://naelshiab.com/tutorial-send-email-python/
    https://stackoverflow.com/questions/3362600/how-to-send-email-attachments
    """
    # build message
    message = """Hello,

your autoclass@web job is now completed.

Your results are available in the following link:

{}/{}/{}

Let's hope your data have been nicely classified ;-)

Please note that your results will be available for one week only. After this period of time, they will be automatically deleted.

Regards.

Autoclass@web Bot
""".format(server_url, "download", job_id)
    msg = MIMEMultipart()
    msg['From'] = "Autoclass@web Bot <{}>".format(sender)
    msg['To'] = mail_address
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Your autoclass@web job {} is ready".format(job_id)
    msg.attach(MIMEText(message))
    msg_str = msg.as_string()
    try:
        if SSL == True:
            logger.info("Mail with SSL")
            mailserver = smtplib.SMTP_SSL(host, port, timeout=timeout)
            if os.environ["FLASK_ENV"] == "development":
                mailserver.set_debuglevel(1)
            mailserver.login(username,password)
            sender = username
        else:
            logger.info("Mail without SSL")
            mailserver = smtplib.SMTP(host, port, timeout=timeout)
            if os.environ["FLASK_ENV"] == "development":
                mailserver.set_debuglevel(1)
        response = mailserver.sendmail(sender, mail_address, msg_str)
        mailserver.quit()
        logger.info("Successfully sent email to {}.".format(mail_address))
    except:
        logger.exception("Error: unable to send results by e-mail.")


if __name__ == "__main__":
    logger = logging.getLogger("autoclasswrapper")
    logger.setLevel(logging.DEBUG)
    # create a file handler
    handler = logging.FileHandler("send.log")
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

    # check AutoClass C worked without error
    if not Path(Path.cwd(), FILE_FOR_SUCCESS).exists():
        logger.critical("Cannot find file {} in {}".format(FILE_FOR_SUCCESS, str(Path.cwd())))
        sys.exit(1)

    # get email address from command line
    email_address = get_email()
    if not email_address:
        logger.critical("Email address is not defined or not found.")
    else:
        logger.info("Email address is {}".format(email_address))

    # get job name from 'summary.txt'
    job_name = get_job_name()
    if not job_name:
        logger.critical("Cannot find job name in summary file.")
    else:
        logger.info("Job name is {}".format(job_name))

    if os.environ.get("FLASK_SERVER_URL", "") == "":
        logger.critical("FLASK_SERVER_URL not defined.")

    if os.environ.get("MAIL_SERVER", "") == "":
        logger.critical("MAIL_SERVER not defined.")

    if os.environ.get("MAIL_PORT", "0") == "0":
        logger.critical("MAIL_PORT not defined.")

    if os.environ.get("MAIL_USE_TLS", "False") == "True":
        SSL = True
    else:
        SSL = False

    send_results_mail(os.environ["MAIL_SERVER"],
                      int(os.environ["MAIL_PORT"]),
                      SSL,
                      os.environ.get("MAIL_USERNAME", ""),
                      os.environ.get("MAIL_PASSWORD", ""),
                      "autoclass-bot@no-reply.net",
                      email_address,
                      os.environ["FLASK_SERVER_URL"],
                      job_name)
    logger.info("Results sent!")
