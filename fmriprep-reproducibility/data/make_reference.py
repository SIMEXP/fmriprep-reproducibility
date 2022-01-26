#!/usr/bin/python3
import os
import sys
import argparse
import shutil
import re
import json
import nibabel as nib
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import stats.stats as stats
import utils.utils as utils
import data.get_data as get_data

DATASET_DESCRIPTION = {
    "Name": "fMRIPrep reproducibility - fMRI PREProcessing reproducibility workflow",
    "BIDSVersion": "1.4.0",
    "DatasetType": "derivative",
    "GeneratedBy": [
        {
            "Name": "fmriprep-reproducibility",
            "Version": "{version}".format(version=utils.get_version()),
            "CodeURL": "https://github.com/SIMEXP/fmriprep-reproducibility/archive/{version}.tar.gz".format(version=utils.get_version())
        }
    ],
    "HowToAcknowledge": "Please cite our paper (<FMRIPREP-REPRO-PAPER-ID>), and include the generated citation boilerplate within the Methods section of the text.",
    "License": "Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0)"
}

def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description="", epilog="""
      Documentation at https://github.com/SIMEXP/fmriprep-reproducibility
      """)

    parser.add_argument(
        "-o", "--output-path", required=False, help="Reference output path (default: \"./outputs/<SAMPLING>/refeference\")",
    )

    parser.add_argument(
        "--sampling", required=False, default="fuzzy", help="Sampling method between \"fuzzy\" or \"ieee\" (default: \"fuzzy\")",
    )

    parser.add_argument(
        "--template", required=False, default="MNI152NLin2009cAsym", help="fMRIprep template (default: \"MNI152NLin2009cAsym\")",
    )

    parser.add_argument(
        "--version", action="version", version=utils.get_version()
    )

    return parser

def make_bids_dataset_from_distribution_parameters(mean_img, std_img, mutual_mask, image_path, mask_path, reference_subpath, template):

    methods = ["_anat_mean", "_anat_std"]
    subpath_to_replace = re.match("(.*)/fmriprep_ds.*", image_path)[1]
    iteration_to_replace = re.match(".*ds\d+(_\d[^/]*).*", image_path)[1] #match everything after _\d up to first "/"
    ref_image_path = image_path.replace(subpath_to_replace, reference_subpath)
    ref_mask_path = mask_path.replace(subpath_to_replace, reference_subpath)
    original_img = nib.load(image_path) #get img affine and header
    original_mask = nib.load(mask_path) #get mask affine and header
    # save mean/std image and mask
    for method in methods:
        if method == "_anat_mean":
            img = mean_img
        elif method == "_anat_std":
            img = std_img
        current_ref_image_path = ref_image_path.replace(iteration_to_replace, method)
        current_ref_mask_path = ref_mask_path.replace(iteration_to_replace, method)
        os.makedirs(os.path.dirname(current_ref_image_path), exist_ok=True)
        nib.save(nib.Nifti1Image(img, original_img.affine, original_img.header), current_ref_image_path)
        nib.save(nib.Nifti1Image(mutual_mask, original_mask.affine, original_mask.header), current_ref_mask_path)
        # copy json metadata files
        #TODO not sure how this impacts
        shutil.copy(image_path.replace(".nii.gz", ".json"), current_ref_image_path.replace(".nii.gz", ".json"))
        shutil.copy(mask_path.replace(".nii.gz", ".json"), current_ref_mask_path.replace(".nii.gz", ".json"))
        bids_dir = os.path.join(os.path.dirname(current_ref_image_path), "..", "..")
        with open(os.path.join(bids_dir, "dataset_description.json"), "w") as file:
            json.dump(DATASET_DESCRIPTION, file)
        get_data.get_bids_files(bids_dir, space=template, save_cache=True)

if __name__ == "__main__":
    print("\n### Running make-reference\n")
    args = get_parser().parse_args()
    sampling = args.sampling
    template = args.template
    if (args.output_path is None):
        output_ref_path = os.path.join(os.path.dirname(__file__), "..", "..", "outputs", sampling, "reference") 
    else:
        output_ref_path = args.output_path
    output_ref_path = os.path.join(output_ref_path, "fmriprep", sampling)
    if not os.path.exists(output_ref_path):
        os.makedirs(output_ref_path, exist_ok=True)
    # reference path, where pre-generated output lives
    input_dir = os.path.join(os.path.dirname(__file__), "..", "..", "outputs", sampling) 
    print(vars(args))

    # match if whole workflow with anat and func detected
    if not any(re.match(".*_\d+$", folder) for folder in os.listdir(input_dir)):
        raise ValueError("fmriprep standard anat/func workflow not detected!\n Independent workflow cannot be used as a reference!")
    # get all experiment and reference input paths and dataset names
    experiments_path, dataset_names = get_data.get_dataset_list(input_dir)
    # loop through each dataset
    for dataset_name in dataset_names:
        print(f"\t Processing {dataset_name}")
        # extract list of experiments for the given dataset, and related files
        fmriprep_outputs_path, output_iterations = get_data.get_experiment_paths(experiments_path, dataset_name)
        # loop through each dataset iteration to extract files and save bids database
        # assume same files layout for each exp iteration (`make test` to check file integrity)
        for fmriprep_output_path in fmriprep_outputs_path:
            print(f"\t\t Saving cache for {fmriprep_output_path}")
            bids_images, bids_masks = get_data.get_bids_files(os.path.join(fmriprep_output_path, "fmriprep"), space=template, save_cache=True)
            print(f"\t\t Copy to {output_ref_path}")
            # copy current raw exp output to reference folder
            fmriprep_reference_path = os.path.join(output_ref_path, os.path.basename(fmriprep_output_path))
            if os.path.exists(fmriprep_reference_path):
                shutil.rmtree(fmriprep_reference_path)
            shutil.copytree(fmriprep_output_path, fmriprep_reference_path)
        print(f"\t Generating mean and std...")
        # iterate through all files
        for bids_image, bids_mask in zip(bids_images, bids_masks):
            mean_std_image, mutual_mask = stats.compute_anat_distribution_parameters(bids_image, bids_mask, iterations=output_iterations)
            make_bids_dataset_from_distribution_parameters(mean_img=mean_std_image[0]
                                                          , std_img=mean_std_image[1]
                                                          , mutual_mask=mutual_mask
                                                          , image_path=bids_image.path
                                                          , mask_path=bids_mask.path
                                                          , reference_subpath=output_ref_path
                                                          , template=template)
