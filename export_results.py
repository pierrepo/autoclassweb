import glob
import io
import logging
import os
import sys

import autoclasswrapper as wrapper


def get_job_name():
    """Extract job name from summary file
    """
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


def write_summary(text):
    """Write summary of job
    """
    summary_found = glob.glob("*summary.txt")
    if summary_found:
        summary_name = summary_found[0]
        if os.path.exists(summary_name):
            with open(summary_name, "a") as summary_file:
                summary_file.write("{}\n".format(text))
    else:
        logger.error("Cannot find summary file.")


if __name__ == "__main__":
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
    # write final status
    if "ERROR" in log_content:
        write_summary("status: failed")
    else:
        write_summary("status: completed")
    #log_capture_string.close()

    # get job name from summary file
    job_name = get_job_name()
    if not job_name:
        logger.critical("Cannot find job name in summary file.")
    else:
        logger.info("Job name is {}".format(job_name))

    # rename result file with job name
    outputzip_new = "{}-{}.zip".format(outputzip[:-4], job_name)
    os.rename(outputzip , outputzip_new)
    logger.info("Renamed {} into {}".format(outputzip, outputzip_new))
    logger.info("Results exported!")
