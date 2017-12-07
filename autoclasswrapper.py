import os   
import random
import subprocess
import re
import logging
import numpy as np
import pandas as pd 

import utilities

logging.basicConfig(level=logging.DEBUG)


class CastFloat64(Exception):
    """
    Exception raised when data column cannot be casted to float64
    """

    def __init__(self, message):
        self.message = message


class Process():
    """
    Class to handle autoclass input files and parameters
    """

    def __init__(self, inputfolder='', missing_encoding="?", tolerate_error=False):
        """
        Object instanciation
        """
        self.inputfolder = inputfolder
        self.missing_encoding = missing_encoding
        self.tolerate_error = tolerate_error

        self.datasets = []
        self.df = None
        self.had_error = False


    def handle_error(f):
        """
        Handle error during data parsing and formating
        """
        def try_function(self, *args, **kwargs):
            if self.tolerate_error or not self.had_error:
                try:
                    return f(self, *args, **kwargs)
                except Exception as e:
                    for line in str(e).split('\n'):
                        logging.error(line)
                    self.had_error = True
        return try_function


    @handle_error
    def change_working_dir(self):
        """
        change working dir
        """
        logging.info("Changing working directory")
        os.chdir(self.inputfolder)


    @handle_error
    def add_input_data(self, input_file, input_type, input_error):
        """
        Add input data for clustering
        """
        input_data = Data(input_file, input_type, input_error)
        self.read_datafile(input_data)
        self.clean_column_names(input_data)
        self.check_data_type(input_data)
        self.check_missing_values(input_data)
        self.datasets.append(input_data)


    @handle_error
    def read_datafile(self, dataset):
        """
        Read datafile as pandas dataframe
        """
        logging.info("Reading {}".format(dataset.input_file))
        # header is on first row (header=0)
        # gene/protein/orf names are on first column (index_col=0)
        dataset.df = pd.read_table(dataset.input_file, sep='\t', header=0, index_col=0)
        nrows, ncols = dataset.df.shape
        logging.info("Found {} rows and {} columns"
                     .format(nrows, ncols+1))


    @handle_error
    def clean_column_names(self, dataset):
        """
        Cleanup column names
        """
        regex = re.compile('[^A-Za-z0-9 .-]+')
        logging.debug("Checking column names")
        # check index column name first
        col_name = dataset.df.index.name
        col_name_new = regex.sub("_", col_name)
        if col_name_new != col_name:
            dataset.df.index.name = col_name_new
            logging.warning("Column '{}' renamed to '{}'"
                            .format(col_name, col_name_new))
        # then other column names
        for col_name in dataset.df.columns:
            col_name_new = regex.sub("_", col_name)
            if col_name_new != col_name:
                dataset.df.rename(columns={col_name: col_name_new}, inplace=True)
                logging.warning("Column '{}' renamed to '{}'"
                                .format(col_name, col_name_new))
        # print all columns names
        logging.debug("Index name: ''{}'".format(dataset.df.index.name))
        for name in dataset.df.columns:
            logging.debug("Column name: '{}'".format(name))


    @handle_error
    def check_data_type(self, dataset):
        """
        check data type
        """
        logging.info("Checking data format")
        if dataset.data_type in ['scalar', 'linear']:
            for col in dataset.df.columns:
                self.check_data_numeric(dataset, col)    


    @handle_error
    def check_data_numeric(self, dataset, col):
        """
        Verify that column is realy numeric
        """
        try:
            dataset.df[col].astype('float64')
            logging.info("Column '{}'\n".format(col)
                         +dataset.df[col].describe(percentiles=[]).to_string())
        except:
            msg  = "Cannot cast column '{}' to float\n".format(col)
            msg += "Check your input file!"
            raise CastFloat64(msg)


    @handle_error
    def check_missing_values(self, dataset):
        """
        check missing values
        """
        logging.info('Checking missing values')
        columns_with_missing = dataset.df.columns[ dataset.df.isnull().any() ].tolist()
        dataset.columns_with_missing = columns_with_missing
        if columns_with_missing:
            dataset.columns_with_missing = columns_with_missing
            logging.warning('Missing values found in columns: {}'
                            .format(" ".join(columns_with_missing)))
        else:
            logging.info('No missing values found.')


    @handle_error
    def merge_dataframes(self):
        """
        Merge input datasets
        """
        if len(self.datasets) == 1:
            self.df = self.datasets[0].df
        else:
            logging.info("Merging input data")
            df_lst = []
            for dataset in self.datasets:
                df_lst.append(dataset.df)
            # https://pandas.pydata.org/pandas-docs/stable/merging.html
            self.df = pd.concat(df_lst, axis=1, join="outer")
        nrows, ncols = self.df.shape
        logging.info("Final datafram has {} lines and {} columns".format(nrows, ncols+1))


    @handle_error
    def create_db2_file(self):
        """
        create .db2 file
        """
        logging.info("Writing .db2 file")
        logging.info("If any, missing values will be encoded as: {}".format(self.missing_encoding))
        self.df.to_csv("clust.db2", header=False, sep="\t", na_rep=self.missing_encoding)
        logging.debug("Writing .tsv file [for later use]")
        self.df.to_csv("clust.tsv", header=True, sep="\t", na_rep="")
    

    @handle_error
    def create_hd2_file(self):
        """
        create .hd2 file
        """
        logging.info("Writing .hd2 file")
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
        logging.info("Writing .model file")
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
        logging.info("Writing .s-params file")
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
        logging.info("Writing .r-params file")
        with open("clust.r-params", "w") as rparams:
            rparams.write('xref_class_report_att_list = 0, 1, 2 \n')


    @handle_error
    def create_run_file(self):
        """
        Create .sh file
        """
        logging.info("Writing run file")
        with open('run_autoclass.sh', 'w') as runfile:
            runfile.write("../autoclass -search clust.db2 clust.hd2 clust.model clust.s-params \n")
            runfile.write("../autoclass -reports clust.results-bin clust.search clust.r-params \n")


    @handle_error
    def prepare_input_files(self):
        """
        Prepare input and parameters files
        """
        logging.info("Preparing data and parameters files")
        self.change_working_dir()
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
        logging.info("Running clustering...")
        proc = subprocess.Popen(['bash', 'run_autoclass.sh', self.inputfolder])
        print(" ".join(proc.args))
        return True


    @handle_error
    def set_password(self, password_length):
        """
        Output access token for user

        Token is 8 characters long and always start with the 'T' letter
        """
        logging.info("{} / writing access file".format(self.inputfolder))
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

    def __init__(self, input_file='', data_type='', error=0.0):
        """
        Object instantiation
        """
        assert data_type in ['real_scalar', 'real_location', 'discrete'], \
               ("data_type in {} should be: "
                "'real_scalar', 'real_location' or 'discrete'"
                .format(input_file))
        self.data_type = data_type

        # filename of input_file
        self.input_file = input_file
        self.error = error
        self.df = None
        self.columns = []
        self.columns_with_missing = []
    

    def load(self):
        """
        Load data
        """
        self.read_datafile()
        self.clean_column_names()
        self.check_data_type()
        self.check_missing_values()
