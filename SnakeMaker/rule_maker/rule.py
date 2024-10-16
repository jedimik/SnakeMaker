from pathlib import Path

from SnakeMaker import defaults as df
from SnakeMaker import utils as ut
from SnakeMaker.rule_maker import rule_defaults as rdf
from SnakeMaker.rule_maker import rule_utils as rut


class Rule:
    def __init__(self):
        # Attributes
        self.name = ""
        self.inputs = dict()
        self.params = dict()
        self.outputs = dict()
        self.resources = dict()
        self.description = ""
        self.shell = list()
        self.run = ""
        self.rule_string = ""
        # Initialize

    def __str__(self):
        """
        Returns a string representation of the Rule object.

        The string includes the name, inputs, parameters, outputs, shell command, run condition, and resources of the Rule.
        """
        return f"Rule(name={self.name}, inputs={self.inputs}, params={self.params}, outputs={self.outputs}, shell={self.shell}, run={self.run}, resources={self.resources})"

    def construct_plane_rule(self):
        inputs = ""
        i = 0
        for input in self.inputs:
            for key, value in input.items():
                if isinstance(value, dict) and "function" in value.keys():  # if its a different param
                    inputs += f"\n\t\t{key}={value.get('function')}," if i > 0 else f"{key}={value.get('function')},"
                else:
                    inputs += f"\n\t\t{key}={f'"{Path(value)}"'}," if i > 0 else f"{key}={f'"{Path(value)}"'},"
                i += 1
        # Params
        params = ""
        for param in self.params:
            for key, value in param.items():
                if isinstance(value, dict):  # if its a different param
                    params += f"\n\t\t{key}={value.get('function')},"  # Like function call
                elif isinstance(value, str) and value.startswith("/"):  # if its a path value
                    params += f"\n\t\t{key}={f'"{Path(value)}"'},"
                elif isinstance(value, str) and value.startswith("lambda"):
                    params += f"\n\t\t{key}={value},"
                else:
                    params += f"\n\t\t{key}={f'"{value}"'},"

        outputs = "\n\t\t".join(
            [f'{key}="{Path(value) if isinstance(value, str) else value}",' for outputs_dict in self.outputs for key, value in outputs_dict.items()]
        )
        resources = (
            "\n\t\t".join([f"{key}={value}," for resources_dict in self.resources for key, value in resources_dict.items()]) if self.resources else ""
        )
        shell = '"""\n\t\t\t' + "\n\t\t\t".join([f"{cmd}" for cmd in self.shell]) + '\n\t\t"""' if self.shell else ""
        run = ""
        i = 0
        for r in self.run:
            for key, val in r.items():
                run += f"\n\t\t{key}={val}" if i > 0 else f"{key}={val}"
        rule_str = f"# Description: {self.description}" if self.description else "# Description missing"
        rule_str += f"""\nrule {self.name}:"""
        if not ut.is_none_or_empty(inputs):  # Set inputs
            rule_str += f"""\n\tinput:\n\t\t{inputs}"""
        if not ut.is_none_or_empty(params):  # Set parameters
            rule_str += f"""\n\tparams:\t\t{params}"""
        if not ut.is_none_or_empty(outputs):  # Set outputs
            rule_str += f"""\n\toutput:\n\t\t{outputs}"""
        if not ut.is_none_or_empty(resources):  # Set resources
            rule_str += f"""\n\tresources:\n\t\t{resources}"""
        if not ut.is_none_or_empty(shell):  # Set shell
            rule_str += f"""\n\tshell:\n\t\t{shell}"""
        if not ut.is_none_or_empty(run):  # Set run
            rule_str += f"""\n\trun:\n\t\t{run}"""
        # Sometimes run
        self.rule_string = rule_str + "\n"


class RuleBuilder:
    def __init__(self, shortened: bool = False):
        """
        Initializes a new instance of the Rule class.
        """
        self.rule = Rule()
        self.shortened = shortened

    def set_name(self, name: str):
        """
        Sets the name of the rule.

        Parameters:
        name (str): The name to set for the rule.

        Args:
            name (str): The name of the rule.

        Returns:
            self: The Rule object with the updated name.
        """
        self.rule.name = name
        return self

    def set_inputs(self, inputs: dict | None, registered_names: dict = None) -> list | None:
        """
        Set the inputs for the rule.

        Args:
            inputs (dict): A dictionary containing the inputs for the rule.

        Returns:
            self: The Rule object with the updated inputs.
        """
        if inputs is None:
            msg = f"Inputs for rule {self.rule.name} is None. Check the inputs for the rule."
            ut.get_logger("error_logger").error(msg)
            print(f"{msg}. Check the inputs for the rule.")
        self.rule.inputs = rut.parse_input_keys_rule(inputs, registered_names, shortened=self.shortened)
        register_names(self, self.rule.inputs, registered_names)
        return self

    def set_params(self, params: dict = None, registered_name: dict = None) -> list | None:
        """
        Set the parameters for the rule.

        Args:
            params (dict): A dictionary containing the parameters for the rule.

        Returns:
            self: The Rule object with the updated parameters.
        """
        if params is None:
            return self
        self.rule.params = rut.parse_params(params, registered_name)
        return self

    def set_outputs(self, outputs: dict | None, registered_names: dict = None) -> list | None:
        """
        Sets the outputs for the rule.

        Args:
            outputs (dict): A dictionary containing the outputs for the rule.

        Returns:
            self: The Rule object with the updated outputs.
        """
        if outputs is None:
            msg = f"Outputs for rule {self.rule.name} is None. Check the outputs for the rule."
            ut.get_logger("error_logger").error(msg)
            print(f"{msg}. Check the outputs for the rule.")
        self.rule.outputs = rut.parse_output_keys_rule(outputs, registered_names, shortened=self.shortened)
        register_names(self, self.rule.outputs, registered_names)
        return self

    def set_shell(self, shell: str | None, inputs: dict, outputs: dict) -> list | None:
        """
        Set the shell for the rule.

        Args:
            shell (str): The shell to set.

        Returns:
            self: The Rule object with the updated shell.
        """
        if shell is None:
            return self
        self.rule.shell = rut.parse_shell_command(shell, inputs=inputs, outputs=outputs)
        return self

    def set_run(self, run: str | None, registered_names: dict = None) -> list | None:
        """
        Set the run value of the rule.

        Parameters:
        - run (str): The run value to be set.

        Returns:
        - self: The Rule object with the updated run value.
        """
        if run is None:
            return self
        self.rule.run = rut.parse_run_command(run, registered_names)
        return self

    def set_resources(self, resources: dict):
        """
        Set the resources for the rule.

        Args:
            resources (dict): A dictionary containing the resources.

        Returns:
            self: The Rule object with the updated resources.
        """
        self.rule.resources = resources
        return self

    def set_description(self, description: str | None):
        """
        Set the description of the rule.

        Args:
            description (str): The description to set for the rule.

        Returns:
            self: The Rule object with the updated description.
        """
        self.rule.description = description if description is not None else ""
        return self

    def build(self):
        """
        Builds and returns the rule.

        Returns:
            The built rule.
        """
        return self.rule


def register_names(self, vars: list, registered_names: dict):
    for var in vars:
        for var_name, path in var.items():
            if var_name in registered_names.keys():
                continue
            registered_names[var_name] = path
