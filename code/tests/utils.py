import os
import re

def gzip_footer(gzip_filepath):
  with open(gzip_filepath, "rb") as f:
    # set cursor to last 8 bytes and read
    f.seek(-8, os.SEEK_END)
    gzip_footer = f.read()

    return gzip_footer

def get_preproc_list(dirpath, pattern=".*?"):
  if not os.path.exists(dirpath):
    raise ValueError("{} does not exists!".format(dirpath))
  filepaths = []
  for root, dirs, files in os.walk(dirpath, followlinks=True):
    for file in files:
      filepath = os.path.join(root, file)
      if re.search(pattern, filepath) is not None:
        filepaths += [filepath]
  
  return filepaths