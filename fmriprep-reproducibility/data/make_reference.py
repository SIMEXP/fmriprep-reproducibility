import os
import re
import bids

#1. cp all raw fuzzy data (if exists!)
#2. save bids cache from raw data
#3. generate mean, sig and std from fuzzy anat
#4. make BIDS dataset on generated fuzzy, and save the bids cache
