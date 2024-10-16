import logging
import os
from pathlib import Path

from dynaconf import Dynaconf

from SnakeMaker import utils as ut

# Environ variables
os.environ["ROOT_PATH_FOR_DYNACONF"] = str(Path(__file__).parent.parent)
# Other env variables - default empty
os.environ["INPUT_DIR_PATH"] = ""
os.environ["OUTPUT_DIR_PATH"] = ""

settings = Dynaconf(settings_files=["config/settings.yaml"], environments=False)

# Loggers
log_settings = settings.get("logger")
info_logger = ut.create_logger(
    name="info_logger",
    path=ut.merge_root_path(log_settings.info.path),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - %(message)s",
    filemode="a",
)
error_logger = ut.create_logger(
    name="error_logger",
    path=ut.merge_root_path(log_settings.error.path),
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s - %(message)s",
    filemode="a",
)
debug_logger = ut.create_logger(
    name="debug_logger",
    path=ut.merge_root_path(log_settings.debug.path),
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s - %(message)s",
    filemode="a",
)

# Default lists/dicts
loggers = {
    "info_logger": info_logger,
    "error_logger": error_logger,
    "debug_logger": debug_logger,
}
pass

env_variables_mapping = {
    "input_data_dir": {
        "env_name": "INPUT_DIR_PATH",
        "key_set": ["app", "INPUT_DIR_PATH"],
        "merge_with_root_dir": True,
    },
    "output_data_dir": {
        "env_name": "OUTPUT_DIR_PATH",
        "key_set": ["app", "OUTPUT_DIR_PATH"],
        "merge_with_root_dir": True,
    },
    "dcm2niix_path": {
        "env_name": "DCM2NIIX_PATH",
        "key_set": ["app", "DCM2NIIX_PATH"],
        "merge_with_root_dir": False,
        "default": "",
    },
    "fsl_dir": {
        "env_name": "FSLDIR",
        "key_sepasst": ["app", "FSLDIR"],
        "merge_with_root_dir": False,
    },
}

rule_defaults = {
    "rule_prepare_dcm2niix": {"command": ["$DCM2NIIX_PATH", "-h"]},
}


# Configs for Subject and Session
t1 = {
    "name": "t1",
    "datatype": "anat",
    "nifti": "",
    "json": "",
}
pass
b0 = {
    "name": "b0",
    "datatype": "dwi",
    "acquisition": "b0",
    "direction": "",
    "nifti": "",
    "json": "",
    "bval": "",
    "bvec": "",
}

b1000 = {
    "name": "b1000",
    "datatype": "dwi",
    "acquisition": "b0",
    "direction": "",
    "nifti": "",
    "json": "",
    "bval": "",
    "bvec": "",
}

default_placeholders = {
    "input_dir_path": "INPUT_DIR_PATH",
    "rule0_folder_name": "RULE0_FOLDER_NAME",
    # Add more mappings as needed
}

output_env_variables = ["OUTPUT_RULE_MAKER_PATH", "OUTPUT_SNAKEMAKE_PATH"]
env_variables_excluded = ["ROOT_PATH_FOR_DYNACONF", "APPLICATION_ROOT_PATH", "OUTPUT_DIR_PATH"]
list_env_variables = ["CUSTOM_FUNCTIONS_PATH_LIST"]


dry_run_command = """#!/bin/bash
snakemake all --dry-run --debug-dag --snakefile Snakemake.smk
"""
hot_run_command = """#!/bin/bash
snakemake all --cores all --debug-dag --keep-going --snakefile Snakemake.smk
"""


# Custom Exceptions
class ConfigError(Exception):
    """
    Exception raised for errors in the rule configuration.
    Attributes:
        message (str): Explanation of the error.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
