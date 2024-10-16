

#Includes


include: '<path>SnakeMaker/data/scripts/demo_functions.py'
include: '<path>SnakeMaker/data/output_data/rules/rules.smk'

#Variables
samples = ['sub-BIOPD01/ses-1']
input_path = '<path>SnakeMaker/data/input_data'
output_path = '<path>SnakeMaker/data/output_data/data'


#Wildcard constraints
wildcard_constraints:
	sample = '|'.join([re.escape(x) for x in samples])


#Config variables
sides = ["sides"]


#Rules
rule all:
	input:
		expand('{output_path}/eddy/{sample}/b1000_eddy_unwarped.nii.gz', sample=samples, output_path=output_path)

