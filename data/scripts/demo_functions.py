import glob
import json
import os
import shlex
import subprocess as sp
from pathlib import Path

import nibabel as nb
import numpy as np


def findTotalReadoutTime(input_json: str) -> str:
    return str(load_config_json(input_json)["TotalReadoutTime"])


def load_config_json(filepath):
    with open(filepath, "r", encoding="utf-8") as jsonfile:
        config = json.load(jsonfile)
    return config


def move_rule0(SM_instance):
    import SnakeMaker.snakemaker as sm

    """
    Move the rule0 files to the output directory.
    """
    for sample in SM_instance.samples:
        process_string = f"""bash <path>SnakeMaker/data/scripts/move_rule0.sh 
        --input_b {SM_instance.env_vars['INPUT_DIR_PATH']}/{sample}/dwi \
        --input_t1 {SM_instance.env_vars['INPUT_DIR_PATH']}/{sample}/dwi \
        --sample {sample} \
        --b0 b0 \
        --b1000 b1000 \
        --t1 t1 \
        --output {SM_instance.env_vars['OUTPUT_DIR_PATH']}/base
        """
        print(process_string)
        command = shlex.split(process_string)
        sp.run(command, shell=False)


def create_index_file(input_bvec: str, output_file: str, index: int = None) -> None:
    """
    Create an index file based on the number of elements in the input bvec file.

    Args:
        input_bvec (str): The path to the input bvec file.
        output_file (str): The path to the output index file.
        index (int, optional): The index to be used. Defaults to None.

    Returns:
        None
    """
    with open(input_bvec, "r") as f:
        index = len(f.readline().strip().split())
    with open(str(output_file), "w") as f:
        for i in range(index):
            f.write("1\n")
        for i in range(index):
            f.write("1\n")
            f.write("1\n")
            f.write("1\n")
