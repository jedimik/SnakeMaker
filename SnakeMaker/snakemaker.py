import argparse
import sys

import bids
import pandas as pd

import SnakeMaker.defaults as df
import SnakeMaker.subject as sb
import SnakeMaker.utils as ut
from SnakeMaker.rule_maker import rulemaker as rm
from SnakeMaker.smkfile_maker import smkfile_maker as sm


class Snakemaker:
    def __init__(
        self,
        input_data_files: str | list | dict = None,
        rule_configuration: dict = None,
        snakefile_configuration: dict = None,
        load_bids_structure: bool = False,
        full_run: bool = False,
        config: dict = None,
        debug: bool = False,
    ) -> None:
        # Parameters
        self.input_data_files = None
        self.bids_structure = None
        self.subjects = dict()
        self.samples = []
        self.rules = dict()
        self.config = dict()
        self.rule_configuration = None
        self.full_run = False
        self.rule0 = None
        self.env_vars = dict()
        # Assign parameters
        self.input_data_files = input_data_files
        self.rule_configuration = rule_configuration
        self.snakefile_configuration = snakefile_configuration
        self.config = config or df.settings
        self.full_run = full_run
        # Call initialize functions
        if not debug:
            self.initialize_config()
            self.assign_env_variables()
            self.samples = self.create_samples(self.input_data_files)
            self.rules = self.create_rules(shortened=True)
            self.snakemake_main_file = self.create_snakemake_main_file()
            if self.rule0:
                self.execute_rule0()
            self.create_shells()

    def create_samples(self, input_data_files: str | dict | list = None, level: str | int = None) -> list:
        """
        Creates a list of samples from the given input data files.

        Parameters:
        -----------
        input_data_files : str | dict | list, optional
            The input data files which can be a string (file path), a dictionary, or a list.
            If not provided, it defaults to `self.input_data_files`.
        level : str | int, optional
            The level of the path to return. If not provided, it defaults to None.

        Returns:
        --------
        list
            A list of samples extracted from the input data files.

        Raises:
        -------
        NotImplementedError
            If the input_data_files parameter is not in the correct format (str, list, or dict).
        """
        input_data_files = input_data_files or self.input_data_files
        if (
            isinstance(input_data_files, str) and self.load_bids_structure
        ):  # This will have exact rule! check it! # THIS IS PREPARATION FOR FUTURE IMG DATA
            self.bids_structure = self.load_bids_structure(input_data_files)
            return self.create_subjects()
        elif isinstance(input_data_files, str) and ut.file_exists(input_data_files):  # CSV input samples format
            if input_data_files.endswith(".csv"):
                return (
                    pd.read_csv(input_data_files)["samples"].to_list()
                    if not level
                    else ut.get_last_directory(pd.read_csv(input_data_files)["samples"].to_list(), level)
                )
            elif input_data_files.endswith(".txt"):  # TXT input samples format
                with open(input_data_files, "r") as f:
                    return f.readlines() if not level else ut.get_last_directory(f.readlines(), level)
        elif isinstance(input_data_files, dict):  # Given dictionary
            return input_data_files.get("samples", []) if not level else ut.get_last_directory(input_data_files.get("samples", []), level)
        elif isinstance(input_data_files, list):
            return input_data_files if not level else ut.get_last_directory(input_data_files, level)
        else:
            raise NotImplementedError(
                "The input_data_files parameter is not in the correct format. You can use only str, list or dict."
                + "for file types: csv, txt, json, yaml, for dict: {'samples': ['sample1', 'sample2']}"
            )

    def initialize_config(self) -> None:
        """
        Initializes the configuration for the Snakemaker instance.

        This method loads the rule configuration and snakefile configuration
        from the specified configuration files. If the configurations are
        already loaded, it uses the existing configurations.

        Returns:
            None
        """
        config = self.config
        self.rule_configuration = ut.load_config(
            config.get("configuration_files", {}).get("rule_configuration", None) if self.rule_configuration is None else self.rule_configuration
        )
        self.snakefile_configuration = ut.load_config(
            config.get("configuration_files", {}).get("snakefile_configuration", None)
            if self.snakefile_configuration is None
            else self.snakefile_configuration
        )

    def assign_env_variables(self) -> None:
        """
        Assigns environment variables based on the configuration provided.

        This method reads the application configuration and sets the environment
        variables accordingly. It handles different scenarios such as default paths,
        full paths, and paths driven by output directories.

        - If the `APPLICATION_ROOT_PATH` is set to "default", it uses the default root path.
        - If a valid full path is provided for `APPLICATION_ROOT_PATH`, it uses that path.
        - If the `APPLICATION_ROOT_PATH` is set to "by_output" and a valid output directory path is provided,
          it sets the `OUTPUT_DIR_PATH` accordingly.
        - For each key in the configuration, it sets the environment variable based on the value provided.
          It handles both relative and full paths.

        Raises:
            ValueError: If an invalid path is provided in the configuration for `APPLICATION_ROOT_PATH`.

        """

        config = self.config.get("app", None)  # Shortened
        path_key = "APPLICATION_ROOT_PATH"  # Shortened
        output_dir_key = "OUTPUT_DIR_PATH"
        custom_functions_key = "CUSTOM_FUNCTIONS_PATH_LIST"
        if config.get(path_key, "") == "default":  # If default, use default path
            self.env_vars.update(ut.set_env_variable(path_key, ut.get_env_variable("ROOT_PATH_FOR_DYNACONF"), True))
        elif (
            ut.directory_exists(config.get(path_key), True) and config.get(path_key, "") != "" and config.get(path_key, "").startswith("/")
        ):  # If full path exists, use it
            self.env_vars.update(ut.set_env_variable(path_key, config.get(path_key), True))  # If different path provided, use it
        else:
            msg = f"Invalid path provided in the configuration for {path_key}."
            ut.get_logger("error_logger").error(msg)
        if config.get(path_key, "") == "by_output" and ut.directory_exists(
            config.get(output_dir_key, ""), True
        ):  # if its driven by output set OUTPUT_DIR_PATH
            self.env_vars.update(ut.set_env_variable(output_dir_key, ut.directory_exists(config.get("OUTPUT_DIR_PATH"), True), True))
        for key, value in config.items():  # For each key in the configuration
            # Handle relative and full paths
            if isinstance(value, str) and value.startswith("/"):
                self.env_vars.update(ut.set_env_variable(key, value, True))
            elif key in df.output_env_variables and not value.startswith("/"):
                self.env_vars.update(ut.set_env_variable(key, ut.merge_paths(ut.get_env_variable(path_key), value), True))
            elif key in df.output_env_variables and value.startswith("/"):
                self.env_vars.update(ut.set_env_variable(key, value, True))
            elif key in df.env_variables_excluded and ut.get_env_variable(key):
                continue
            elif key == custom_functions_key and isinstance(value, list):  # If custom functions, set them
                self.env_vars.update(ut.set_env_variable(key, ut.merge_paths(ut.get_env_variable(path_key), value), True, as_list=True))
            else:
                self.env_vars.update(ut.set_env_variable(key, ut.merge_paths(ut.get_env_variable(path_key), value), True)) if value else None
        # Also set Input dir path as the main path for input samples
        if ut.get_env_variable("INPUT_DIR_PATH"):
            self.input_data_files = ut.get_env_variable("INPUT_DIR_PATH")

    def add_subject(self, subject_id: str, subject_data: pd.DataFrame) -> None:
        """
        Create and add a subject to the snakemaker.

        Args:
            subject_id (str): The ID of the subject.
            subject_data (pd.DataFrame): The data associated with the subject.

        Returns:
            None
        """
        self.subjects[subject_id] = sb.Subject(subject_id, subject_data)

    def load_bids_structure(self, input_data_files: str) -> bids.BIDSLayout:
        """
        Load the BIDS structure from the given data input path.

        Args:
            input_data_files (str): The path to the BIDS dataset.

        Returns:
            bids.BIDSLayout: The loaded BIDSLayout object.

        Raises:
            Exception: If there is an error while loading the BIDS structure.
        """
        try:
            return bids.BIDSLayout(input_data_files)
        except Exception as e:
            msg = f"Error while loading BIDS structure: {e}"
            ut.get_logger("error_logger").error(msg)
            raise Exception(msg)

    def get_bids_df(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame representation of the BIDS structure.

        Returns:
            pd.DataFrame: The BIDS structure as a DataFrame.
        """
        return self.bids_structure.to_df()

    def get_subject(self, subject_id: str) -> dict:
        """
        Retrieve a subject from the subjects dictionary based on the given subject_id.

        Args:
            subject_id (str): The ID of the subject to retrieve.

        Returns:
            dict: The subject information as a dictionary.

        Raises:
            KeyError: If the subject_id is not found in the subjects dictionary.
        """
        return self.subjects[subject_id]

    def get_all_subjects_str(self) -> list:
        output = []
        for subject in self.subjects.keys():
            if len(self.subjects[subject].sessions.keys()) > 0:
                for session in self.subjects[subject].sessions.keys():
                    if self.load_bids_structure:
                        output.append(f"sub-{subject}/ses-{session}")
                    else:
                        output.append(f"{subject}_{session}")
            else:
                output.append(subject)
        return output

    def create_subjects(self) -> None:
        """
        Get the subjects from the BIDS structure.

        Returns:
            dict: A dictionary containing the subjects.
        """
        if self.load_bids_structure:
            bids_df = self.get_bids_df()
            subject_ids = bids_df["subject"].dropna().unique()
        else:
            subject_ids = self.samples
        for subject_id in subject_ids:  # For each unique subject
            # Create subjects
            self.add_subject(subject_id, bids_df[(bids_df["subject"] == subject_id)])
        return self.get_all_subjects_str()

    def execute_rule0(self):
        """
        Executes a series of rules defined in `self.rule0`.

        This method iterates over the rules in `self.rule0` and attempts to import
        and execute functions specified in those rules. If a rule contains a "path"
        key, it imports the module from that path and executes the function specified
        by "function_name" within that module. If no "path" is provided, it falls back
        to importing modules from the paths specified in the environment variable
        "CUSTOM_FUNCTIONS_PATH_LIST".

        Yields:
            The result of the executed function for each rule.

        Raises:
            AttributeError: If the specified function does not exist in the module.
            ImportError: If the module cannot be imported.
        """
        check = False
        for i, rule_ in enumerate(self.rule0):
            rule = rule_.get(list(rule_.keys())[0])
            if rule.get("path", None):
                module = ut.import_scripts(rule.get("path"), rule.get("function_name"))
                if hasattr(module, rule.get("function_name")):
                    function = getattr(module, rule.get("function_name"))
                    return function(self, rule.get("path"))
                else:
                    msg = f"Function {rule.get('function_name')} does not exist in the module {rule.get('path')}"
                    ut.get_logger("error_logger").error(msg)
                    print(f"{msg}. Check the function name in the module.")
            else:
                check = True
        if check:
            for script in ut.get_env_variable("CUSTOM_FUNCTIONS_PATH_LIST", as_list=True):
                module = ut.import_scripts(script, rule.get("function_name"))
                if hasattr(module, rule.get("function_name")):
                    function = getattr(module, rule.get("function_name"))
                    return function(self)
                else:
                    msg = f"Function {rule.get('function_name')} does not exist in the module {script}"
                    ut.get_logger("error_logger").error(msg)
                    print(f"{msg}. Check the function name in the module.")

    def create_shells(self):
        """
        Create the shell scripts for the rules.

        This method iterates over the rules and creates the shell scripts
        based on the shell commands provided in the rules.

        Returns:
            None
        """
        ut.create_shell_script(ut.merge_paths(ut.get_env_variable("OUTPUT_SNAKEMAKE_PATH"), "dry_run.sh"), df.dry_run_command)
        ut.create_shell_script(ut.merge_paths(ut.get_env_variable("OUTPUT_SNAKEMAKE_PATH"), "run.sh"), df.hot_run_command)

    def create_rules(self, shortened: bool = False) -> dict:
        """
        Create rules based on the given rule configuration.

        Returns:
            dict: A dictionary containing the created rules.
        """
        # NOTE: in future add try except for the rule configuration
        rm_instance = rm.Rulemaker(self.rule_configuration, shortened=shortened)
        self.rule0 = rm_instance.get_rule_0()
        return rm.Rulemaker(self.rule_configuration, shortened=shortened).get_rules()

    def create_snakemake_main_file(self) -> str:
        """
        Create the main Snakemake file.

        Returns:
            str: The path to the created Snakemake file.
        """
        # NOTE: in future add try except for the rule configuration
        return sm.SmkFileMaker(self.snakefile_configuration, samples=self.samples).get_smkfile()


if __name__ == "__main__":
    Snakemaker(load_bids_structure=True, debug=False)
