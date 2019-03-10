import io
import logging
import os
from pathlib import Path
import shutil
import sys
import zipfile

import autoclasswrapper as wrapper


FILE_FOR_SUCCESS = "autoclass-run-success"

def wrap_output_files():
    """Wrap output files in a zip archive."""
    DIR_NAME = Path.cwd().parts[-1]
    OUTPUT_FILES = ["autoclass_in.log",
                    "autoclass_out.tsv",
                    "autoclass_out.cdt",
                    "autoclass_out_withproba.cdt",
                    "autoclass_out_stats.tsv",
                    "autoclass_out_dendrogram.png"]
    OUTPUT_FILES_RENAMED = \
    [name.replace("autoclass",
                  "{}_autoclass".format(DIR_NAME))
     for name in OUTPUT_FILES]
    # rename files
    for name_in, name_out in zip(OUTPUT_FILES,
                                 OUTPUT_FILES_RENAMED):
        os.rename(name_in, name_out)
    # create archive
    zipname = "{}_autoclass.zip".format(DIR_NAME)
    with zipfile.ZipFile(zipname, "w") as outputzip:
        for filename in OUTPUT_FILES_RENAMED:
            if os.path.exists(filename):
                outputzip.write(filename)
    logger.info("Results exported!")


def get_running_time():
    """Compute running time.

    Format is HH:MM:SS
    """
    time_older, file_older = min((f.stat().st_mtime, f)
                                 for f in Path.cwd().iterdir()
                                 )
    time_last, file_last = max((f.stat().st_mtime, f)
                                for f in Path.cwd().iterdir()
                                )
    logger.info("Older file is {}".format(file_older.name))
    logger.info("Most recent file is {}".format(file_last.name))
    elapsed_time = int(time_last - time_older)
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    running_time = "{:02}:{:02}:{:02}".format(int(hours),
                                              int(minutes),
                                              int(seconds))
    return running_time


def write_summary(text):
    """Write job summary.

    And copy summary file to parent directory.
    """
    summary_found = list(Path.cwd().glob("*summary.txt"))
    if summary_found:
        summary = summary_found[0]
        with open(summary, "a") as summary_file:
            summary_file.write("{}\n".format(text))
        shutil.copyfile(summary, summary.parent.parent / summary.name)
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

    # check AutoClass C worked without error
    if not Path(Path.cwd(), FILE_FOR_SUCCESS).exists():
        write_summary("status: failed")
        write_summary("running-time: {}".format(get_running_time()))
        logger.critical("Cannot find file {} in {}".format(FILE_FOR_SUCCESS, str(Path.cwd())))
        sys.exit(1)

    # prepare results
    results = wrapper.Output()
    logger.info("autoclasswrapper {}".format(wrapper.__version__))
    results.extract_results()
    results.aggregate_input_data()
    results.write_cdt()
    results.write_cdt(with_proba=True)
    results.write_class_stats()
    results.write_dendrogram()
    log_content = log_capture_string.getvalue()
    # write final status
    if "ERROR" in log_content:
        write_summary("status: failed")
    else:
        write_summary("status: completed")
    #log_capture_string.close()

    # write running time
    write_summary("running-time: {}".format(get_running_time()))

    # wrap files
    wrap_output_files()
