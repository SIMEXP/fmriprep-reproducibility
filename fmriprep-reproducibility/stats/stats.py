import os
import glob
import re
import numpy as np
import nibabel as nib
import nilearn.plotting
import matplotlib.pyplot as plt
import pandas as pd
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import utils.utils as utils
import data.get_data as get_data

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def compute_mutual_mask(mask_paths):
    """Get mutually inclusive mask for each experiment iteration"""
    all_masks = []
    for mask_path in mask_paths:
        all_masks += [nib.load(mask_path).get_fdata().astype('float32')]
    all_masks = np.array(all_masks)
    mutual_mask = np.array(np.prod(all_masks, axis=0))

    return mutual_mask

def compute_anat_distribution_parameters(bids_image, bids_mask, iterations):
    """Compute anatomical distribution (mean and standard deviation)"""

    # match subpath to be replaced to iterate
    input_iteration = re.match(".*_(ds\d+_\d).*", bids_image.path)[1]
    images_path = []
    masks_path = []
    for ii in iterations:
        images_path += [bids_image.path.replace(input_iteration, input_iteration[:-1] + ii)]
        masks_path += [bids_mask.path.replace(input_iteration, input_iteration[:-1] + ii)]
    # compute mean and std images, this assumes same affine
    images = [nib.load(image_path).get_fdata().astype('float32') for image_path in images_path]
    mean_img = np.array(np.mean(images, axis=0))
    std_img = np.array(np.std(images, axis=0))
    # compute mutual mask, this assumes same affine
    mutual_mask = compute_mutual_mask(masks_path)

    return [mean_img, std_img], mutual_mask

def compute_parametric_stats(mean_img_path, mean_mask_path, std_img_path, test_img_path):
    '''Compute the gaussian parametric test between reference and test img.'''
    #TODO: code here the test we want to use

    #load and mask
    mean_img = nib.load(mean_img_path).get_fdata()
    mean_mask = nib.load(mean_mask_path).get_fdata().astype(np.bool)
    std_img = nib.load(std_img_path).get_fdata()
    test_img = nib.load(test_img_path).get_fdata()

    min_valid_pixels = 0.95*(len(test_img[mean_mask]))

    valid_voxels = np.sum(np.abs(test_img[mean_mask] - mean_img[mean_mask]) < 1.96*std_img[mean_mask])

    return valid_voxels > min_valid_pixels

def run_anat_test(parametric=True):
    '''Run anatomical tests for each dataset/subject'''

    ieee_output_dir = os.path.join(os.path.dirname(
        __file__), "..", "..", "outputs", "ieee")
    fuzzy_reference_dir = os.path.join(os.path.dirname(
        __file__), "..", "..", "inputs", "fmriprep-reproducibility-reference", "fuzzy")

    # get list of all datasets
    _, dataset_names = get_data.get_dataset_list(ieee_output_dir)
    # loop through each dataset and do the job
    for dataset_name in dataset_names:
        # for each iteration of current IEEE dataset output (usually just one iteration "_0")
        for curr_dataset in os.listdir(ieee_output_dir):
            if ((dataset_name in curr_dataset) & ("_0" in curr_dataset)):
                print(f"\t Processing {curr_dataset}")
                ieee_curr_path = os.path.join(ieee_output_dir, curr_dataset, "fmriprep")
                fuzzy_reference_mean_path = os.path.join(fuzzy_reference_dir, get_data.get_reference_dataset_path(fuzzy_reference_dir, dataset_name, "mean")[0], "fmriprep")
                fuzzy_reference_std_path = os.path.join(fuzzy_reference_dir, get_data.get_reference_dataset_path(fuzzy_reference_dir, dataset_name, "std")[0], "fmriprep")
                for sub in get_data.get_subjects(ieee_curr_path):
                # loop threw each subject within the dataset    
                    ref_mean_img_path, ref_mean_mask_path = get_data.get_bids_files(fuzzy_reference_mean_path, space="MNI152NLin2009cAsym", subject=sub)
                    ref_std_img_path, _ = get_data.get_bids_files(fuzzy_reference_std_path, space="MNI152NLin2009cAsym", subject=sub)
                    test_img_path, _ = get_data.get_bids_files(ieee_curr_path, space="MNI152NLin2009cAsym", subject=sub)
                    if parametric:
                        valid = compute_parametric_stats(mean_img_path=ref_mean_img_path[0].path, mean_mask_path=ref_mean_mask_path[0].path, std_img_path=ref_std_img_path[0].path, test_img_path=test_img_path[0].path)
                    else:
                        #TODO: non-parametric tests
                        pass
                    msg_result = f"{bcolors.BOLD}{bcolors.OKGREEN}PASS{bcolors.ENDC}" if valid else f"{bcolors.BOLD}{bcolors.FAIL}FAIL{bcolors.ENDC}"
                    print(f"\t\t" + os.path.basename(test_img_path[0].path) + " " + msg_result)

        # # assume same files layout for each exp iteration (`make test` to check file integrity)
        # bids_images, bids_masks = get_data.get_bids_files(
        #     fmriprep_outputs_path[0])
        # # iterate through all files
        # for bids_image, bids_mask in zip(bids_images, bids_masks):
        #     stats.new_compute_task_statistics(
        #         bids_image, bids_mask, reference_iterations, reference_dir)

if __name__ == "__main__":
    run_anat_test()
