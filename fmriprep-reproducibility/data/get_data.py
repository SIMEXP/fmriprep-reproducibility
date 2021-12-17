import os
import re
import bids


def get_dataset_list(input_dir, experience_name):
    '''Get all the dataset names and related absolute path'''
    list_experiment_path = [os.path.join(input_dir, dir) for dir in os.listdir(
        input_dir) if experience_name in dir]
    dataset_names = [re.match(".*fmriprep_(ds\d+)_.*", path)[1]
                     for path in list_experiment_path]
    dataset_names = list(set(list(dataset_names)))

    return list_experiment_path, dataset_names


def get_experiment_paths(list_experiment_path, dataset_name):
    '''Get the path and number of reproducibility experiments'''
    list_fmriprep_output = [
        path for path in list_experiment_path if dataset_name in path]
    iterations = [re.match(".*_(\d)_.*", folder)[1]
                  for folder in list_fmriprep_output]
    iterations = list(set(list(iterations)))

    return list_fmriprep_output, iterations


def get_bids_files(input_path, space="MNI152NLin2009cAsym"):
    '''Extract the mask, and imaging entities from the fmriprep output'''

    bids_dir = os.path.join(input_path, "fmriprep")
    layout = bids.BIDSLayout(bids_dir, validate=False)
    layout.add_derivatives(bids_dir)

    bids_images = layout.get(scope="derivatives", space=space,
                             desc="preproc", suffix=["T1w", "bold"], extension="nii.gz")
    bids_masks = layout.get(scope="derivatives", space=space,
                            desc="brain", suffix="mask", extension="nii.gz")

    return  bids_images, bids_masks
