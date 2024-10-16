# Configuration
> Configuration file is a YAML or JSON file that contains all the necessary information for the SnakeMaker to run. It contains information about the input and output directories, the paths to the custom functions, rules, and Snakemake files, and other settings. The configuration file is used to define the workflow and the parameters that will be used to run the workflow. 
> Configuration is divided into three files:

- `settings.yaml` - main configuration file, place to define all environmental variables and paths for other configuration files.
- `rule_config.yaml` - configuration file for rules, place to define all rules for the workflow. More info is in the [Rule configuration](rule_configuration.md) section.
- `snakefile_config.yaml` - configuration file for main Snakefile, an entry point for the Snakemake engine. More info is in the [Snakefile configuration](snakefile_configuration.md) section.

## Settings.yaml
> This configuration file is a place to define loggers (will be moved soon from configuration), all environmental variables and paths for other configuration files. It is divided into sections:

- `logger` - section for loggers, will be moved soon from configuration
- `configuration_files` - section for paths to other configuration files
- `app` - section to define enviromental variables

### Configuration files
- `rule_configuration` - path to the rule configuration file
- `snakefile_configuration` - path to the snakefile configuration file

### App
- `APPLICATION_ROOT_PATH` - Specifies the root path of the application. Options: default - which means project path, by_output - which is driven by output_dir_path. When default other Output section is relative into application root path. But there need to be OUTPUT_DIR_PATH as absolute path defined.
- `INPUT_DIR_PATH` - Specifies the path to the input data files directory. To look for samples
- `OUTPUT_DIR_PATH` - Specifies the path to the output data files directory. To save results
- `OUTPUT_RULE_MAKER_PATH` - Specifies the path where created rules will be saved.
- `OUTPUT_SNAKEMAKE_PATH` - Specifies the path where main Snakefile will be created.
- `CUSTOM_FUNCTIONS_PATH_LIST` - List of paths to the custom functions files to be imported.

**Combos**
- When `INPUT_DIR_PATH`, `OUTPUT_DIR_PATH`, `OUTPUT_RULE_MAKER_PATH`, `OUTPUT_SNAKEMAKE_PATH` are defined as relative paths, they will be merged with `APPLICATION_ROOT_PATH` path. Otherwise, they will be used as absolute paths. 


**Default settings.yaml**
```yaml
logger:
  info:
    path: logs/info.log
    level: INFO
  error:
    path: logs/error.log
    level: ERROR
  debug:
    path: logs/debug.log
    level: DEBUG
configuration_files:
  rule_configuration: <path>SnakeMaker/config/demo_rule_config.yaml
  snakefile_configuration: <path>SnakeMaker/config/demo_snakefile_config.yaml
app:
  APPLICATION_ROOT_PATH: default 
  FSLDIR: 
  INPUT_DIR_PATH: data/input_data
  OUTPUT_DIR_PATH: data/output_data/data
  OUTPUT_RULE_MAKER_PATH: data/output_data/rules
  OUTPUT_SNAKEMAKE_PATH: data/output_data
  CUSTOM_FUNCTIONS_PATH_LIST: 
    - <path>SnakeMaker/data/scripts/demo_functions.py
```