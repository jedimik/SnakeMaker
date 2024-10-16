import ast
import importlib
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml
from dynaconf.utils.boxing import DynaBox
from dynaconf.vendor.box.box_list import BoxList


def merge_paths(base_path: str, merge_path: str | list) -> str:
    """
    Merge base path with merge path.

    Args:
        base_path (str): The base path.
        merge_path (str|list): The path to be merged with the base path.

    Returns:
        str: The merged path.
    """
    base = Path(base_path)
    if isinstance(merge_path, list):
        return str(base.joinpath(*merge_path))
    else:
        return str(base.joinpath(merge_path))


def get_last_directory(path: str | list, level: str | int):
    """
    Extracts the last 'level' directories from the given path(s).
    Parameters:
    path (str or list): A single path as a string or a list of paths.
    level (str or int): The number of directory levels to extract from the end of the path(s).
    Returns:
    str or list: The last 'level' directories of the given path if a single path is provided.
                 A list of the last 'level' directories for each path if a list of paths is provided.
    Example:
    >>> get_last_directory('/a/b/c/d', 2)
    'c/d'
    >>> get_last_directory(['/a/b/c/d', '/e/f/g/h'], 2)
    ['c/d', 'g/h']
    """
    if isinstance(level, str):
        level = int(level)
    if isinstance(path, list):
        values = [Path(single_path).parts[-level:] for single_path in path]
        return [os.path.join(*value) for value in values]
    values = Path(path).parts[-level:]
    return os.path.join(*values)


def is_none_or_empty(value: str) -> bool:
    """
    Check if the value is None or empty.

    Args:
        value (str): The value to check.

    Returns:
        bool: True if the value is None or empty, False otherwise.
    """
    return value is None or value == ""


def get_current_datetime():
    """
    Get current date and time.

    Returns:
        str: The current date and time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def set_env_variable(var: str, value: str, log: bool = False, as_list: bool = False) -> None:
    """
    Set the environment variable with the specified value.

    Args:
        var (str): The name of the environment variable.
        value : The value of the environment variable.
    """
    if as_list:
        if not isinstance(value, list):
            value = [value]
        os.environ[var] = ";".join(value)
    os.environ[var] = str(value)
    if log:
        return {var: value}


def ensure_list(variable):
    """
    Checks if a variable is a Dynaconf BoxList and converts it to a regular list.

    Args:
      variable: The variable to check.

    Returns:
      A list (either the original list if it was already a list or a
      converted list from a BoxList).
    """
    if isinstance(variable, BoxList):
        return list(variable)  # Convert BoxList to list
    elif isinstance(variable, list):
        return variable  # Already a list, return as is
    else:
        raise False


def get_env_variable(var: str, as_list: bool = False) -> str:
    """
    Get the value of the environment variable.

    Args:
        var (str): The name of the environment variable.

    Returns:
        str: The value of the environment variable.
    """
    if as_list and os.getenv(var):
        try:
            return ast.literal_eval(os.getenv(var))
        except (ValueError, SyntaxError):
            return os.getenv(var).split(";")
    return os.getenv(var)

    # Safely accessing deeply nested values


def get_nested_conf(data, *keys, default=None):
    """
    Retrieve a nested value from a dynaconf BoxList using a sequence of keys.

    Args:
        data (dict): The dictionary to search.
        *keys: A sequence of keys to traverse the dictionary.
        default: The value to return if any key is not found (default is None).

    Returns:
        The value found at the nested key location, or the default value if any key is not found.
    """
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, {})
        else:
            return default
    return data if data != {} else default


def directory_exists(directory_path, create=False):
    """
    This function checks if a directory exists.

    Args:
        directory_path: The path to the directory.
        create: If True, the directory is created if it doesnt exist

    Returns:
        True if the directory exists, or True when created, False otherwise.
    """
    if not os.path.isdir(directory_path) and create:
        create_directory(directory_path)
        return os.path.isdir(directory_path)
    return os.path.isdir(directory_path)


def create_directory(directory_path):
    """
    This function creates a directory if it doesn't already exist.

    Args:
        directory_path: The path to the directory to be created.
    """
    try:
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_path}' already exists.")


def merge_root_path(path: str | list) -> str:
    """
    Merges the root path with the specified path.

    Args:
        path (str|list): The path to merge with the root path.

    Returns:
        str: The merged path.
    """
    if isinstance(path, list):
        return str(Path(get_env_variable("ROOT_PATH_FOR_DYNACONF")).joinpath(*path))
    return str(Path(get_env_variable("ROOT_PATH_FOR_DYNACONF")) / path)


def get_sample(path, input_dir):
    """
    Get the sample name from a given file path relative to the input directory.

    Args:
        path (str): The file path.
        input_dir (str): The input directory path.

    Returns:
        str: The sample name.
    """
    # Remove any surrounding quotes
    path = path.strip("'")
    input_dir = input_dir.strip("'")

    # Normalize paths to handle any inconsistencies in separators
    path = os.path.normpath(path)
    input_dir = os.path.normpath(input_dir)

    # Get the relative path
    relative_path = os.path.relpath(os.path.dirname(path), input_dir)

    # Split the relative path and take the first two components
    components = relative_path.split(os.sep)
    sample = os.path.join(*components[:2])

    return sample


def get_nested_value_from_dict(dictionary, keys: list):
    """Return a given value from dictionary based on list of keys

    Args:
        dictionary (_type_): base configuration
        keys (_type_): list of keys

    Returns:
        _type_: returns value on given key
    """
    try:
        current_item = dictionary
        for key in keys:
            if isinstance(current_item, list):
                # If current item is a list, we need to check each dictionary in the list
                new_current_item = []
                for item in current_item:
                    if isinstance(item, dict):
                        value = item.get(key, None) or item.get(key.upper(), None)
                        if value is not None:
                            new_current_item.append(value)
                if not new_current_item:
                    current_item = None
                else:
                    current_item = new_current_item
            else:
                current_item = current_item.get(key, None) or current_item.get(key.upper(), None)

            if current_item is None:
                break

        return current_item
    except Exception as e:
        msg = f"An error occurred while getting nested value of {'.'.join(keys)} for dictionary: {dictionary}\n with error:{e}"
        get_logger("error_logger").error(msg)
        raise Exception(msg)


def create_logger(name: str, path: str, level: str, format: str, filemode: str) -> logging.Logger:
    """
    Create a logger with the specified parameters.

    Args:
        name (str): The name of the logger.
        path (str): The path to the log file.
        level (str): The log level.
        format (str): The format of the log message.
        filemode (str): The file mode.

    Returns:
        logging.Logger: The logger with the specified parameters.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.FileHandler(path, mode=filemode)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(name: str, loggers: dict = None) -> logging.Logger:
    """
    Get the logger with the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The logger with the specified name.
    """
    from SnakeMaker.defaults import loggers

    loggers = loggers
    return loggers.get(name)


def test_dependency(rule_dict: dict) -> bool:
    """
    Test the dependency by executing the command specified in the rule dictionary.

    Args:
        rule_dict (dict): A dictionary containing the rule information.

    Returns:
        bool: True if the command executed successfully, False otherwise.
    """
    # First test command
    test_command(rule_dict.get("dependencies", None).get("command"))


def test_command(command: dict) -> bool:
    try:
        command_list = [os.path.expandvars(item) for item in command.get("command")]
        result = subprocess.run(command_list, check=True)
        if result.returncode == 0:
            msg = f"Command {command.get('command')} executed successfully"
            get_logger("info_logger").info(msg)
            return True
        else:
            msg = f"Command {command.get('command')} failed to execute"
            get_logger("error_logger").error(msg)
            return False
    except Exception as e:
        msg = f"An error occurred while executing command {command.get('command')} with error:{e}"
        get_logger("error_logger").error(msg)
        return False


def create_shell_script(script_path, script_content):
    """
    Creates a shell script with the given content and makes it executable.

    Args:
      script_path: The path to the shell script file.
      script_content: The content of the shell script.
    """
    try:
        with open(script_path, "w") as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)  # Make the script executable
        print(f"Shell script created and made executable: {script_path}")
    except OSError as e:
        print(f"Error creating shell script: {e}")


# TODO: in future also add something to handle non default dependencies
def validate_dependencies(config: dict, rule: str) -> None:
    """
    Validates the dependencies for a given rule in the configuration.

    Args:
        config (dict): The configuration dictionary.
        rule (str): The rule to validate dependencies for.

    Raises:
        Exception: If the dependency test for the rule fails.
    """
    rule_dict = config.get(rule)
    env_dependencies = rule_dict.get("dependencies", None).get("env_vars", None)
    sw_dependencies = rule_dict.get("dependencies", None).get("sw_dependencies", None)
    rule_dependencies = rule_dict.get("dependencies", None).get("rule_dependencies", None)

    if rule_dict.get("dependencies", None).get("test", False):  # Test if the script defined is working
        if not test_dependency(rule_dict):
            msg = f"Dependency test for rule {rule} failed"
            get_logger("error_logger").error(msg)
            raise Exception(msg)
    if env_dependencies:
        for env_var in env_dependencies:
            if not os.getenv(env_var):
                msg = f"Environment variable {env_var} is not set"
                get_logger("error_logger").error(msg)
                raise Exception(msg)
    return True
    # TODO: handle sw and rule dependencies


def replace_placeholders(command_list, **kwargs):
    """
    Replaces placeholders in a command list with corresponding values from kwargs. Placeholders have prefix as dollarn sign '$'.

    Args:
        command_list (list): List of strings representing a command with placeholders.
        **kwargs: Keyword arguments containing the values to replace the placeholders.

    Returns:
        list: List of strings with placeholders replaced by corresponding values.
    """
    return [kwargs.get(part[1:], part) if part.startswith("$") else part for part in command_list]


def load_config(config_path: str) -> dict:
    """
    Load the configuration from the specified path.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The configuration dictionary.
    """
    if config_path.endswith(".json"):
        with open(config_path, "r") as f:
            return json.load(f)
    elif config_path.endswith(".yaml"):
        with open(config_path, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    else:
        raise Exception("Unsupported configuration file format, please use either JSON or YAML.")


def import_scripts(script_paths: str | list, function_name: str = False) -> importlib:
    """
    Imports Python scripts from a list of paths

    Args:
      script_paths: A list of dictionaries, where each dictionary has keys:
                     'path': The path to the Python script.
    """
    if not isinstance(script_paths, list):
        script_paths = [script_paths]
    for script_path in script_paths:
        script_dir = os.path.dirname(script_path)
        script_name = os.path.splitext(os.path.basename(script_path))[0]

        if script_dir not in sys.path:
            sys.path.append(script_dir)

        # Import using importlib.import_module()
        module = importlib.import_module(script_name)
        if function_name and hasattr(module, function_name):
            return module


def file_exists(file_path: str) -> bool:
    """
    Check if the file exists.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)


def replace_placeholders_test(obj, placeholders):
    """
    Recursively replace placeholders in a nested dictionary or list.

    Args:
        obj: The JSON object (dictionary or list) where placeholders need replacing.
        placeholders: A dictionary mapping placeholder names to environment variables.

    Returns:
        The object with replaced placeholders.
    """
    if isinstance(obj, dict):
        return {k: replace_placeholders(v, placeholders) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_placeholders(v, placeholders) for v in obj]
    elif isinstance(obj, str):
        # Replace placeholders in strings with environment variables or default values
        for placeholder, env_var in placeholders.items():
            env_value = os.getenv(env_var, f"{{{placeholder}}}")  # Keep the placeholder if env var not found
            obj = obj.replace(f"{{{placeholder}}}", env_value)
        return obj
    else:
        return obj  # Return the object unchanged if it's not a string, dict, or list


def string_contains_pattern(string: str, pattern: str) -> bool:
    """
    Check if the string matches the specified pattern.

    Args:
        string (str): The string to check.
        pattern (str): The pattern to match.

    Returns:
        bool: True if the string contains the pattern, False otherwise.
    """

    return bool(re.search(pattern, string))
    return bool(re.search(pattern, string))
