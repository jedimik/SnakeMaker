# Description: Denoise the input DWI data.
rule denoise_step1:
	input:
		b0="{output_path}/base/{sample}/b0.nii.gz",
		b1000="{output_path}/base/{sample}/b1000.nii.gz",
	output:
		b0_denoised="{output_path}/denoised/{sample}/b0_denoised.nii.gz",
		b1000_denoised="{output_path}/denoised/{sample}/b1000_denoised.nii.gz",
	shell:
		"""
			dwidenoise {input.b0} {output.b0_denoised}
			dwidenoise {input.b1000} {output.b1000_denoised}
		"""
# Description missing
rule deggibs_step1:
	input:
		b0_denoised="{output_path}/denoised/{sample}/b0_denoised.nii.gz",
		b1000_denoised="{output_path}/denoised/{sample}/b1000_denoised.nii.gz",
	output:
		b0_denoised_degibbs="{output_path}/degibbs/{sample}/b0_denoised_degibbs.nii.gz",
		b1000_denoised_degibbs="{output_path}/degibbs/{sample}/b1000_denoised_degibbs.nii.gz",
	shell:
		"""
			mrdegibbs {input.b0_denoised} {output.b0_denoised_degibbs}
			mrdegibbs {input.b1000_denoised} {output.b1000_denoised_degibbs}
		"""
# Description missing
rule topup_step1:
	input:
		b0_denoised_degibbs="{output_path}/degibbs/{sample}/b0_denoised_degibbs.nii.gz",
		b1000_denoised_degibbs="{output_path}/degibbs/{sample}/b1000_denoised_degibbs.nii.gz",
	output:
		roi_b0="{output_path}/topup/{sample}/roi_b0.nii.gz",
		roi_b1000="{output_path}/topup/{sample}/roi_b1000.nii.gz",
	shell:
		"""
			fslroi {input.b0_denoised_degibbs} {output.roi_b0} 0 1
			fslroi {input.b1000_denoised_degibbs} {output.roi_b1000} 0 1
		"""
# Description missing
rule topup_step2:
	input:
		roi_b0="{output_path}/topup/{sample}/roi_b0.nii.gz",
		roi_b1000="{output_path}/topup/{sample}/roi_b1000.nii.gz",
	output:
		b0_b1000_merged="{output_path}/topup/{sample}/b0_b1000.nii.gz",
	shell:
		"""
			fslmerge -t {output.b0_b1000_merged} {input.roi_b1000} {input.roi_b0}
		"""
# Description missing
rule topup_step3:
	input:
		b0_json="{output_path}/base/{sample}/b0.json",
	params:		
		b0_json=lambda wildcards: findTotalReadoutTime(f'{output_path}/base/{wildcards.sample}/b0.json'),
	output:
		acq_params="{output_path}/topup/{sample}/acq_params.txt",
	shell:
		"""
			echo "0 1 0 {params.b0_json}\n0 -1 0 {params.b0_json}" > {output.acq_params}
		"""
# Description missing
rule topup_step4:
	input:
		b0_b1000_merged="{output_path}/topup/{sample}/b0_b1000.nii.gz",
		acq_params="{output_path}/topup/{sample}/acq_params.txt",
	params:		
		topup_config="b02b0_1.cnf",
	output:
		b0_b1000_merged_topup="{output_path}/topup/{sample}/b0_b1000_topup.nii.gz",
		b0_b1000_merged_topup_field="{output_path}/topup/{sample}/b0_b1000_topup_fieldmap_Hz.nii.gz",
	shell:
		"""
			topup --imain={input.b0_b1000_merged} --datain={input.acq_params} --config={params.topup_config} --out={output.b0_b1000_merged_topup} -fout={output.b0_b1000_merged_topup_field}
		"""
# Description missing
rule topup_step5:
	input:
		b0_denoised_degibbs="{output_path}/degibbs/{sample}/b0_denoised_degibbs.nii.gz",
		acq_params="{output_path}/topup/{sample}/acq_params.txt",
		b0_b1000_merged_topup="{output_path}/topup/{sample}/b0_b1000_topup.nii.gz",
	params:		
		inindex="1",
		method="jac",
	output:
		b1000_topup_brain="{output_path}/topup/{sample}/b1000_brain.nii.gz",
	shell:
		"""
			applytopup --imain={input.b0_denoised_degibbs} --inindex={params.inindex} --datain={input.acq_params} --topup={input.b0_b1000_merged_topup} --method={params.method} --out={output.b1000_topup_brain}
		"""
# Description missing
rule eddy_step1:
	input:
		b1000_topup_brain="{output_path}/topup/{sample}/b1000_brain.nii.gz",
	output:
		b1000_1stVol="{output_path}/eddy/{sample}/b1000_1stVol.nii.gz",
	shell:
		"""
			fslroi {input.b1000_topup_brain} {output.b1000_1stVol} 0 1
		"""
# Description missing
rule eddy_step2:
	input:
		b1000_1stVol="{output_path}/eddy/{sample}/b1000_1stVol.nii.gz",
	params:		
		f="0.2",
	output:
		b1000_brain="{output_path}/eddy/{sample}/b1000_brain.nii.gz",
	shell:
		"""
			bet {input.b1000_1stVol} {output.b1000_brain} -m -f {params.f}
		"""
# Description missing
rule eddy_step3:
	input:
		b0_bvec="{output_path}/base/{sample}/b0.bvec",
	output:
		index_file="{output_path}/eddy/{sample}/index.txt",
	run:
		b0_bvec=create_index_file(input.b0_bvec)
# Description missing
rule eddy_step4:
	input:
		b1000_denoised_degibbs="{output_path}/degibbs/{sample}/b1000_denoised_degibbs.nii.gz",
		b1000_brain="{output_path}/eddy/{sample}/b1000_brain.nii.gz",
		index_file="{output_path}/eddy/{sample}/index.txt",
		acq_params="{output_path}/topup/{sample}/acq_params.txt",
		b1000_bvec="{output_path}/base/{sample}/b1000.bvec",
		b1000_bval="{output_path}/base/{sample}/b1000.bval",
		b0_b1000_merged_topup="{output_path}/topup/{sample}/b0_b1000_topup.nii.gz",
	params:		
		fwhm="0",
		flm="quadratic",
	output:
		b1000_eddy_unwarped="{output_path}/eddy/{sample}/b1000_eddy_unwarped.nii.gz",
		b1000_eddy_unwarped_rotated_bvecs="{output_path}/eddy/{sample}/b1000_eddy_unwarped.eddy_rotated_bvecs",
		b1000_eddy_unwarped_parameters="{output_path}/eddy/{sample}/b1000_eddy_unwarped.eddy_parameters",
	shell:
		"""
			eddy_cuda10.2 --imain={input.b1000_denoised_degibbs} --mask={input.b1000_brain} --index={input.index_file} --acqp={input.acq_params} --bvecs={input.b1000_bvec} --bvals={input.b1000_bval} --fwhm={params.fwhm} --topup={input.b0_b1000_merged_topup} --flm={params.flm} --out={output.b1000_eddy_unwarped} --cnr_maps --repol
		"""
