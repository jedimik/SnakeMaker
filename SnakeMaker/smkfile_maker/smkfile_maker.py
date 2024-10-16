import SnakeMaker.defaults as df
import SnakeMaker.rule_maker.rule_utils as ru
import SnakeMaker.smkfile_maker.smkfile_defaults as sdf
import SnakeMaker.utils as ut


class SmkFileMaker:
    def __init__(
        self,
        config: str | dict = None,
        imports: list[str] = sdf.default_imports,
        vars: dict = sdf.default_vars,
        config_vars: dict = sdf.config_vars,
        include: dict = sdf.default_include,
        rules: dict = sdf.default_rules,
        smkfile_path: str = None,
        samples: list = None,
        test: bool = False,
    ):
        # Parameters
        self.imports = imports
        self.vars = vars
        self.config_vars = config_vars
        self.include = include
        self.rules = rules
        self.samples = samples
        self.snakefile_string = None
        # Initialize
        self.config = self.initialize_config(config)
        self.smkfile_path = smkfile_path or ut.get_env_variable("OUTPUT_SNAKEMAKE_PATH")
        # Run
        if not test:
            self.process_config()
            self.make_smkfile(self.snakefile_string)

    def initialize_config(self, config: str | dict = None):
        """
        Initializes the configuration for the application.

        Parameters:
        config (str | dict, optional): The configuration to initialize. It can be:
            - None: If no configuration is provided, the default configuration is loaded.
            - dict: If a dictionary is provided, it is used as the configuration.
            - str: If a string (representing a file path) is provided and the file exists, the configuration is loaded from the file.

        Returns:
        dict: The initialized configuration.
        """
        # if config is None:  NOTE:#CHHECK FUTURE WHy to have it here
        if isinstance(config, dict):
            config = config
        elif isinstance(config, str) and ut.file_exists(config):
            config = ut.load_config(config)
        self.config = config
        # Add new values
        self.imports = self.config.get("imports", self.imports)  # TODO: Check if it works
        self.vars = self.config.get("vars", self.vars)
        self.config_vars = self.config.get("config_vars", self.config_vars)
        self.include = self.config.get("include", self.include)
        self.rules = self.config.get("rules", self.rules)
        return config

    def process_config_vars(self, config_vars: dict = None) -> str:
        """
        Processes the variables for the current instance.

        If the `vars` attribute is empty, the method returns immediately.
        Otherwise, it concatenates the string "#Variables" with each variable in the `vars` dictionary, separated by newline characters.

        Returns:
            str: A string containing the processed variables, or None if there are no variables.
        """

        # if not self.vars:
        # Check for the values and if there is an config nested value # REWORK AD DICT NOWWWW
        config_vars = config_vars or self.config.get("config_vars", None)
        output = "\n\n#Config variables\n"
        for key, val in config_vars.items():
            if isinstance(val, dict) and "config_nested" in val:
                value = ""
                for nested_key in val["config_nested"]:
                    value += f'["{nested_key}"]'
                # output[key] = value
                output += f"{key} = {value}\n"
            # elif isinstance(val, list):
            #     output[key] = f'["{val[0]}"]'
            else:
                output += f"{key} = {val}\n"
        return output

    def process_config(self):
        """
        Processes the configuration by sequentially processing imports, includes,
        variables, configuration variables, and rules. Combines the results into
        a single output string.

        Returns:
            str: The combined output string after processing all configuration
            components.
        """
        full_output = ""
        full_output += self.process_imports(self.imports) if self.imports else ""
        full_output += self.process_includes(self.include) if self.include else ""
        full_output += self.process_vars(self.vars) if self.vars else ""
        full_output += self.process_config_vars(self.config_vars) if self.config_vars else ""
        full_output += self.process_rules(self.rules) if self.rules else ""
        self.snakefile_string = full_output

    def process_rules(self, rules: dict = None) -> str:
        """_summary_

        Args:
            rules (dict, optional): _description_. Defaults to None.

        Returns:
            str: _description_
        """
        rules = rules or sdf.rule
        output = "\n\n#Rules\n"
        for rule_name, rule_value in rules.items():
            output += f"rule {rule_name}:\n"
            for key, value in rule_value.items():
                if key == "shell":
                    output += f"\t{key}:\n\t\t" + f'"""\n\t\t\t{value}\n\t\t"""'
                    continue
                if "{default_path}" in value:  # Replace default_path with actual data path
                    value = value.replace("{default_path}", ut.get_env_variable("OUTPUT_SNAKEMAKE_PATH"))
                output += f"\t{key}:\n\t\t{value}\n"
            output += "\n"
        return output

    def process_includes(self, includes: dict | list = None) -> str:
        """
        Processes the includes provided either as a dictionary or a list and returns a formatted string of paths.

        Args:
            includes (dict | list, optional): A dictionary containing 'global_path' and 'rules' keys or a list of absolute paths.
                - If a dictionary:
                    - 'global_path' (str): The base path to be used for rules. If 'default', it fetches the default path from environment variables.
                    - 'rules' (list): A list of rule paths to be merged with the global path.
                - If a list: A list of absolute paths to be validated.

        Returns:
            str: A formatted string of paths prefixed with "#Includes".

        Raises:
            ValueError: If the provided paths do not exist or if no global path is provided in the includes dictionary.
        """
        # Choose the correct global path to ensure that all rule paths are correctly prefixed.
        output = "\n\n#Includes\n" + "\n"
        if isinstance(includes, dict) and includes.get("global_path"):
            if includes["global_path"] == "default":
                global_path = ut.get_env_variable("OUTPUT_RULE_MAKER_PATH")
            else:
                global_path = includes["global_path"]
        elif isinstance(includes, list):  # if its a list of absolute paths
            for path in includes:
                if path.startswith("/"):
                    filepath = path
                else:
                    filepath = ut.merge_paths(ut.get_env_variable("OUTPUT_RULE_MAKER_PATH"), path)
                if not ut.file_exists(filepath):
                    msg = f"Path {filepath} does not exist."
                    ut.get_logger("error_logger").error(msg)
                    raise ValueError(msg)
            output += f"\ninclude: '{filepath}'"
            # return "\n\n#Includes\n" + "\n".join([f"include('{filepath}')" for path in includes])
        else:
            msg = "No global path provided in the includes dictionary."
            ut.get_logger("error_logget").error(msg)
            raise ValueError(msg)
        # rules = []
        # for rule in includes.get("rules", []):
        #     rules.append(ut.merge_paths(global_path, rule))
        # return "\n\n#Includes\n" + "\n".join([f"include('{rule}')" for rule in rules])
        return output

    def process_vars(self, vars: dict = None) -> str:
        """
        Processes the variables for the current instance.

        If the `vars` attribute is empty, the method returns immediately.
        Otherwise, it concatenates the string "#Variables" with each variable in the `vars` dictionary, separated by newline characters.

        Returns:
            str: A string containing the processed variables, or None if there are no variables.
        """
        # Options
        ## Name of variable: list of values
        ## Name of variable: dictionary of values
        ## Name of variable: name of function defined by "function" key in the config
        # if not self.vars:
        if vars:
            self.vars = vars
        if not self.vars:
            return
        output = ""
        wildcard_constraints = "\n\n#Wildcard constraints\nwildcard_constraints:"
        for k, v in self.vars.items():
            if k == "samples" and not v.get("paths", None) and not v.get("function", None):
                output += f"{k} = {self.samples}\n"
            elif k == "samples" and v.get("paths", None):
                output += f"{k} = {v['paths']}\n"
            elif k == "samples" and v.get("function", None):
                output += f"{k} = {v['function']}\n"
            elif isinstance(v, list):
                output += f"{k} = {v}\n"
            elif isinstance(v, dict) and "function" in v:  # If its a function
                output += f"{k} = {v['function']}\n"
            elif isinstance(v, dict) and "paths" in v:  # If its a list of paths
                output += f"{k} = {v['paths']}\n"
            elif isinstance(v, dict) and v.get("type", "") == "env":
                output += f"{k} = '{ut.get_env_variable(v.get('name'))}'\n"
            # Specific cases:
            elif k == "wildcard_constraints" and v == "default":
                for k, v in sdf.defaults["wildcard_constraints"].items():
                    wildcard_constraints += f"\n\t{k} = {v}\n"
            elif k == "wildcard_constraints":  # Without default - user specific
                if isinstance(v, dict):
                    for k, v in v.items():
                        wildcard_constraints += f"\n\t{k} = {v}\n"
            else:
                output += f"{k} = {v}\n"
        if wildcard_constraints:  # Add wildcard constraints if they exist
            output += wildcard_constraints

        return "\n\n#Variables\n" + output

    def process_imports(self, imports: dict = None) -> str:
        """
        Processes the imports for the current instance.

        If the `imports` attribute is empty, the method returns immediately.
        Otherwise, it concatenates the string "#Imported libraries" with each
        import in the `imports` list, separated by newline characters.

        Returns:
            str: A string containing the processed imports, or None if there are no imports.
        """
        if imports:
            self.imports = imports
        if not self.imports:
            return
        return "\n\n#Imported libraries\n" + "\n".join(self.imports)

    def make_smkfile(self, smkfile_content: str, smkfile_path: str = None) -> bool:
        """
        Creates and writes content to a Snakemake file.

        Args:
            smkfile_content (str): The content to be written to the Snakemake file.
            smkfile_path (str): The path where the Snakemake file will be saved.

        Returns:
            bool: True if the file was successfully created and written, False otherwise.

        Raises:
            Exception: If an error occurs during the file writing process, it will be caught and printed.
        """
        smkfile_path = smkfile_path or self.smkfile_path
        try:
            ut.create_directory(smkfile_path)
            with open(ut.merge_paths(smkfile_path, "Snakemake.smk"), "w") as smkfile:
                smkfile.write(smkfile_content)
            return True
        except Exception as e:
            print(f"Error occured during saving main Snakemake file: {e}")
            return False

    def get_smkfile(self) -> str:
        """
        Returns the content of the Snakemake file.

        Returns:
            str: The content of the Snakemake file.
        """
        return self.snakefile_string


def write_test_file(path, name, data):
    import os

    with open(os.path.join(path, name), "w") as f:
        f.write(data)
