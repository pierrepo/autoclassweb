import os
import datetime
import re
import glob
import logging
from pathlib import Path
import glob

import utilities


class Job():
    """
    Autoclass job management
    """
    def __init__(self, alive=30):
        """
        Constructor
        """
        self.path = None
        self.folder = None
        self.name = None
        self.ctime = None
        self.status = ""
        self.running_time = 0
        self.alive = alive
        self.results_file = ""

    def create_from_path(self, path):
        """Create Job from path
        """
        self.path = path
        answer = self.verify_folder_name(self.path)
        if answer:
            self.folder, self.name, self.ctime = answer
        else:
            raise("{} is not a valid Job path".format(self.path))
        # get running status
        self.get_status()
        # get results file if any
        self.get_results_file()


    def create_from_name(self, root, name):
        """
        Create Job from root directory and job name
        """
        # clean name
        name_clean = ""
        for character in name:
            if character in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMONPQRSTUVWXYZ_-":
                name_clean += character
            else:
                name_clean += "-"
        self.name = name_clean

        self.ctime = datetime.datetime.now()
        date = datetime.datetime.strftime(self.ctime, "%Y%m%d")
        time = datetime.datetime.strftime(self.ctime, "%H%M%S")

        self.folder =  "{}.{}.{}".format(date, time, self.name)
        self.path = os.path.join(root, self.folder)
        try:
            os.makedirs(self.path)
            print("Created folder {}".format(self.folder))
        except OSError:
            print("Directory {} already exists".format(self.folder))
        except:
            print("Cannot create folder: {}".format(self.folder))
            raise





    def create_new(self, root, name_length):
        """
        Create new job in root directory
        """
        # create random name from unambiguous characters
        self.name = utilities.create_random_string(name_length-1)
        self.name = "N" + self.name

        self.ctime = datetime.datetime.now()
        date = datetime.datetime.strftime(self.ctime, "%Y%m%d")
        time = datetime.datetime.strftime(self.ctime, "%H%M%S")

        self.folder =  "{}.{}.{}".format(date, time, self.name)
        self.path = os.path.join(root, self.folder)
        try:
            os.makedirs(self.path)
            print("Created folder {}".format(self.folder))
        except OSError:
            print("Directory {} already exists".format(self.folder))
        except:
            print("Cannot create folder: {}".format(self.folder))
            raise


    def get_status(self):
        """
        Test job status and how long it has run (or is running)

        We considere that the time to make search clusters is much smaller
        than the time to build reports.
        """
        # default values
        self.running_time = 0
        self.status = "failed"
        # first try to find log file for autoclass search (.log)
        file_lst = glob.glob(os.path.join(self.path, "clust.log"))
        if file_lst:
            log_file = file_lst[0]
            # modified time
            mtimestamp = os.path.getmtime(log_file)
            mtime = datetime.datetime.fromtimestamp(mtimestamp)
            # running status
            if ((datetime.datetime.now() - mtime).seconds < self.alive ):
                self.status = "running"
            else:
                self.status = "failed"
            # running time
            self.running_time = (mtime - self.ctime).seconds / 60
        # then try to find log file for autoclass report (.rlog)
        file_lst = glob.glob(os.path.join(self.path, "job-completed"))
        if file_lst:
            self.status = "completed"
            start = datetime.datetime.fromtimestamp(
                      os.path.getmtime(os.path.join(self.path, "clust.model"))
                     )
            end = datetime.datetime.fromtimestamp(
                       os.path.getmtime(os.path.join(file_lst[0]))
                    )
            self.running_time = (end - start).seconds / 60


    def get_results_file(self):
        """
        Find results file
        """
        self.results_file = ""
        zip_lst = glob.glob(os.path.join(self.path,"*autoclass*.zip"))
        if len(zip_lst) >= 1:
            self.results_file = zip_lst[0]


    def __repr__(self):
        """
        __repr___
        """
        return "{} in {} created: {}  status: {}".format(
                self.name, self.folder, self.ctime,  self.status)





    @staticmethod
    def verify_folder_name(folder):
        """
        Verify folder name is compliant with naming convention
        """
        regex = re.compile("^(\w+)/([0-9]{8})\.([0-9]{6})\.(\w+)$")
        find = regex.search(folder)
        if find:
            root = find.group(1)
            date = "{}.{}".format( find.group(2), find.group(3) )
            name = find.group(4)
            folder = "{}.{}".format( date, name )
            try:
                ctime = datetime.datetime.strptime(date, "%Y%m%d.%H%M%S")
                return (folder, name, ctime)
            except:
                return False


class JobManager():
    """
    Manager for autoclass jobs
    """

    def __init__(self, path, max_jobs, alive=30):
        """
        Constructor
        """
        self.path = path
        self.max = max_jobs
        self.running = []
        self.stopped = []
        self.alive = alive


    def autodiscover(self):
        """
        Discover autoclass jobs automatically
        """
        # list sub folders
        #print(os.walk(self.path))

        #job_folder_lst = next(os.walk(self.path))[1]
        p = Path(self.path)
        job_folder_lst = [str(x) for x in p.iterdir() if x.is_dir()]

        # create jobs
        jobs = {}
        for job_folder in job_folder_lst:
            if Job.verify_folder_name(job_folder):
                job = Job(alive=self.alive)
                job.create_from_path(job_folder)
                jobs[job.ctime.strftime("%Y-%m-%d %H:%M:%S")] = job
        # store jobs against creation time and status
        for creation_time in sorted(jobs, reverse=True):
            job = jobs[creation_time]
            if job.status == 'running':
                self.running.append(job)
            else:
                self.stopped.append(job)


if __name__ == '__main__':

    job_manager = JobManager("tmp", 4)
    job_manager.autodiscover()
    for job in job_manager.jobs:
        print(job)
