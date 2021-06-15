import unittest
import os
import re

def get_preproc_list(dir, pattern=".*?"):
    filepaths = []
    for root, _, files in os.walk(dir, followlinks=True):
        for file in files:
            filepath = os.path.join(root, file)
            if re.search(pattern, filepath) is not None:
                filepaths += [filepath]
    
    return filepaths

# Get consistent hash form gzip files
# https://stackoverflow.com/questions/28213912/python-md5-hashes-of-same-gzipped-file-are-inconsistent
# def digest(filepath, block_size=4096):
#     md5 = hashlib.md5()
#     with open(filepath, 'rb') as f:
#         for chunk in iter(lambda: f.read(block_size), b''):
#             md5.update(chunk)
#     return md5.hexdigest()

# def smart_gzip_hash(filepath):
#   input_handle = open(filepath, 'rb')
#   output_filename = output_template.format(x)
#   myzip = gzip.GzipFile(
#       filename='',  # do not emit filename into the output gzip file
#       mode='wb',
#       fileobj=open(output_filename, 'wb'),
#       mtime=0,
#   )
#   block_size = 4096
#   try:
#       for chunk in iter(lambda: input_handle.read(block_size), b''):
#           myzip.write(chunk)
#   finally:
#       input_handle.close()
#       myzip.close()
#   print(digest(output_filename, block_size))

# https://docs.fileformat.com/compression/gz/
def gzip_footer(gzip_filepath):
  with open(gzip_filepath, "rb") as f:
    # set cursor to last 8 bytes and read
    f.seek(-8, os.SEEK_END)
    gzip_footer = f.read()

    return gzip_footer

class Test(unittest.TestCase):
  def test_integrity(self):
    dirpath = os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "ieee")
    list_folders = os.listdir(dirpath)
    folder_matches = []
    # list all folders without the iteration
    for folder in list_folders:
      match_dataset_method = re.match("(.*)_[0-9]+_(.*)", folder)
      if match_dataset_method:
        folder_matches += [match_dataset_method[1] + "_[0-9]+_" + match_dataset_method[2]]
    folder_matches = list(set(folder_matches))

    # start the file integrity check
    for folder_match in folder_matches:
      print("# {}".format(folder_match))
      # get all preprocessed file from the current folders (same dataset, subject and method, but any iteration)
      filematch = ".*" + folder_match + ".*" + "space-MNI152NLin2009cAsym_desc-preproc.*\\.nii\\.gz"
      list_preproc = get_preproc_list(dirpath, pattern=filematch)
      # get the unique list of preprocessed files
      preproc_matches = []
      for preproc_file in list_preproc:
        preproc_matches += [os.path.basename(preproc_file)]
      preproc_matches = list(set(preproc_matches))
      # for each preprocessed file, get all iterations
      for preproc_match in preproc_matches:
        print("\t{}".format(preproc_match))
        filematch = ".*" + folder_match + ".*" + preproc_match
        list_preproc_for_dir = get_preproc_list(dirpath, pattern=filematch)
        # check if gzip footer (CRC-32) for each file
        if list_preproc_for_dir:
          footer = gzip_footer(list_preproc_for_dir[0])
          for preproc_file in list_preproc_for_dir[1:]:
            curr_footer = gzip_footer(preproc_file)
            self.assertEqual(curr_footer, footer)

if __name__ == "__main__":
  Test().test_integrity()