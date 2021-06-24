# import unittest
import pytest
import os
import re
if __name__ == '__main__':
    import utils
else:
    from . import utils

DIRPATH = os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "ieee")
LIST_FOLDERS = os.listdir(DIRPATH)
exp_matches = []
# create match pattern from folders list
for folder in LIST_FOLDERS:
  match_dataset_method = re.match("(.*)_[0-9]+_(.*)", folder)
  if match_dataset_method:
    exp_matches += [match_dataset_method[1] + "_[0-9]+_" + match_dataset_method[2] + "$"]
  else:
    match_dataset_method = re.match("(.*)_[0-9]+", folder)
    if match_dataset_method:
      exp_matches += [match_dataset_method[1] + "_[0-9]+$"]
EXPERIMENT_MATCHES = list(set(exp_matches))

def file_integrity_check(experiment_matches, preproc_match):
  # start the file integrity check
  for exp_match in experiment_matches:
    print("# {}".format(exp_match))
    print("\t{}".format(preproc_match))
    # get all preprocessed file from the current folders (same dataset, subject and method, but any iteration)
    # to avoid checking large content of files, we restric to fmriprep output folder
    curr_matching_exps = sorted([folder for folder in LIST_FOLDERS if re.match(exp_match, folder)])
    list_preproc = [utils.get_preproc_list(dirpath=os.path.join(DIRPATH, curr_exp, "fmriprep"), pattern=preproc_match) for curr_exp in curr_matching_exps]
    if not all(list_preproc):
      raise ValueError("No preprocessing files found for {}!".format(preproc_match))
    num_experiments = len(list_preproc)
    num_preproc = len(list_preproc[0])
     # check if preproc gzip footer (CRC-32) matches for each experiment
    for ii in range(num_preproc):
      preproc_first = list_preproc[0][ii]
      preproc_first_name = os.path.basename(preproc_first)
      print("\t\t{}".format(preproc_first_name))
      footer = utils.gzip_footer(preproc_first)
      for jj in range(1, num_experiments):
        if not any(preproc_first_name in s for s in list_preproc[jj]):
          raise NameError("{} not found for iter #{} of experiment {}!".format(preproc_first_name, jj+1, exp_match))
        preproc_iter = list_preproc[jj][ii]
        preproc_iter_name = os.path.basename(preproc_iter)
        if not (preproc_first_name == preproc_iter_name):
          raise NameError("Check file naming for {}!".format(preproc_iter_name))
        curr_footer = utils.gzip_footer(preproc_iter)
        assert curr_footer == footer

def test_experiments_exists():
  assert len(EXPERIMENT_MATCHES) != 0

#TODO put here the final list of datasets and subjects to test
@pytest.mark.parametrize(
  "dataset_name,subject_id"
  , [("ds000256", "CTS201")
     , ("ds000256", "CTS201")])
def test_dataset_subject(dataset_name, subject_id):
  filtered_exp_matches = []
  for exp_match in EXPERIMENT_MATCHES:
    if "[0-9]+$" in exp_match: # check that the current exp match ends with an integer (default repro experiment)
      filtered_exp_matches += [exp_match]
  if not filtered_exp_matches:
    raise ValueError("No default IEEE experiment found!")
  preproc_match = ".*{}.*sub-{}.*".format(dataset_name, subject_id)
  preproc_match = preproc_match + "space-MNI152NLin2009cAsym_desc-preproc.*\\.nii\\.gz"
  file_integrity_check(experiment_matches=filtered_exp_matches, preproc_match=preproc_match)

def test_multiprocess():
  pass

def test_multithread():
  pass

def test_other_experiments():
  filtered_exp_matches = []
  for exp_match in EXPERIMENT_MATCHES:
    if ("[0-9]+$" not in exp_match) \
      & ("multi" not in exp_match) \
      & ("func" not in exp_match) \
      & ("anat" not in exp_match):
      filtered_exp_matches += [exp_match]
  if filtered_exp_matches:
    file_integrity_check(experiment_matches=filtered_exp_matches, preproc_match="space-MNI152NLin2009cAsym_desc-preproc.*\\.nii\\.gz")

if __name__ == "__main__":
  test_experiments_exists()
  test_dataset_subject("ds000256", "CTS210")