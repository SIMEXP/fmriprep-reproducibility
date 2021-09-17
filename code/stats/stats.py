import os
import glob
import re
import numpy as np
import nibabel as nib

def get_tasks(func_path, sampling, dataset, participant):
  # Get tasks name
  list_tasks = []
  func_by_task = glob.glob(glob_func_path.format(sampling=sampling, dataset=dataset, ii=1, participant=participant, scan="func", task="*"))
  for fpath in func_by_task:
      task = re.search(".*?task-(.*?)_space.*?", fpath)[1]
      if task:
          list_tasks += [task]
  
  return list_tasks

def corr_test_restest(img_1, img_2):
  """Compute the normalized correlation voxel wise between test and re-test
    
  Parameters
  ----------
    img_1 : `np.array` of size [x, y, z, t]
      test fMRI image
    img_2 : `np.array` of size [x, y, z, t]
      re-test fMRI image
  Returns
  -------
    `np.array` of size [x, y, z] : preason correlation voxel wise
  """
  temporal_length = img_1.shape[-1]
  mean_1 = np.mean(img_1, axis=-1)[..., None] @ np.ones((1, 1, 1, temporal_length))
  mean_2 = np.mean(img_2, axis=-1)[..., None] @ np.ones((1, 1, 1, temporal_length))
  std_1 = np.std(img_1, axis=-1)[..., None] @ np.ones((1, 1, 1, temporal_length))
  std_2 = np.std(img_2, axis=-1)[..., None] @ np.ones((1, 1, 1, temporal_length))
  corr = (1/temporal_length) * np.sum(((img_1 - mean_1) * (img_2 - mean_2) + 1e-9) / ((std_1 * std_2) + 1e-9), axis=-1)

  return corr

# # For each task
# for task in list_tasks:
#     func_images = []
#     func_masks = []
#     for ii in range(n_samples):
#         # filenames
#         func_task = glob.glob(glob_func_path.format(sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan=scan, task=task))[0]
#         glob_func_mask_path = glob.glob(glob_func_path.format(sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan=scan, task=task))[0]
#         # mask loading
# #         func_masks += [nib.load(mask_file).get_fdata().astype('bool')]
#         # image loading
#         nib_img = nib.load(func_task)
#         func_images += [nib_img.get_fdata()[::5, ::5, ::5]]
# #     func_masks = np.array(func_masks)
# #     final_func_mask = np.array(np.prod(np.float32(func_masks), axis=0), dtype=np.bool)
#     func_images = np.array(func_images)
#     histogram(func_images, title=f"task-{task}")
    
# #     parameters = dict(category="raw", participant=participant, dataset=dataset)
# #     view_sig_dig(func_images, final_func_mask, affine, **parameters)

if __name__ == "__main__":
  input_dir = os.path.join(os.getcwd(), "outputs", "ieee")
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
  glob_mask_path = os.path.join(input_dir, f"*{output_template}_desc-brain_mask.nii.gz")

  for task in get_tasks(glob_func_path, sampling=sampling, dataset=dataset, participant=participant):
    func_images = []
    func_masks = []
    print(f"Starting task {task}")
    print(f"\t Reading fMRI and mask images...")
    for ii in range(n_samples):
      # paths definition
      func_path = glob.glob(glob_func_path.format(sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan="func", task=task))[0]
      mask_path = glob.glob(glob_mask_path.format(sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan="anat", task=task))[0]
      # mask and image loading
      func_masks += [nib.load(mask_path).get_fdata().astype('bool')]
      func_images += [nib.load(func_path).get_fdata()]
    func_masks = np.array(func_masks)
    final_func_mask = np.array(np.prod(np.float32(func_masks), axis=0), dtype=np.bool)
    print(f"\t Computing voxel-wise pearson correlations...")
    # compute pearson normalized correlation voxel-wise, for each combination of all iterations
    pearson_corr = np.zeros(func_images[0].shape[:-1])
    for ii in range(n_samples - 1):
      for jj in range(ii + 1, n_samples):
        print(f"\t\t {ii} - {jj}")
        pearson_corr += corr_test_restest(func_images[ii], func_images[jj])
    # mean pearson correlation accros each iteration
    pearson_corr /= (n_samples * (n_samples - 1)/2)