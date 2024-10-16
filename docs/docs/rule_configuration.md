# Rule configuration
> Rule configuration file is a YAML or JSON file that contains all the necessary information for the SnakeMaker to create rules. It contains information about the input and output files, the shell command or run command. The rule configuration file is used to define the rules that will be used to run the workflow.

## File register
> SnakeMaker contains a feature which will register all the files that are in input/output section of the rules. This is used to make the workflow more readable and to make it easier to define next the rules without redundancy.

## Rule0
>  You can define rule0 which will be executed right after Snakemaker will finish creating complete workflow and starting scripts. You can define the path to the script or function name, which will be called from the custom functions file.
```yaml
rule0:
 - base: # rule name
    path:  # If there is defined script without input arguments
    function_name: move_rule0 # if special function is needed
```
## Structure:
> You can define inputs, outputs, parameters, shell or run command and description for the rules.


### Input:
> Input is a place to define all input files, which can be defined with the absolute path or with specific functions.
> After specifying the input keyword you can define the input files, their path, or function how to obtain them.
> Structure of the input can be:
```yaml
    ...
  denoise_step1:
    input:
      b0:
        path: ''
        function: 
          name: base_input_dir
        folder: base
        filename: b0.nii.gz
      b1000:
        path: ''
        function: 
          name: base_input_dir
        folder: base
        filename: b1000.nii.gz
```
> If you are working with file, which was generated previously in the workflow, you can use the registered files feature, which means, you can define the file only by the key (name) of the input/output of previous rules. Like example below:
```yaml
    ...
    # Previous rule output
  denoise_step1:
   ...
    output:
      b0_denoised:
        output_name: b0_denoised.nii.gz
        output_folder: denoised
      b1000_denoised:
        output_name: b1000_denoised.nii.gz
        output_folder: denoised
    # Current rule input
  deggibs_step1:
    input:
      b0_denoised: # it will assign the path of the denoise_step1 output b0_denoised
      b1000_denoised:  # it will assign the path of the denoise_step1 output b1000_denoised
    output:
    ...
```
### Params:
> Params are used to define the parameters for the rule. It can be used for the shell command or run command.
> Params can hold multiple type of values, like string, integer, float
> In Params you can use custom functions, which are defined in the custom functions file. (more info at [Configuration](configuration.md) and in the [Functions](#functions) section)
```yaml
    ...
  denoise_step1:
    ...
    params:
      readout_value:      
        function:
          name: findTotalReadoutTime
          args:
            from_input:
              b0_json:
                name: b0_json
```yaml
    ...
  denoise_step1:
    ...
    params:
      b0_json:
        name: b0_json
        function:
          name: get_json
          args:
            from_input: 
              b0:
                name: b0
      b1000_json:
        name: b1000_json
        function:
          name: get_json
          args:
            from_input: 
              b1000:
                name: b1000
```
### Output:
> Output is a place to define all output files, which can be defined with the absolute path or with specific functions.
> After specifying the output keyword you can define the output folder and expected output name.
> Structure of the output can be:
```yaml
    ...
  denoise_step1:
    ...
    output:
      b0_denoised:
        output_name: b0_denoised.nii.gz
        output_folder: denoised
      b1000_denoised:
        output_name: b1000_denoised.nii.gz
        output_folder: denoised
```

### Shell:
> Shell is a place to define the shell command, which will be executed in the rule.
> After specifying the shell keyword you can define the shell command as a string, or list of strings.
> Structure of the shell can be:
```yaml
    ...
  denoise_step1:
    ...
    shell:
      - mrdegibbs {input.b0_denoised} {output.b0_denoised_degibbs}
      - mrdegibbs {input.b1000_denoised} {output.b1000_denoised_degibbs}
```
### Run:
> Run is a place to define the run command, which will be executed
> After specifying the run keyword you can define the run command as function which will be called from the custom functions file.

```yaml
    ...
    run:
      function: 
        name: create_index_file
        args:
          from_input:
            b0_bvec:
              name: b0_bvec
```

### Functions
> You can define functions that will be used to generate the input files paths. This is usable when you want to run the processing for number of samples and make your workflow more generall.
> Structure of the function can be:

- Defining built-in functions like `base_input_dir` - this function is used to define files from the input directory. Mostly used for the first rule. 
```yaml
    ...
    function:
      name: <function_name>
```
- Defining function with parameters - this is used when you want to define more complex functions and pass variables. In case below you can use registered files, which were in the previous rules defined. Only need to specify args as *from_input*
```yaml
    ...
    function:
      name: <function_name>
      args:
        from_input: 
          b0_json:
            name: b0_json
```
- Example of function called from the custom functions file:
```yaml
    ...
    params:
      readout_value:      
        function:
          name: findTotalReadoutTime
          args:
            from_input:
              b0_json:
                name: b0_json
```
**Which will create**
```python
params:
    readout_value=lambda wildcards: findTotalReadoutTime(f'{output_path}/base/{wildcards.sample}/b0.json'),
```
