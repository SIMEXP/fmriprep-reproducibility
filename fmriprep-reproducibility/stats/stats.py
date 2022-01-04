import os
import glob
import re
import numpy as np
import nibabel as nib
import nilearn.plotting
import matplotlib.pyplot as plt
import pandas as pd

def compute_mutual_mask(mask_paths):
    """Get mutually inclusive mask for each experiment iteration"""
    all_masks = []
    for mask_path in mask_paths:
        all_masks += [nib.load(mask_path).get_fdata().astype('float32')]
    all_masks = np.array(all_masks)
    mutual_mask = np.array(np.prod(all_masks, axis=0))

    return mutual_mask

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
    func_masks = []

    for ii in range(n_samples):
        # paths definition
        mask_path = glob.glob(glob_mask_path.format(
            sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan="func", task=task))[0]
        # mask and image loading
        func_masks += [nib.load(mask_path).get_fdata().astype('float32')]
    func_masks = np.array(func_masks)
    final_func_mask = np.array(np.prod(func_masks, axis=0))

    return final_func_mask

def get_mutual_anat_mask(n_samples, glob_mask_path, sampling, dataset, participant, task="*"):
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
    anat_masks = []

    for ii in range(n_samples):
        # paths definition
        mask_path = glob.glob(glob_mask_path.format(
            sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan="anat"))[0]
        # mask and image loading
        anat_masks += [nib.load(mask_path).get_fdata().astype('float32')]
    anat_masks = np.array(anat_masks)
    final_anat_mask = np.array(np.prod(anat_masks, axis=0))

    return final_anat_mask


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
    func_by_task = glob.glob(glob_func_path.format(
        sampling=sampling, dataset=dataset, ii=1, participant=participant, scan="func", task="*"))
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
    mean_1 = np.mean(img_1, axis=-1)[...,
                                     None] @ np.ones((1, 1, 1, temporal_length))
    mean_2 = np.mean(img_2, axis=-1)[...,
                                     None] @ np.ones((1, 1, 1, temporal_length))
    std_1 = np.std(img_1, axis=-1)[...,
                                   None] @ np.ones((1, 1, 1, temporal_length))
    std_2 = np.std(img_2, axis=-1)[...,
                                   None] @ np.ones((1, 1, 1, temporal_length))
    corr = (1/temporal_length) * np.sum(((img_1 - mean_1) *
                                         (img_2 - mean_2) + 1e-9) / ((std_1 * std_2) + 1e-9), axis=-1)

    return corr

def plot_stats(inv_pearson_img, samples, bg_img, sampling, dataset, participant, task="", anat=False):
    """Save difference image and histogram"""
    figure_dir = os.path.join(os.path.join(os.path.dirname(__file__), "..", "..", "reports", "figures", sampling, dataset, participant))
    if not os.path.isdir(figure_dir):
      os.makedirs(figure_dir)
    if anat:
        task = "anat"
    name = f"{sampling}_{dataset}_{participant}_{task}"
    diff_img_path = os.path.join(figure_dir, name + "_differences.html")
    hist_path = os.path.join(figure_dir, name + "_distribution.png")
    output_stats_filepath = os.path.join(figure_dir, name + "_stats.csv")
    output_samples_filepath = os.path.join(figure_dir, name + "_distribution_samples.npz")
    # nilearn plot
    threshold = 1e-2
    vmax = 1
    if anat:
        threshold = 10
        vmax = None
    html = nilearn.plotting.view_img(
        inv_pearson_img
        , title=f"{participant} for {task}"
        , black_bg=True
        , threshold=threshold
        , vmax=vmax
        , symmetric_cmap=False
        , cmap = "jet"
        , cut_coords=(0., 0., 0.)
        , bg_img=bg_img)
    html.save_as_html(diff_img_path)
    # histogram
    fig, axes = plt.subplots(nrows=1, ncols=1)
    axes.hist(samples, bins=100)
    if anat:
        axes.set_title("Mean raw differences")
    else:
        axes.set_title("Pearson correlation")
    fig.savefig(hist_path)
    # descriptive statistics
    stats_table = descriptive_statistics(samples, name=name)
    stats_table.to_csv(output_stats_filepath, index=False)
    print(stats_table)
    # distribution samples
    np.savez(output_samples_filepath, samples)

def descriptive_statistics(samples, name=""):
    '''Compute the mean, std and quantile from samples.'''
    descriptive_stats = pd.DataFrame(
        columns=['name', 'n_samples', 'mean', 'std', 'q_0.01', 'q_0.05', 'q_0.95', 'q_0.99'])

    desc = {'name': name,
            'n_samples': [len(samples)],
            'mean': [np.mean(samples)],
            'std': [np.std(samples)],
            'q_0.01': [np.quantile(samples, q=0.01)],
            'q_0.05': [np.quantile(samples, q=0.05)],
            'q_0.95': [np.quantile(samples, q=0.95)],
            'q_0.99': [np.quantile(samples, q=0.99)]}
    descriptive_stats = descriptive_stats.append(pd.DataFrame(desc))

    return descriptive_stats

def new_compute_task_statistics(bids_image, bids_mask, iterations):

    # functionnal and anat have different results
    is_func = True
    if bids_image.entities['datatype'] == "anat":
        is_func = False
        # differences
    # get images and mask path for each experiment iteration
    iteration_match = re.match(".*(_\d_).*", bids_mask.path)[1]
    images_path = [bids_image.path.replace(iteration_match, f"_{ii}_") for ii in iterations]
    masks_path = [bids_mask.path.replace(iteration_match, f"_{ii}_") for ii in iterations]
    # compute mutual mask, this assumes same affine
    mutual_mask = compute_mutual_mask(masks_path)
    # for image_path in images_path:
    #   # pearson voxel-wise correlation
    #   # if is_func:
      
    #   # raw pixel differences
    #   if not is_func:
    #     # mask and image loading
    #     anat_images += [nib.load(anat_path).get_fdata()]
    #     affine = nib.load(anat_path).affine
    #     print(f"\t Computing voxel-wise differences...")
    #     # compute voxel-wise differences, for each combination of all iterations
    #     diff = np.zeros(anat_images[0].shape)
    #     for ii in range(n_samples - 1):
    #         for jj in range(ii + 1, n_samples):
    #             print(f"\t\t {ii} - {jj}")
    #             diff += np.abs(anat_images[ii] - anat_images[jj])
    #     # mean pearson correlation accros each iteration combination
    #     diff /= (n_samples * (n_samples - 1)/2)
    #     # saving stats images
    #     print(f"\t Saving figures...")
    #     diff_values = diff.flatten()
    #     masked_diff = diff * mask_img # masking raw differences
    #     inv_diff_img = nib.Nifti1Image(masked_diff, affine)
    #     bg_img = nib.Nifti1Image(anat_images[0], affine)
    #     plot_stats(inv_diff_img, diff_values, bg_img, sampling, dataset, participant, anat=True)



def compute_task_statistics(
    fmriprep_output_dir
    , dataset
    , participant
    , task
    , exp_anat_func=False
    , exp_multithread=False
    , exp_multiprocess=False
    , n_samples=5
    , sampling="ieee"
    , output_template="MNI152NLin2009cAsym"):
    """Compute fmri statistics using pearson correlation voxel wise

    Parameters
    ----------
      fmriprep_output_dir: str
        output directory for fmriprep
      dataset: str
        dataset name
      participant: str
        full BIDS participant name
      task: str
        task name
      exp_anat_func: bool
        independent anatomical and functionnal workflow
      exp_multithread: bool
        multithreaded workflow enabled
      exp_multiprocess: bool
        multitprocessed workflow enabled
      n_samples: int
        number of sample for the reproducibility experiments
      sampling: str
        sampling method used
      output_template: str
        name of the TemplateFlow template used by fmriprep
    """
    # TODO: use fmriprep BIDS derivative output to go through all the files: 
    # https://github.com/ccna-biomarkers/ccna_qc/blob/31d2fdd356d93d887c5ac24a8d7674521e233a1a/src/features/build_features.py#L172-L176
    # TODO: for debugging, to actually view some differences in the images
    # exp_multithread = True

    if exp_anat_func:
        fmriprep_output_dir = os.path.join(
            fmriprep_output_dir, "fmriprep_{dataset}_{ii}_{scan}", "fmriprep", "{participant}", "{scan}")
    elif exp_multithread:
        fmriprep_output_dir = os.path.join(
            fmriprep_output_dir, "fmriprep_{dataset}_{ii}_multithreaded", "fmriprep", "{participant}", "{scan}")
    elif exp_multiprocess:
        fmriprep_output_dir = os.path.join(
            fmriprep_output_dir, "fmriprep_{dataset}_{ii}_multiprocessed", "fmriprep", "{participant}", "{scan}")
    else:
        fmriprep_output_dir = os.path.join(
            fmriprep_output_dir, "fmriprep_{dataset}_{ii}", "fmriprep", "{participant}", "{scan}")

    glob_func_path = os.path.join(
        fmriprep_output_dir, "*_task-{task}_" + f"*{output_template}_desc-preproc_bold.nii.gz")
    glob_mask_path = os.path.join(
        fmriprep_output_dir, "*_task-{task}_" + f"*{output_template}_desc-brain_mask.nii.gz")

    # statistics for functionnal images
    func_images = []
    print(f"Starting func {participant} from {dataset} with task {task}")
    print(f"\t Reading mask and fMRI images...")
    mask_img = get_mutual_mask(n_samples, glob_mask_path, sampling=sampling,
                                dataset=dataset, participant=participant, task=task)
    for ii in range(n_samples):
        # paths definition
        func_path = glob.glob(glob_func_path.format(
            sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan="func", task=task))[0]
        # mask and image loading
        func_images += [nib.load(func_path).get_fdata()]
        affine = nib.load(func_path).affine
    print(f"\t Computing voxel-wise pearson correlations...")
    # compute pearson normalized correlation voxel-wise, for each combination of all iterations
    pearson_corr = np.zeros(func_images[0].shape[:-1])
    for ii in range(n_samples - 1):
        for jj in range(ii + 1, n_samples):
            print(f"\t\t {ii} - {jj}")
            pearson_corr += corr_test_restest(
                func_images[ii], func_images[jj])
    # mean pearson correlation accros each iteration combination
    pearson_corr /= (n_samples * (n_samples - 1)/2)
    # saving stats images
    print(f"\t Saving figures...")
    pearson_values = pearson_corr.flatten()
    inv_pearson_corr = (1 - pearson_corr) * mask_img # invert perason to be able to threshold
    inv_pearson_img = nib.Nifti1Image(inv_pearson_corr, affine)
    bg_img = nib.Nifti1Image(func_images[0][..., 0], affine)
    plot_stats(inv_pearson_img, pearson_values, bg_img, sampling, dataset, participant, task)


def compute_anat_statistics(
    fmriprep_output_dir
    , dataset
    , participant
    , exp_anat_func=False
    , exp_multithread=False
    , exp_multiprocess=False
    , n_samples=5
    , sampling="ieee"
    , output_template="MNI152NLin2009cAsym"):
    """Compute anatomical statistics using voxel wise difference

    Parameters
    ----------
      fmriprep_output_dir: str
        output directory for fmriprep
      dataset: str
        dataset name
      participant: str
        full BIDS participant name
      exp_anat_func: bool
        independent anatomical and functionnal workflow
      exp_multithread: bool
        multithreaded workflow enabled
      exp_multiprocess: bool
        multitprocessed workflow enabled
      n_samples: int
        number of sample for the reproducibility experiments
      sampling: str
        sampling method used
      output_template: str
        name of the TemplateFlow template used by fmriprep
    """

    if exp_anat_func:
        fmriprep_output_dir = os.path.join(
            fmriprep_output_dir, "fmriprep_{dataset}_{ii}_{scan}", "fmriprep", "{participant}", "{scan}")
    elif exp_multithread:
        fmriprep_output_dir = os.path.join(
            fmriprep_output_dir, "fmriprep_{dataset}_{ii}_multithreaded", "fmriprep", "{participant}", "{scan}")
    elif exp_multiprocess:
        fmriprep_output_dir = os.path.join(
            fmriprep_output_dir, "fmriprep_{dataset}_{ii}_multiprocessed", "fmriprep", "{participant}", "{scan}")
    else:
        fmriprep_output_dir = os.path.join(
            fmriprep_output_dir, "fmriprep_{dataset}_{ii}", "fmriprep", "{participant}", "{scan}")

    glob_anat_path = os.path.join(
        fmriprep_output_dir, f"*{output_template}_desc-preproc_T1w.nii.gz")
    glob_mask_path = os.path.join(
        fmriprep_output_dir, f"*{output_template}_desc-brain_mask.nii.gz")

    # statistics for anat images
    anat_images = []
    print(f"Starting anat {participant} from {dataset}")
    print(f"\t Reading mask and anat images...")
    mask_img = get_mutual_anat_mask(n_samples, glob_mask_path, sampling=sampling,
                                    dataset=dataset, participant=participant)
    for ii in range(n_samples):
        # paths definition
        anat_path = glob.glob(glob_anat_path.format(
            sampling=sampling, dataset=dataset, ii=ii+1, participant=participant, scan="anat"))[0]
        # mask and image loading
        anat_images += [nib.load(anat_path).get_fdata()]
        affine = nib.load(anat_path).affine
    print(f"\t Computing voxel-wise differences...")
    # compute voxel-wise differences, for each combination of all iterations
    diff = np.zeros(anat_images[0].shape)
    for ii in range(n_samples - 1):
        for jj in range(ii + 1, n_samples):
            print(f"\t\t {ii} - {jj}")
            diff += np.abs(anat_images[ii] - anat_images[jj])
    # mean pearson correlation accros each iteration combination
    diff /= (n_samples * (n_samples - 1)/2)
    # saving stats images
    print(f"\t Saving figures...")
    diff_values = diff.flatten()
    masked_diff = diff * mask_img # masking raw differences
    inv_diff_img = nib.Nifti1Image(masked_diff, affine)
    bg_img = nib.Nifti1Image(anat_images[0], affine)
    plot_stats(inv_diff_img, diff_values, bg_img, sampling, dataset, participant, anat=True)