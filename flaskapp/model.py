import datetime
import glob
import logging
import os
from pathlib import Path
import random
import re
import shutil


def create_random_string(length):
    """Create random string from a character set.
    
    Parameters
    ----------
    length : int
        Size of the expected string.
        
    Returns
    -------
    str
        Random string.

    Notes
    -----
    String is created from unambiguous letters.
    
    """
    return ''.join(random.choice("ACDEFGHJKMNPQRTWXYZ")
                     for _ in range(length)
                    )


logger = logging.getLogger("flaskapp")


class Job():
    """Autoclass job management.
    """
    def __init__(self):
        """
        Constructor.
        """
        self.path = None
        self.folder = None
        self.name = None
        self.ctime = None
        self.status = ""
        self.running_time = "00:00:00"
        self.results_file = ""

    def create_from_path(self, path):
        """Create Job from path."""
        self.path = path
        answer = self.verify_folder_name(self.path)
        if answer:
            self.folder, self.name, self.ctime = answer
        else:
            raise(f"{self.path} is not a valid job path")
        # get running status
        self.get_status()
        # get results file if any
        self.get_results_file()

    def create_new(self, root, name_length):
        """Create new job in root directory."""
        self.name = create_random_string(name_length)
        self.ctime = datetime.datetime.now()
        date_time = datetime.datetime.strftime(self.ctime, "%Y%m%d_%H%M%S")
        self.folder =  f"{date_time}_{self.name}"
        self.path = os.path.join(root, self.folder)
        try:
            os.makedirs(self.path)
            print(f"Created folder {self.folder}")
        except OSError:
            print(f"Directory {self.folder} already exists")
        except:
            print(f"Cannot create folder: {self.folder}")
            raise

    def get_status(self):
        """Test job status and how long it has run (or is running).

        We consider that the time to build classification (i.e clustering)
        is much larger than the time to build reports.
        """
        # find status
        # search in summary file first
        self.status = "running"
        status = self.search_summary("status")
        if status:
            self.status = status.split()[1]
        # define running time
        # search in summary file first
        self.running_time = "00:00:00"
        running_time = self.search_summary("running-time")
        if running_time:
            self.running_time = running_time.split()[1]
        # calculate running time
        else:
            now = datetime.datetime.now()
            elapsed_time = (now - self.ctime).seconds
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.running_time = (
                f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            )

    def get_results_file(self):
        """Find results file."""
        self.results_file = ""
        zip_lst = glob.glob(os.path.join(self.path,"*autoclass*.zip"))
        if len(zip_lst) >= 1:
            self.results_file = zip_lst[0]

    def write_summary(self, text):
        """Write summary of job in file.

        And copy summary file to parent directory.
        """
        summary = Path(self.path, self.folder + "_summary.txt")
        with open(summary, "a") as summary_file:
            summary_file.write(f"{text}\n")
        shutil.copyfile(summary, summary.parent.parent / summary.name)

    def search_summary(self, target, name="*summary.txt"):
        """Read summary of job."""
        summary_found = glob.glob(os.path.join(self.path, name))
        if summary_found:
            summary_name = summary_found[0]
            if os.path.exists(summary_name):
                with open(summary_name, "r") as summary_file:
                    for line in summary_file:
                        if target in line:
                            return line[:-1]
        return None

    def get_file_modification_time(self, filename):
        """Get time when file was last modified."""
        mtime = None
        if os.path.exists(filename):
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
        return mtime

    def destroy(self):
        """Destroy itself by removing directory."""
        if Path(self.path).exists():
            logger.info(f"Trying to destroy old job {self.name}")
            try:
                shutil.rmtree(self.path)
            except PermissionError:
                logger.error(f"Cannot destroy job {self.name}!")
                logger.error("Permission error.")
            except:
                logger.error(f"Cannot destroy job {self.name}!")
                logger.error("Unknown error.")
            else:
                logger.info(f"Destroyed job {self.name}")
    
    def __repr__(self):
        """Job representation."""
        return (f"{self.name} in {self.folder} "
                f"created: {self.ctime}  status: {self.status}")

    @staticmethod
    def verify_folder_name(folder):
        """Verify folder name is compliant with naming convention."""
        regex = re.compile("\/([0-9]{8})_([0-9]{6})_(\w+)$")
        find = regex.search(folder)
        if find:
            date = f"{find.group(1)}_{find.group(2)}"
            name = find.group(3)
            folder = f"{date}_{name}"
            try:
                ctime = datetime.datetime.strptime(date, "%Y%m%d_%H%M%S")
                return (folder, name, ctime)
            except:
                return False


class JobManager():
    """Manager for autoclass jobs."""

    def __init__(self, path, job_duration=30):
        """Constructor."""
        self.path = path
        self.job_duration = job_duration
        self.running = []
        self.stopped = []

    def autodiscover(self):
        """Discover autoclass jobs automatically."""
        # list sub folders
        p = Path(self.path)
        job_folder_lst = [str(x) for x in p.iterdir() if x.is_dir()]
        # create jobs
        jobs = {}
        for job_folder in job_folder_lst:
            if Job.verify_folder_name(job_folder):
                job = Job()
                job.create_from_path(job_folder)
                now = datetime.datetime.now()
                age = now - job.ctime
                if age.days > self.job_duration:
                    job.destroy()
                else:
                    jobs[job.ctime.strftime("%Y-%m-%d %H:%M:%S")] = job
        # store jobs against creation time and status
        for creation_time in sorted(jobs, reverse=True):
            job = jobs[creation_time]
            if job.status == 'running':
                self.running.append(job)
            else:
                self.stopped.append(job)


if __name__ == '__main__':
    job_manager = JobManager("results")
    job_manager.autodiscover()
    for job in job_manager.jobs:
        print(job)
