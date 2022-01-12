#!/usr/bin/python3

import os
import sys
import argparse
import re
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import stats.stats as stats
import utils.utils as utils
import data.get_data as get_data


def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description="", epilog="""
      Documentation at https://github.com/SIMEXP/fmriprep-reproducibility
      """)

    parser.add_argument(
        "-i", "--input_dir", required=False, default=".", help="Input data directory with ieee and/or fuzzy folders (default: install directory)",
    )

    parser.add_argument(
        "--exp-anat-func", action="store_true", required=False, help="Experiment with independent anatomical and functionnal workflow",
    )

    parser.add_argument(
        "--exp-multithread", action="store_true", required=False, help="Experiment with multithreading",
    )

    parser.add_argument(
        "--exp-multiprocess", action="store_true", required=False, help="Experiment with multiprocessing",
    )

    parser.add_argument(
        "--sampling", required=False, default="ieee", help="Sampling method between \"ieee\" or \"fuzzy\" (default: \"ieee\")",
    )

    parser.add_argument(
        "--template", required=False, default="MNI152NLin2009cAsym", help="fMRIprep template (default: \"MNI152NLin2009cAsym\")",
    )

    parser.add_argument(
        "--version", action="version", version=utils.get_version()
    )

    return parser.parse_args()


if __name__ == "__main__":
    #TODO: pixel wise comparison with fuzzy outputs (order testing or assume gaussian for confidence interval)
    #TODO: review file integrity check to (maybe) compare with fuzzy reference (first iteration of fuzzy for ex) ?
    # if outputs has more than 1 iteration, make reports (for us to be saved in inputs/reference/fuzzy/ieee)
    #TODO: rainplotclouds for pairwise differences visualization
    #TODO: mean and average images (just for anat)
    args = get_parser()
    print("\n### Running make-reports\n")
    print(vars(args))
    # reference path, where pre-generated output lives
    reference_dir = os.path.join(os.path.dirname(__file__), "..", "..", "inputs", "reference", "fmriprep", "fuzzy")
    # input path, where fmriprep experiments lives
    if args.input_dir == ".":
        input_dir = os.path.join(os.path.dirname(__file__),
                                  "..", "..", "outputs", args.sampling)
    else:
        input_dir = os.path.join(args.input_dir, args.sampling)
    if args.exp_multithread:
        experience_name = "_multithreaded"
    elif args.exp_multiprocess:
        experience_name = "_multiprocessed"
    elif args.exp_anat_func:
        experience_name = "_anat"
    else:
        experience_name = ""
    # get all experiment and reference input paths and dataset names
    experiments_path, dataset_names = get_data.get_dataset_list(input_dir, experience_name)
    references_path, _ = get_data.get_dataset_list(reference_dir, experience_name)
    # loop through each dataset and do the job
    for dataset_name in dataset_names:
        print(f"\t Processing {dataset_name}")
        # extract list of experiments for the given dataset, and related files
        fmriprep_outputs_path, output_iterations = get_data.get_experiment_paths(experiments_path, dataset_name)
        reference_outputs_path, reference_iterations = get_data.get_experiment_paths(references_path, dataset_name)
        #TODO take idx (fmriprep_outputs_path[0]) of output experiment in a loop of all output iterations
        bids_images, bids_masks = get_data.get_bids_files(fmriprep_outputs_path[0]) # assume same files layout for each exp iteration (`make test` to check file integrity)
        # iterate through all files
        for bids_image, bids_mask in zip(bids_images, bids_masks):
            stats.new_compute_task_statistics(bids_image, bids_mask, reference_iterations, reference_dir)


    # dataset_sub_task_dict = {}
    # for folder in sorted(os.listdir(input_path)):
    #     folder_path = os.path.join(input_path, folder)
    #     if os.path.isdir(folder_path):
    #         match_dataset_method = re.match("fmriprep_(.*)_1(.*)", folder)
    #         if match_dataset_method:
    #             if args.exp_multithread:
    #                 if not "multithreaded" in folder:
    #                     continue
    #             elif args.exp_multiprocess:
    #                 if not "multiprocessed" in folder:
    #                     continue
    #             elif args.exp_anat_func:
    #                 if not (("anat" in folder) | ("func" in folder)):
    #                     continue
    #             else:
    #                 if ("anat" in folder) | ("func" in folder) | ("multiprocessed" in folder) | ("multithreaded" in folder):
    #                     continue
    #             # get sub and task list
    #             list_tasks = utils.get_preproc_tasks(
    #                 dirpath=folder_path, template=args.template)
    #             list_tasks = list(set(list_tasks))
    #             list_subs = utils.get_preproc_sub(
    #                 dirpath=folder_path, template=args.template)
    #             list_subs = list(set(list_subs))
    #             dataset_name = match_dataset_method[1]
    #             dataset_sub_task_dict[dataset_name] = {
    #                 "subs": sorted(list_subs), "tasks": sorted(list_tasks)}
    # print(dataset_sub_task_dict)
    # for dataset in dataset_sub_task_dict.keys():
    #     for sub in dataset_sub_task_dict[dataset]['subs']:
    #         stats.compute_anat_statistics(
    #             fmriprep_output_dir=input_path
    #             , dataset=dataset
    #             , participant=sub
    #             , exp_anat_func=args.exp_anat_func
    #             , exp_multithread=args.exp_multithread
    #             , exp_multiprocess=args.exp_multiprocess
    #             , sampling=args.sampling
    #             , output_template=args.template)
    #         for task in dataset_sub_task_dict[dataset]['tasks']:
    #             stats.compute_task_statistics(
    #                 fmriprep_output_dir=input_path
    #                 , dataset=dataset
    #                 , participant=sub
    #                 , task=task
    #                 , exp_anat_func=args.exp_anat_func
    #                 , exp_multithread=args.exp_multithread
    #                 , exp_multiprocess=args.exp_multiprocess
    #                 , sampling=args.sampling
    #                 , output_template=args.template)
