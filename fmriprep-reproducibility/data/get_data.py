import os
import re
import bids
import shutil


def get_dataset_list(input_dir, experience_name=""):
    '''Get all the dataset names and related absolute path'''
    list_experiment_path = [os.path.join(input_dir, dir) for dir in os.listdir(
        input_dir) if re.match(".*fmriprep_ds\d+_\d" + experience_name + "$", dir)]
    dataset_names = [re.match(".*fmriprep_(ds\d+)_.*", path)[1]
                     for path in list_experiment_path]
    dataset_names = sorted(list(set(list(dataset_names))))

    return list_experiment_path, dataset_names


def get_experiment_paths(list_experiment_path, dataset_name):
    '''Get the path and number of reproducibility experiments'''
    list_fmriprep_output = [
        path for path in list_experiment_path if dataset_name in path]
    iterations = [re.match(".*_ds\d+_(\d).*", folder)[1]
                  for folder in list_fmriprep_output]
    iterations = sorted(list(set(list(iterations))))

    return list_fmriprep_output, iterations


def get_bids_files(input_bids_dir, space="MNI152NLin2009cAsym", validate=False, save_cache=False, load_cache=False):
    '''Extract the mask, and imaging entities from the fmriprep output'''
    database_path = os.path.join(input_bids_dir, ".pybids_cache")
    if load_cache:
        layout = bids.BIDSLayout(input_bids_dir, validate=validate, database_path=database_path)
    else:
        layout = bids.BIDSLayout(input_bids_dir, validate=validate)
    layout.add_derivatives(input_bids_dir)
    if save_cache:
        if os.path.exists(database_path):
            shutil.rmtree(database_path)
        layout.save(database_path)

    bids_images = layout.get(scope="derivatives", space=space,
                             desc="preproc", suffix=["T1w", "bold"], extension="nii.gz")
    bids_masks = layout.get(scope="derivatives", space=space,
                            desc="brain", suffix="mask", extension="nii.gz")

    return  bids_images, bids_masks
