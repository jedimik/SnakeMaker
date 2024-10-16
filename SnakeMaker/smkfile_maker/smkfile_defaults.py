default_imports = ["from datetime import datetime", "import numpy as np"]

default_vars = {
    "samples": {
        "paths": ["/path/to/sample1", "/path/to/sample2"],
    },
    "wildcard_constraints": "default",
    "years": ["2018", "2020"],
}

# Defube cystin global path and rules to look for
default_include = {"global_path": "/path/to/global", "rules": ["first_rule.smk", "last_rule.smk", "groups.smk"]}
default_include = {
    "global_path": "default",
    "rules": ["first_rule", "last_rule", "groups"],
}  # Also option default (for whole process - default rule output folder)
# Or another version with fullpaths
default_include = ["default_include/smkfile_maker/smkfile_defaults.py"]


defaults = {
    "wildcard_constraints": {"sample": "'|'.join([re.escape(x) for x in samples])"},
}
rule_all_options = ["first_rule", "last_rule", "groups"]

config_file = "default"  # Can be options like default, or provided some different, or providded by main app
config_vars = {
    "sides": {"config_nested": ["sides"]},  # If I want to get some nested keys from the config to main snakemake file
}

default_rules = {  # all have only one value per line. no list allowed, but multiple rules as checkpoints can be used
    # Dont forget to add processed to all, now its not
    "all": {
        "input": "expand('{default_path}/{sample}/data/{side}/{year}.csv', sample=samples, side=sides, year=years)",
    },
    "process_one": {
        "input": "expand('{default_path}/{sample}/data/{side}/{year}.csv', sample=samples, side=sides, year=years)",
        "output": "expand('{default_path}/{sample}/results/{side}/{year}.csv', sample=samples, side=sides, year=years)",
        "shell": "python process_one.py {input} {output}",
    },
}
