import os
import glob
import re
import numpy as np
import nibabel as nib
import nilearn.plotting
import matplotlib.pyplot as plt

def get_mutual_mask(n_samples, glob_mask_path, sampling, dataset, participant, task):
  """Get mutually inclusive mask for each experiment iteration
    
  Parameters
  ----------
    n_samples: int
      number of experiment iteration
    glob_mask_path: str
      glob path to mask images
    sampling: str
      sampling method between ieee and fuzzy
    dataset: str
      datalad dataset to use
    participant: str
      participant id with format `sub-id`
  Returns
  -------
    `np.array` of `np.float32` and shape [x, y, z]: boolean mask image
  """
  func_masks= []

  for ii in range(n_samples):
    # paths definition
    mask_path = glob.glob(glob_mask_path.format(sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan="func", task=task))[0]
    # mask and image loading
    func_masks += [nib.load(mask_path).get_fdata().astype('float32')]
  func_masks = np.array(func_masks)
  final_func_mask = np.array(np.prod(func_masks, axis=0))

  return final_func_mask

def get_tasks(glob_func_path, sampling, dataset, participant):
  """Get task names from fmri filepath
    
  Parameters
  ----------
    glob_func_path: str
      glob path to functionnal images
    sampling: str
      sampling method between ieee and fuzzy
    dataset: str
      datalad dataset to use
    participant: str
      participant id with format `sub-id`
  Returns
  -------
    `list` of [`str`]: task names
  """
  # Get tasks name
  list_tasks = []
  func_by_task = glob.glob(glob_func_path.format(sampling=sampling, dataset=dataset, ii=1, participant=participant, scan="func", task="*"))
  for fpath in func_by_task:
      task = re.search(".*?task-(.*?)_space.*?", fpath)[1]
      if task:
          list_tasks += [task]
  
  return list_tasks

def corr_test_restest(img_1, img_2):
  """Compute the pearson correlation voxel wise between test and re-test
    
  Parameters
  ----------
    img_1: `np.array` of size [x, y, z, t]
      test fMRI image
    img_2: `np.array` of size [x, y, z, t]
      re-test fMRI image
  Returns
  -------
    `np.array` of `np.float32` and shape [x, y, z]: preason correlation voxel wise
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
  glob_mask_path = os.path.join(input_dir, "*_task-{task}_" + f"*{output_template}_desc-brain_mask.nii.gz")

  # statistics for functionnal images
  for task in get_tasks(glob_func_path, sampling=sampling, dataset=dataset, participant=participant):
    func_images = []
    func_masks = []
    print(f"Starting task {task}")
    print(f"\t Reading mask images...")
    mask_img = get_mutual_mask(n_samples, glob_mask_path, sampling=sampling, dataset=dataset, participant=participant, task=task)
    print(f"\t Reading fMRI images...")
    for ii in range(n_samples):
      # paths definition
      func_path = glob.glob(glob_func_path.format(sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan="func", task=task))[0]
      # mask and image loading
      func_images += [nib.load(func_path).get_fdata()]
      affine = nib.load(func_path).affine
    print(f"\t Computing voxel-wise pearson correlations...")
    # compute pearson normalized correlation voxel-wise, for each combination of all iterations
    pearson_corr = np.zeros(func_images[0].shape[:-1])
    for ii in range(n_samples - 1):
      for jj in range(ii + 1, n_samples):
        print(f"\t\t {ii} - {jj}")
        pearson_corr += corr_test_restest(func_images[ii], func_images[jj])
    # mean pearson correlation accros each iteration combination
    pearson_corr /= (n_samples * (n_samples - 1)/2)
    # masking
    pearson_corr = pearson_corr * mask_img
    # saving html view
    nib_pearson = nib.Nifti1Image((1-pearson_corr) * mask_img, affine)
    bg_img = nib.Nifti1Image(func_images[0][..., 0], affine)
    html = nilearn.plotting.view_img(
      nib_pearson, title=f"{participant} for {task}"
      , black_bg=True
      , vmin=0.
      , vmax=1.
      , symmetric_cmap=False
      , threshold=1e-2
      , cut_coords=(0., 0., 0.)
      , bg_img=bg_img)
    html.save_as_html(f"{sampling}_{dataset}_{participant}_{task}_differences.html")
    pearson_values = pearson_corr.flatten()
    pearson_values = pearson_values[pearson_values > 0]
    fig, axes = plt.subplots(nrows=1, ncols=1)
    axes.hist(pearson_values, bins=100)
    axes.set_title("Pearson correlation")
    fig.savefig(f"{sampling}_{dataset}_{participant}_{task}_pearson.png")