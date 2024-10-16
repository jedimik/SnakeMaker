# Snakefile configuration\
> Snakefile configuration file is a YAML or JSON file that contains all the necessary information for the creation of main SnakeFile file, which serves as entry point for the Snakemake engine.
> You can define here imports, variables, include section, wildcard constraints and the main rule all.

## Imports:
> Imports are a place to define all the necessary ptthon imports for the main Snakefile.
> Can be specified as a lsit of strings
```yaml
imports:
  - os
  - sys
  - pandas as pd
  - numpy as np
```
## Variables:
> Variables are a place to define all the necessary variables for the main Snakefile.
> Can be assigned by value, leaved empty or assigned with the environment variable.

- `samples` - is reserved keyword for the samples list, which can be a list of values. When empty - it will be filled by the samples calculated from the input folder.
```yaml
vars:
  samples: # reserved keyword for samples
    paths:
    function: 
```
- `env` variables - is a place to define define variable, just need specify the name.
```yaml
vars:
  input_path: # name of the variable
    type: env
    name: INPUT_DIR_PATH # name of the env. variable
```
- `normal` variables - is a place to define define variable and assign the value.
```yaml
vars:
  var1: VarValue
```
## Include:
> Include is a place to define all the necessary includes for the main Snakefile.
> Can be specified as a list of strings. With the relative path to the OUTPUT_RULE_MAKER_PATH, or absolute paths to the rule files or custom python scripts.
```yaml
include:
  - rules.smk
  - <path>SnakeMaker/data/scripts/demo_functions.py
```

## Rules
> Rules are a place to define the main rule for the main Snakefile.
> Can be specified as a dictionary with the rule name and the rule configuration.
> By default the main Snakefile should contain rule all, which will be the main rule for the workflow. It can be dependent on smaller rules.
```yaml
rules:
  all:
    input: expand('{output_path}/eddy/{sample}/b1000_eddy_unwarped.nii.gz', sample=samples, output_path=output_path)

```