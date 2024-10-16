allowed_keys = {
    "input": {"path": str, "filename": str},
    "output": {
        "output_name": str,
        "file_extension": str,
        "output_folder": str,
        "path": str,
    },
    "shell": {
        "command": [str, list],
    },
    "run": {
        "command": [str, list],
    },
}

function_structure = {
    "function": {
        "name": str,
        "args": dict,
    }
}

file_register_keys = ["inputs", "outputs"]

rule0_folder_name = "base"

rules_demo = {}
