# Rules

- rule file keys:
    - rule_0:dict, with keys = "name", "script_file_path", "args", 

## Rules definition conventions
- input:
    - name : dict
        - path
        - function : specific function to assign the input file with args in it, if are some. Example mzfunction(smt,smt2)
        - folder must be provded with filename. Its relative path to the INPUT_DIR_PATH
        - filename must be provided with input_folder. Contains also an extension. Cannot be used with sample wildcard
    Combos:
        - function: base_input_dir - driven by sample 
         can be in combo with folder. or function can be defined as :
        function:
          name: findTotalReadoutTime
          args:
            b0_json:
              path: ''
              function: base_input_dir
              folder: base
              filename: b0.json
        or function_name:
            args:
              - something
              - something

    That means, its after rule0 if exists.

- params:
    - name : dict
        - path : to file
        - function:
          - function_name: name of the function which is from imported functions
          - input args: named args for the function
          - input

    params:
      readout_value:
        function:
          name: findTotalReadoutTime
          args:
            input_files:
              b0_json:
                path: ''
                function: 
                  name: base_input_dir
                folder: base
                filename: b0.json
      test_value:
        function:
          name: findTotalReadoutTime
          args:
            from_input:
              test_json:
                name: b0_json

- output:


    run:
      function: 
        name: create_index_file
        args:
          from_input:
            b0_bvec:
              name: b0_bvec

              Now only based on the inputs. no diff args Fix soon
# Wildcards

## Sample wildcard
> default wildcards
## other wildcards
> can be defined in the file_name
        