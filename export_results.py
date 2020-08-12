import io
import logging
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
    OUTPUT_FILES_RENAMED = []
    for name in OUTPUT_FILES:
        output_file = Path(name)
        if output_file.exists():
            new_name = name.replace("autoclass", f"{DIR_NAME}_autoclass")
            output_file.rename(new_name)
            OUTPUT_FILES_RENAMED.append(new_name)
        else:
            logger.warning(f"Cannot find {name}")
    # Create archive.
    zipname = f"{DIR_NAME}_autoclass.zip"
    with zipfile.ZipFile(zipname, "w") as outputzip:
        for filename in OUTPUT_FILES_RENAMED:
            if Path(filename).exists():
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
    logger.info(f"Older file is {file_older.name}")
    logger.info(f"Most recent file is {file_last.name}")
    elapsed_time = int(time_last - time_older)
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"


def write_summary(text):
    """Write job summary.

    And copy summary file to parent directory.
    """
    summary_found = list(Path.cwd().glob("*summary.txt"))
    if summary_found:
        summary = summary_found[0]
        with open(summary, "a") as summary_file:
            summary_file.write(f"{text}\n")
        shutil.copyfile(summary, summary.parent.parent / summary.name)
    else:
        logger.error("Cannot find summary file.")


if __name__ == "__main__":
    # Call logger from autoclasswrapper.
    logger = logging.getLogger("autoclasswrapper")
    logger.setLevel(logging.DEBUG)
    # Create a file handler.
    handler = logging.FileHandler("output.log")
    handler.setLevel(logging.INFO)
    # Create a stream handler.
    log_capture_string = io.StringIO()
    handler_stream = logging.StreamHandler(log_capture_string)
    handler_stream.setLevel(logging.INFO)
    # Create logging format.
    formatter = logging.Formatter("%(asctime)s :: %(levelname)-8s :: %(message)s",
                                  datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    handler_stream.setFormatter(formatter)
    # Add handlers to the logger.
    logger.addHandler(handler)
    logger.addHandler(handler_stream)

    # Check AutoClass C worked without error.
    if not Path(Path.cwd(), FILE_FOR_SUCCESS).exists():
        write_summary("status: failed")
        write_summary(f"running-time: {get_running_time()}")
        logger.critical(f"Cannot find file {FILE_FOR_SUCCESS} in {str(Path.cwd())}")
        sys.exit(1)

    # Prepare results.
    results = wrapper.Output()
    logger.info(f"autoclasswrapper {wrapper.__version__}")
    results.extract_results()
    results.aggregate_input_data()
    results.write_cdt()
    results.write_cdt(with_proba=True)
    results.write_class_stats()
    if Path("autoclass_out_stats.tsv").exists():
        results.write_dendrogram()
    else:
        logger.warning("No stats -> no dendrogram.")
    log_content = log_capture_string.getvalue()
    # Write final status.
    if "ERROR" in log_content:
        write_summary("status: failed")
    else:
        write_summary("status: completed")
    #log_capture_string.close()

    # Write running time.
    write_summary(f"running-time: {get_running_time()}")

    # Wrap files.
    wrap_output_files()
