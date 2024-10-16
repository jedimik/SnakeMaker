#!/bin/bash

# Script, which will rename and move all files based on pattern

# """ # Example
# bash <path>/SnakeMaker_dev/scripts/move_rule0.sh \
# --input_b <path>/data/input_data/sub-BIOPD01/ses-1/dwi \
# --input_t1 <path>/data/input_data/sub-BIOPD01/ses-1/anat \
# --sample BIOPD01/1 \
# --b0 b0 \
# --b1000 b1000 \
# --t1 t1 \ 
# --output <path>/data/output_data/base
# """
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input_b)
      input_b="$2"
      shift 2
      ;;
    --input_t1)
      input_t1="$2"
      shift 2
      ;;
    --sample)
      sample="$2"
      shift 2
      ;;
    --b0)
      b0="$2"
      shift 2
      ;;
    --b1000)
      b1000="$2"
      shift 2
      ;;
    --t1)
      t1="$2"
      shift 2
      ;;
    --output)
      output="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# Create output folder for data
mkdir -p $output
# Move b0 and b1000 files
for file in "$input_b"/*; do    
    if [[ $file =~ [Bb][0] ]]; then    
        if [[ $file == *.nii.gz ]]; then 
            filename=$(basename "$file")
            new_name="b0.nii.gz"                        
        else
            filename=$(basename "$file")
            extension="${filename##*.}"
            new_name="b0.$extension"        
        fi
        echo "Copying $file to $output/$sample/$new_name"
        mkdir -p "$output/$sample"
        cp -R -p "$file" "$output/$sample/$new_name"
    elif [[ $file =~ [Bb]1000 ]]; then
        if [[ $file == *.nii.gz ]]; then 
            filename=$(basename "$file")
            new_name="b1000.nii.gz"                        
        else
            filename=$(basename "$file")
            extension="${filename##*.}"
            new_name="b1000.$extension"        
        fi
        echo "Copying $file to $output/$sample/$new_name"
        mkdir -p "$output/$sample"
        cp -R -p "$file" "$output/$sample/$new_name"
    
    fi
done
# move t1 files
for file in "$input_t1"/*; do
    if [[ $file =~ [Tt][1] ]]; then
        if [[ $file == *.nii.gz ]]; then
            filename=$(basename "$file")
            new_name="t1.nii.gz"
        else
            filename=$(basename "$file")
            extension="${filename##*.}"
            new_name="t1.$extension"
        fi
        echo "Copying $file to $output/$sample/$new_name"
        mkdir -p "$output/$sample"
        cp -R -p "$file" "$output/$sample/$new_name"
    fi
done


