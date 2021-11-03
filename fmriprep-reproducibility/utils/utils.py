import os
import re

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

def get_preproc_tasks(dirpath, template):
  pattern=".*task-(.*)_space-" + template + "_desc-preproc.*\\.nii\\.gz"
  if not os.path.exists(dirpath):
    raise ValueError("{} does not exists!".format(dirpath))
  tasks = []
  for root, dirs, files in os.walk(dirpath, followlinks=True):
    for file in files:
      filepath = os.path.join(root, file)
      match = re.match(pattern, filepath)
      if match:
        tasks += [match[1]]
  
  return tasks

def get_preproc_sub(dirpath, template):
  pattern=".*sub-(.*)_.*_space-" + template + "_desc-preproc.*\\.nii\\.gz"
  if not os.path.exists(dirpath):
    raise ValueError("{} does not exists!".format(dirpath))
  participants = []
  for root, dirs, files in os.walk(dirpath, followlinks=True):
    for file in files:
      filepath = os.path.join(root, file)
      match = re.match(pattern, filepath)
      if match:
        participants += ["sub-" + match[1]]
  
  return participants