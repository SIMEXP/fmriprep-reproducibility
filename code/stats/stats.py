import os
import glob
import re

def get_tasks(func_path):
  task="*"
  # Get tasks name
  list_tasks = []
  func_by_task = glob.glob(glob_func_path.format(sampling=sampling, dataset=dataset, ii=1, participant=participant, scan=scan, task="*"))
  for fpath in func_by_task:
      task = re.search(".*?task-(.*?)_space.*?", fpath)[1]
      if task:
          list_tasks += [task]

# For each task
for task in list_tasks:
    func_images = []
    func_masks = []
    for ii in range(n_samples):
        # filenames
        func_task = glob.glob(glob_func_path.format(sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan=scan, task=task))[0]
        glob_func_mask_path = glob.glob(glob_func_path.format(sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan=scan, task=task))[0]
        # mask loading
#         func_masks += [nib.load(mask_file).get_fdata().astype('bool')]
        # image loading
        nib_img = nib.load(func_task)
        func_images += [nib_img.get_fdata()[::5, ::5, ::5]]
#     func_masks = np.array(func_masks)
#     final_func_mask = np.array(np.prod(np.float32(func_masks), axis=0), dtype=np.bool)
    func_images = np.array(func_images)
    histogram(func_images, title=f"task-{task}")
    
#     parameters = dict(category="raw", participant=participant, dataset=dataset)
#     view_sig_dig(func_images, final_func_mask, affine, **parameters)

if __name__ == "__main__":
  input_dir = os.path.join(os.getcwd(), "..", "..", "outputs", "ieee")
  independent_anat_func = False
  exp_multithread = True #TODO: for debugging, to view actuall differences in the images
  exp_multiprocess = False
  n_samples = 5
  sampling = "ieee"
  dataset = "ds000256"
  participant = "sub-CTS201"
  output_template = "MNI152NLin2009cAsym"

  if independent_anat_func:
    input_dir = os.path.join(input_dir, "fmriprep_{dataset}_{ii}_{scan}", "fmriprep", "{participant}", "{scan}")
  elif exp_multithread:
      input_dir = os.path.join(input_dir, "fmriprep_{dataset}_{ii}_multithreaded", "fmriprep", "{participant}", "{scan}")
  elif exp_multiprocess:
      input_dir = os.path.join(input_dir, "fmriprep_{dataset}_{ii}_multiprocessed", "fmriprep", "{participant}", "{scan}")
  else:
      input_dir = os.path.join(input_dir, "fmriprep_{dataset}_{ii}", "fmriprep", "{participant}", "{scan}")

  glob_func_path = os.path.join(input_dir, "*_task-{task}_" + f"*{output_template}_desc-preproc_bold.nii.gz")