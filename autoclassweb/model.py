import os
import datetime
import re


class Job():
    """
    Autoclass job management
    """
    def __init__(self, root, folder=None, name=None):
        """
        Constructor
        """
        self.root = root
        self.folder = folder
        self.name = name
        self.ctime = None
        self.mtime = None
        self.rtime = None 

        # you need either path or name
        if self.folder == None and self.name == None:
            print("Either path or name must be specified for Job instance.")
            raise

        # create folder from name

        # clean name
        if self.name:
            name_clean = ""
            for character in name:
                if character in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMONPQRSTUVWXYZ_-":
                    name_clean += character
                else:
                    name_clean += "-"
            self.name = name_clean

            self.ctime = datetime.datetime.now()
            now_string = datetime.datetime.strftime(self.ctime, "%Y%m%d.%H%M%S")

            self.folder = "{}.{}".format(now_string, self.name)
            try:
                os.makedirs(os.path.join(self.root, self.folder))
                print("Created folder {}".format(self.folder))
            except OSError:
                print("Directory {} already exists".format(self.folder))
            except:
                print("Cannot create folder: {}".format(self.folder))
                raise 

        # create name and ctime from folder
        if self.folder:
            self.name, self.ctime = self.verify_folder_name(self.folder)

        # modified time
        mtime = os.path.getmtime(os.path.join(self.root, self.folder))
        self.mtime = datetime.datetime.fromtimestamp(mtime)

        # running status
        self.is_running = True if ((datetime.datetime.now() - self.mtime).seconds < 30 ) else False
        # running time
        self.rtime = (self.mtime - self.ctime).seconds / 60

    def __repr__(self):
        """
        __repr___
        """
        return "{}/{}  created: {} modified: {} is_running: {}".format(
                self.root, self.folder, self.ctime, self.mtime, self.is_running)


    @staticmethod
    def verify_folder_name(folder):
        """
        Verify folder name is compliant with naming convention
        """
        separator = "."
        fields = folder.split(separator)
        try:
            date_mask = "%Y%m%d{}%H%M%S".format(separator)
            ctime = datetime.datetime.strptime(separator.join(fields[0:2]), date_mask)
            job_name = fields[2]
            return [job_name, ctime]
        except:
            return False




class JobManager():
    """
    Manager for autoclass jobs
    """
    def __init__(self, path, max_jobs):
        """
        Constructor
        """
        self.path = path
        self.max_jobs = max_jobs
        self.jobs = []
        self.alive_threshold = []

    def autodiscover(self):
        """
        Discover autoclass jobs automatically
        """
        # list sub folders
        print(os.walk(self.path))
        job_folder_lst = next(os.walk(self.path))[1]
        
        # create jobs
        for job_folder in job_folder_lst:
            if Job.verify_folder_name(job_folder):
                job = Job(self.path, folder=job_folder)
                self.jobs.append(job)



if __name__ == '__main__':


    job_manager = JobManager("tmp", 4)
    job_manager.autodiscover()
    for job in job_manager.jobs:
        print(job)
