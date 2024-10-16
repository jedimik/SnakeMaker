from pathlib import Path

import numpy as np

from SnakeMaker import utils as ut
from SnakeMaker.rule_maker import rule_defaults as rdf
from SnakeMaker.subject import Subject, SubjectSession


def get_base_rule_dict():
    return ut.get_env_variable("OUTPUT_RULE_MAKER_PATH")


def parse_input_keys_rule(rule: dict, registered_names: dict = None, shortened: bool = False):
    """
    Parses a dictionary of rules to generate output paths or functions based on the provided keys and values.

    Args:
        rule (dict): A dictionary where each key represents an output name and the value is a dictionary containing
                     details about the path, function, input folder, or filename.
        registered_names (dict, optional): A dictionary of already registered names and their corresponding paths.
                                           Defaults to None.

    Returns:
        list: A list of dictionaries where each dictionary contains the output name and its corresponding path or
              function details.
    TODO: Add examples

    Raises:
        KeyError: If a required key is missing in the input rule.
        ValueError: If the path for a key is not provided in the input rule.
    """
    if rule is None:  # if inputs are not provided
        return []
    output_creator = list()
    for key, value in rule.items():
        output = dict()
        # First check if that file is not already registered
        if key in registered_names.keys() if registered_names else False:
            output_creator.append({key: registered_names.get(key)})
            continue
        if value.get("path", None):  # if there is path for output name
            output[key] = value.get("path")
        elif value.get("function", None):  # For other functions, which returns specific path
            output[key] = construct_function_output(key, value, registered_names, shortened=shortened)  # TODO: shortened
        elif value.get("input_folder", None) and value.get("filename", None):
            output[key] = (
                str(
                    Path(ut.get_env_variable("INPUT_DIR_PATH"))
                    / Path(value.get("input_folder"))
                    / Path("{sample}")
                    / Path(f"{value.get('filename')}")
                )
                if not shortened
                else f"{{output_path}}/{value.get('input_folder')}/{value.get('filename')}"
            )
        else:
            msg = f"Path for {key} is not provided in the input rule"
            ut.get_logger("error_logger").error(msg)
            print(f"{msg}. Check the naming of the keys in the input rule.")
            # TODO: Add own exception
        output_creator.append(output)
    return output_creator


def parse_output_keys_rule(rule: dict, registered_names: dict = None, shortened: bool = False):
    """
    Parses the output keys from a given rule dictionary and generates a list of output paths.

    Args:
        rule (dict): A dictionary containing rule definitions. Each key-value pair represents
                     a rule where the key is the rule name and the value is a dictionary with
                     rule properties.
        registered_names (dict, optional): A dictionary of registered names. Defaults to None.

    Returns:
        list: A list of dictionaries where each dictionary represents an output path for a rule.
              If the rule contains a "path" key, the output path is taken from the "output_name".
              Otherwise, the output path is constructed using the base rule dictionary, output
              folder, and output name.
    """
    output_creator = list()
    for key, value in rule.items():
        # File based on key
        output = dict()
        if value.get("path", None):  # if there is path for output name
            output[key] = value.get("output_name")
        else:
            output[key] = (
                str(Path(get_base_rule_dict()) / Path(value.get("output_folder")) / Path("{sample}") / Path(f"{value.get('output_name')}"))
                if not shortened
                else f"{{output_path}}/{value.get('output_folder')}/{{sample}}/{value.get('output_name')}"
            )
        output_creator.append(output)
    return output_creator


def parse_params(rule: dict, registered_names: dict = None, shortened: bool = False):
    """
    Parses a given rule dictionary and generates a list of output configurations.

    This function processes each key-value pair in the input `rule` dictionary. If the value is a nested dictionary,
    it checks for specific keys ("name" and "folder" or "function") to create output configurations. If the value is
    not a nested dictionary, it directly adds the key-value pair to the output configurations.

    Args:
        rule (dict): The input rule dictionary to be parsed.
        output_creator (list, optional): A list to store the output configurations. If None, a new list is created.

    Returns:
        list: A list of dictionaries representing the output configurations.

    Raises:
        ValueError: If the nested dictionary in the rule has incorrect keys.
    """
    output_creator = list()
    for key, value in rule.items():
        output = dict()
        # if is nested dict:
        if isinstance(value, dict):
            if value.get("name", None) and (value.get("folder", None)):
                output[key] = str(Path(get_base_rule_dict()) / Path(value.get("folder")) / Path("{sample}") / Path(f"{value.get('name')}"))
                output_creator.append(output)
            elif value.get("function", None):
                # output_creator.append({k_: v_} for k_, v_ in x.items() for x in construct_function_output(key, value))\
                for item in construct_function_output(key, value, registered_names):
                    output_creator.append(item)
            else:
                msg = f"Incorrect {key} : {value} in input rule"
                ut.get_logger("error_logger").error(msg)
                print(f"{msg}. Check the naming of the keys in the input rule.")
        else:
            output = dict()
            output[key] = value
            output_creator.append(output)
    return output_creator


def parse_shell_command(rule: dict, inputs: dict, outputs: dict):
    """
    Parses a shell command from a given rule and appends it to the output_creator list.

    Args:
        rule (dict): A dictionary containing the shell command to be parsed.
        inputs (dict): A dictionary of input parameters (not used in the current implementation).
        outputs (dict): A dictionary of output parameters (not used in the current implementation).
        output_creator (list, optional): A list to which the parsed command will be appended.
                                         If None, a new list will be created.

    Returns:
        list: The updated output_creator list with the parsed command appended.
    """
    output_creator = list()
    for cmd in rule:
        output_creator.append(cmd)
    return output_creator


def parse_run_command(
    rule: dict,
    registered_names: dict = None,
):
    """
    Parses a rule dictionary to extract function commands.

    This function iterates over the key-value pairs in the provided rule dictionary.
    If a key named "function" is found, its corresponding value is appended to the
    output_creator list. If output_creator is not provided, a new list is created.

    Args:
        rule (dict): A dictionary containing rule definitions.
        output_creator (list, optional): A list to store extracted function commands.
                                         Defaults to None.

    Returns:
        list: A list containing the extracted function commands.
    """
    output_creator = list()
    for key, val in rule.items():
        if key == "function":  # if its called function
            output_creator.append(construct_function_output(key, rule, registered_names, from_run=True))
    # hotfix
    if isinstance(output_creator[0], list):
        return output_creator[0]
    return output_creator


def construct_function_output(var_name, value: dict | str, registered_names: dict = None, from_run: bool = False, shortened: bool = False) -> list:
    """
    Constructs the output string for a given function based on the provided value dictionary.

    Args:
        var_name (str): The name of the variable for which the function output is being constructed.
        value (dict | str): A dictionary or string containing the function details and arguments.
        registered_names (dict, optional): A dictionary of registered names. Defaults to None.
        shortened (bool, optional): A flag to indicate if the paths are shortened. Defaults to False.

    Returns:
        str: The constructed function output string.

    Raises:
        KeyError: If required keys are missing in the value dictionary.
        TypeError: If the value is not a dictionary or string.

    Notes:
        - If the function name is "base_input_dir", constructs a path based on the "INPUT_DIR_PATH" environment variable.
        - If the function has "input_files" in its arguments, constructs a function string for each input file.
        - If the function has "from_input" in its arguments, constructs a lambda function string for each input variable.
        - If the function arguments are a list, constructs a function call string with the arguments.
        - Logs an error if the function details are not provided in the input rule.
    """
    output = []
    if value.get("function", {}).get("name") == "base_input_dir" and not from_run:
        return (
            str(Path(ut.get_env_variable("INPUT_DIR_PATH")) / Path(value.get("folder", "") / Path("{sample}") / Path(f"{value.get('filename')}")))
            if not shortened
            else f"{{output_path}}/{value.get('folder')}/{{sample}}/{value.get('filename')}"
        )
    elif value.get("function", {}) and isinstance(value.get("function"), dict):
        func_name = value.get("function").get("name")
        if "args" in value.get("function") and "from_input" in value.get("function").get("args", {}).keys() and not from_run:
            for item in value.get("function").get("args").get("from_input"):
                function_string = f"{func_name}(f'{parse_input_keys_rule({item: value.get("function").get("args").get("from_input").get(item)},registered_names)[0].get(item)}')"
                if ut.string_contains_pattern(function_string, r"{.+}"):  # Check if there is some wildcard used
                    # check for shortened version
                    if "{sample}" in function_string:
                        function_string = function_string.replace("{sample}", "{wildcards.sample}")
                    output.append({item: f"lambda wildcards: {function_string}"})
                else:
                    output.append({item: function_string})
        elif (
            "args" in value.get("function") and "from_input" in value.get("function", {}).get("args") and not from_run
        ):  # From input - look for registeres names
            for var in value.get("function", {}).get("args").get("from_input"):
                values = value.get("function", {}).get("args").get("from_input")
                output.append(
                    {var: f"lambda wildcards, input: {value.get("function").get("name")}(input.{values.get(var).get("name","")})"}
                )  # Otherwise it will throw error.
        elif "args" in value.get("function") and isinstance(value.get("function").get("args"), list) and not from_run:
            output[var_name] = f"{func_name}(" + ",".join(value.get("function").get("args")) + ")"
        elif "args" in value.get("function") and isinstance(value.get("function").get("args"), dict) and from_run:  # For run command specially
            for item in value.get("function").get("args").get("from_input"):
                # function_string = f"{func_name}('{parse_input_keys_rule({item: value.get("function").get("args").get("from_input").get(item)},registered_names)[0].get(item)}')"
                function_string = f"{func_name}(input.{value.get("function").get("args").get("from_input").get(item).get("name")})"
                output.append({item: function_string})
    else:
        msg = f"Function for {var_name} is not provided in the input rule"
        ut.get_logger("error_logger").error(msg)
        print(f"{msg}. Check the naming of the keys in the input rule.")
    return output
