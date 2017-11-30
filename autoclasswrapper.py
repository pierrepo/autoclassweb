import os   
import random
import subprocess
import re
import numpy as np
import pandas as pd 

import utilities

class Log():
    """
    Class to handle message and error message
    """
    def __init__(self):
        self.error = False
        self.msg = ""


    def add(self, message, status="OK"):
        """
        Add message
        """
        header = ""
        if status == "error":
            header = "ERROR: "
            self.error = True
        for line in message.split('\n'):
            if line.strip() != "":
                self.msg += "{}{}\n".format(header, line)


    def adderror(self, message):
        """
        Add error message
        """
        self.add(message, status="error")



class Feature():
    """
    Class to handle feature in dataset
    """
    def __init__(self, name="", type="", missing=False):
        """
        Object instanciation
        """
        self.name = name
        self.type=type
        self.missing = missing


    def __repr__(self):
        """
        __repr___
        """
        return "feature {} / type {} / missing values {}".format(
                self.name, self.type, self.missing)


class Process():
    """
    Class to handle autoclass input files and parameters
    """

    def __init__(self, inputfolder='', missing_encoding="?"):
        """
        Object instanciation
        """
        self.log = Log()

        self.inputfolder = inputfolder
        self.missing_encoding = missing_encoding
        self.input_data_lst = []


    def handle_error(f):
        def try_function(self, *args, **kwargs):
            if not self.log.error:
                try:
                    return f(self, *args, **kwargs)
                except Exception as e:
                    self.log.adderror(str(e))
        return try_function


    @handle_error
    def change_working_dir(self):
        """
        change working dir
        """
        self.log.add("Changing working directory")
        os.chdir(self.inputfolder)



    @handle_error
    def add_input_data(self, input_file, input_type, input_error):
        """
        Add input data for clustering
        """
        input_data = Data(input_file, input_type, input_error)
        self.input_data_lst.append(input_data)


    @handle_error
    def create_db2_file(self):
        """
        create .db2 file
        """
        self.log.add("Writing .db2 file")
        self.log.add("If any, missing values will be encoded as: {}".format(self.missing_encoding))
        self.df.to_csv("clust.db2", header=False, sep="\t", na_rep=self.missing_encoding)
        self.log.add("Writing .tsv file [for later use]")
        self.df.to_csv("clust.tsv", header=True, sep="\t", na_rep="")
    

    @handle_error
    def create_hd2_file(self):
        """
        create .hd2 file
        """
        self.log.add("Writing .hd2 file")
        error_type = "rel_error"
        error_value = self.error
        with open("clust.hd2", "w") as hd2:
            hd2.write("num_db2_format_defs {}\n".format(2))
            hd2.write("\n")
            # get number of columns + index
            hd2.write("number_of_attributes {}\n".format(self.ncols+1))
            hd2.write("separator_char '{}'\n".format("\t"))
            hd2.write("\n")
            # write first columns (protein/gene names)
            hd2.write('0 dummy nil "{}"\n'.format(self.df.index.name))
            for col_id in range(self.ncols):
                hd2.write('{} real scalar "{}" zero_point {} {} {}\n'
                          .format(col_id+1, self.df.columns[col_id], self.df.min()[col_id], error_type, error_value))


    @handle_error
    def create_model_file(self):
        """
        Create .model file
        """
        self.log.add("Writing .model file")
        real_values_normals = ""
        real_values_missing = ""
        multinomial_values = ""
        for index, column in enumerate(self.columns):
            print(column)
            if column.type in ['scalar', 'linear']:
                if not column.missing:
                    real_values_normals += '{} '.format(index+1)
                else:
                    real_values_missing += '{} '.format(index+1)
            if column.type == 'discrete':
                multinomial_values += '{} '.format(index+1)
        # count number of different models
        model_count = 1
        for model in [real_values_normals, real_values_missing, multinomial_values]:
            if model:
                model_count += 1
        # write model file
        with open("clust.model", "w") as model:
            model.write("model_index 0 {}\n".format(model_count))
            model.write("ignore 0\n")
            if real_values_normals:
                model.write("single_normal_cn {}\n".format(real_values_normals))
            if real_values_missing:
                model.write("single_normal_cm {}\n".format(real_values_missing))
            if multinomial_values:
                model.write("single_multinomial {}\n".format(multinomial_values))


    @handle_error
    def create_sparams_file(self):
        """
        create  .s-params file
        """
        self.log.add("Writing .s-params file")
        with open("clust.s-params", "w") as sparams:
            sparams.write('screen_output_p = false \n')
            sparams.write('break_on_warnings_p = false \n')
            sparams.write('force_new_search_p = true \n')

            # max_duration
            # When > 0, specifies the maximum number of seconds to run.
            # When = 0, allows run to continue until otherwise halted.
            # doc in search-c.text, lines 493-495
            # default value: max_duration = 0
            # max_duration set to 3600 sec. (1 hour)
            sparams.write('max_duration = 3600 \n')
            
            # max_n_tries
            # max number of trials
            # doc in search-c.text, lines 403-404
            # default value: max_n_tries = 200
            sparams.write('max_n_tries = 1000 \n')
            
            # max_cycles
            # max number of cycles per trial
            # doc in search-c.text, lines 316-317
            # default value: max_cyles = 200
            sparams.write('max_cycles = 1000 \n')
            
            # start_j_list
            # initial guess of the number of clusters
            # doc in search-c.text, line 332
            # default values: 2, 3, 5, 7, 10, 15, 25
            sparams.write('start_j_list = 2, 3, 5, 7, 10, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105 \n')


    @handle_error
    def create_rparams_file(self):
        """
        create .r-params file

        try those parameters:
        report_mode = "data"
        comment_data_headers_p = true
        """
        self.log.add("Writing .r-params file")
        with open("clust.r-params", "w") as rparams:
            rparams.write('xref_class_report_att_list = 0, 1, 2 \n')


    @handle_error
    def create_run_file(self):
        """
        Create .sh file
        """
        self.log.add("Writing run file")
        with open('run_autoclass.sh', 'w') as runfile:
            runfile.write("../autoclass -search clust.db2 clust.hd2 clust.model clust.s-params \n")
            runfile.write("../autoclass -reports clust.results-bin clust.search clust.r-params \n")


    @handle_error
    def prepare_input_files(self):
        """
        Prepare input and parameters files
        """
        self.log.add("Preparing data and parameters files")
        self.change_working_dir()
        self.read_datafile()
        self.check_data_type()
        self.check_missing_values()
        self.clean_column_names()
        self.create_db2_file()
        self.create_hd2_file()
        self.create_model_file()
        self.create_sparams_file()
        self.create_rparams_file()
        self.create_run_file()


    @handle_error
    def run(self):
        """
        Run autoclass
        """
        self.log.add("Running clustering...")
        proc = subprocess.Popen(['bash', 'run_autoclass.sh', self.inputfolder])
        print(" ".join(proc.args))
        return True


    @handle_error
    def set_password(self, password_length):
        """
        Output access token for user

        Token is 8 characters long and always start with the 'T' letter
        """
        print("{} / writing access file".format(self.inputfolder))
        token = utilities.create_random_string(password_length-1)
        token = 'P' + token
        with open('access', 'w') as accessfile:
            accessfile.write(token)
        return token


    @handle_error
    def print_files(self):
        """
        Print generated files
        """
        content = ""
        for name in ('clust.hd2', 'clust.model', 'clust.s-params', 'clust.r-params', 'run_autoclass.sh'):
            if os.path.exists(name):
                content += "\n"
                content += "--------------------------------------------------------------------------\n"
                content += "{}\n".format(name)
                content += "--------------------------------------------------------------------------\n"
                with open(name, 'r') as param_file:
                    content += "".join( param_file.readlines() )
        return content


        @handle_error
        def format_results(self):
            """
            Format results for end user
            """
            case_name = 'clust.case-data-1'
            case_id = []
            case_class = []
            case_prob = []
            with open(case_name, 'r') as case_file:
                for line in case_file:
                    if not line:
                        continue
                    if line.startswith('#') or line.startswith('DATA'):
                        continue
                    items = line.split()
                    case_id.append( items[0] )
                    case_class.append( items[1] )
                    case_prob.append( items[2] )
            self.df = pd.read_table(self.inputfile, sep='\t', header=0, index_col=0)
            self.nrows, self.ncols = self.df.shape
            if (self.nrows != len(case_class)) or (self.nrows != len(case_prob)):
                raise('Number of rows != number of cases!')
            self.df['cluster_class'] = case_class
            self.df['cluster_prob'] = case_prob
            self.df.sort(['cluster_class'], ascending=[True], inplace=True)


class Data():
    """
    Class to handle autoclass data files
    """

    def __init__(self, filename='', type='', error=0.0):
        """
        Object instantiation
        """
        self.log = Log()

        self.type = type
        self.filename = filename
        self.error = error
        self.df = None
        self.columns = []
    

    @handle_error
    def read_datafile(self):
        """
        Read datafile as pandas dataframe
        """
        self.log.add("Reading {}".format(self.inputfile))
        # header is on first row (header=0)
        # gene/protein/orf names are on first column (index_col=0)
        self.df = pd.read_table(self.inputfile, sep='\t', header=0, index_col=0)
        self.nrows, self.ncols = self.df.shape
        for name in self.df.columns.tolist():
            col = Feature(name=name, type=self.datatype)
            self.columns.append(col)
        msg =  "    Found {} rows and {} columns\n".format(self.nrows, self.ncols+1)
        msg += "    Columns are: "
        msg += "'{}' ".format(self.df.index.name)
        for col in self.columns:
            msg += "'{}' ".format(col.name)
        self.log.add(msg)


    @handle_error
    def check_data_type(self):
        """
        check data type
        """
        self.log.add("Checking data format")
        if self.datatype in ['scalar', 'linear']:
            for col in self.df.columns:
                try:
                    self.df[col].astype('float64')
                except:
                    print("{} is {}".format(col, self.df[col].dtype))
                    msg = "Cannot cast column '{}' to float".format(col)
                    print(msg)
                    self.log.adderror(msg)
                    self.log.adderror("Check your input file format!")


    @handle_error
    def check_missing_values(self):
        """
        check missing values
        """
        self.log.add('Checking missing values')
        are_missing_lst = self.df.isnull().any().tolist()
        missing_str = ''
        for index, missing in enumerate(are_missing_lst):
            if missing:
                self.columns[index].missing = True
                missing_str += "'{}' ".format(self.columns[index].name)
        if missing_str:
            self.log.add('    Missing values found in columns: {}'
                         .format(missing_str))
        else:
            self.log.add('    No missing values found.')


    @handle_error
    def clean_column_names(self):
        """
        Cleanup column names
        """
        regex = re.compile('[^A-Za-z0-9 .-]+')
        self.log.add("Checking column names")
        for col_name in self.df.columns:
            col_name_new = regex.sub("_", col_name)
            if col_name_new != col_name:
                self.df.rename(columns={col_name: col_name_new}, inplace=True)
                msg = "Column '{}' renamed to '{}'".format(col_name, col_name_new)
                self.log.add(msg)
                print(msg)


    def load(self):
        """
        Load data
        """
        self.read_datafile():
        self.