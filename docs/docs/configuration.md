## Env variables
- Option 1 - define a full path
- Option 2 - define a relative path - not starting with `/`  on the start, and it will be automatically merged in to the root path of the project


- Docker specific paths and envs 
Types of variables:
    - APPLICATION_ROOT_PATH - Specifies the root path of the application. 
    Options: default - which means project settings, by_output - which is driven by output_dir_path. When default other Output section is relative into application root path
     But there need to be OUTPUT_DIR_PATH as absolute path
    - INPUT_DIR_PATH - Specifies the path to the input directory

Output_section:
    - OUTPUT_DIR_PATH - Specifies the path to the output directory
    - OUTPUT_RULE_MAKER_PATH - Specifies the path to the rule maker file
    - OUTPUT_SNAKEMAKE_PATH - Specifies the path to the snakemake file

Custom_section:
    - CUSTOM_FUNCTIONS_PATH_LIST - must be provided fullpaths
    - CUSTOM_RULES_PATH_LIST #TODO: ADD / provided fullpath NOT IMPLEMENTED YET
    - CUSTOM_SNAKEMAKE_PATH_LIST #TODO: ADD - provided fullpath NOT IMPLEMENTED YET, for import script files
    - FSLDRI etc...

Other_section:
