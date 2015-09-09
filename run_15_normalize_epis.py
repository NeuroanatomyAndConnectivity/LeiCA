__author__ = 'franzliem'
'''
how to run

'''

# fixme
# some (all?) already have /scr/adenauer2/Franz/LeiCA_NKI_test/c/0120659/rsfMRI_preprocessing/epis_MNI_3mm
# from centrality calc

import os

# # LeiCA modules
from preprocessing import normalize

from variables import working_dir, ds_dir, preprocessed_data_dir, template_dir
from variables import full_subjects_list, TR_list
#from variables import use_n_procs, plugin_name


##############################

working_dir = '/scr/adenauer1/Franz/LeiCA_NKI/normalize'

##############################

use_n_procs = 30
plugin_name = 'MultiProc'

# fixme
# ignore warning from np.rank
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    normalize.normalize_epi(subjects_list=full_subjects_list,
                            TR_list=TR_list,
                            preprocessed_data_dir=preprocessed_data_dir,
                            working_dir=working_dir,
                            ds_dir=ds_dir,
                            template_dir=template_dir,
                            plugin_name=plugin_name,
                            use_n_procs=use_n_procs)
