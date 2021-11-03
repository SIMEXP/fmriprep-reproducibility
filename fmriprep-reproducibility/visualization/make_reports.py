#!/usr/bin/python3

# import statistics.stats

import os
import sys
import argparse
import re
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import utils.utils as utils

def read(relative_path):
    """Read the curent file.
    Parameters
    ----------
        relative_path : string, required
            relative path to the file to be read, from the directory of this file

    Returns
    -------
        string : content of the file at relative path
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, relative_path), 'r') as fp:
        return fp.read()


def get_version():
    """Get the version of this software, as describe in the __init__.py file from the top module.

    Returns
    -------
        string : version of this software
    """
    init_filepath = os.path.join(os.path.join(os.path.dirname(__file__), ".."), "__init__.py")
    with open(init_filepath, "r") as f:
        for line in f.read().splitlines():
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
            else:
                raise RuntimeError("Unable to find version string.")


def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description="", epilog="""
            Documentation at https://github.com/SIMEXP/fmriprep-reproducibility
            """)

    parser.add_argument(
        "-i", "--input_dir", required=False, default=".", help="Input data directory (default: install directory)",
    )

    parser.add_argument(
        "--independent-anat-func", action="store_true", required=False, help="Experiment with independent anatomical and functionnal workflow",
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
        "--version", action="version", version=get_version()
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_parser()
    print("\n### Running make-reports\n")
    print(vars(args))

    # output_path
    if args.input_dir == ".":
        output_path = os.path.join(os.path.dirname(__file__),
                                   "..", "..", "outputs", args.sampling)
    else:
        output_path = os.path.join(args.input_dir, "outputs", args.sampling)
    # create dataset, participant id and task dict
    dataset_sub_task_dict = {}
    for folder in sorted(os.listdir(output_path)):
      folder_path = os.path.join(output_path, folder)
      if os.path.isdir(folder_path):
        match_dataset_method = re.match("fmriprep_(.*)_1(.*)", folder)
        if match_dataset_method:
            if args.exp_multithread:
                if not "multithreaded" in folder:
                    continue
            elif args.exp_multiprocess:
                if not "multiprocessed" in folder:
                    continue
            elif args.independent_anat_func:
                if not "func" in folder:
                    continue
            else:
              if ("func" in folder) | ("anat" in folder) | ("multiprocessed" in folder) | ( "multithreaded" in folder):
                  continue
            # get sub and task list
            list_tasks = utils.get_preproc_tasks(dirpath=folder_path, template=args.template)
            list_tasks = list(set(list_tasks))
            list_subs = utils.get_preproc_sub(dirpath=folder_path, template=args.template)
            list_subs = list(set(list_subs))
            dataset_name = match_dataset_method[1]
            dataset_sub_task_dict[dataset_name] = {"subs": list_subs, "tasks": list_tasks}
    print(dataset_sub_task_dict)
    # loop through all participants and all tasks
    # for participant in sub_task_dict.keys():
    # exp_matches_list = list(set(exp_matches))
    # print(exp_matches_list)
