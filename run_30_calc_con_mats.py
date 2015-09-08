__author__ = 'franzliem'
'''
how to run

'''

import os

# # LeiCA modules
from metrics import calc_con_mats

from variables import  working_dir, freesurfer_dir, template_dir, script_dir, ds_dir
from variables import TR_list, subjects_list
from variables import vols_to_drop, rois_list, lp_cutoff_freq, hp_cutoff_freq, use_fs_brainmask
from variables import use_n_procs, plugin_name

# working_dir = os.path.join(working_dir, 'con_mats')

# for subject_id in subjects_list:
#     subject_working_dir = os.path.join(working_dir, subject_id)
#     subject_ds_dir = os.path.join(ds_dir, subject_id)

## #### ## indent here

test_dir = '/Users/franzliem/Desktop/mattest/'
subject_working_dir = test_dir + 'wd'
subject_ds_dir = test_dir + 'ds'
time_series_file = '/Users/franzliem/Desktop/LeiCA/0144314/residual_filt_norm_warp.nii.gz'

# INPUT PARAMETERS for pipeline

bp_freq_list = [(), (0.01, 0.1)]

parcellation_list = []
parcellation_list.append({'name': 'msdl',
                          'path': os.path.join(template_dir, 'parcellations/msdl_atlas/MSDL_rois/msdl_rois.nii')
                          'is_probabilistic': True})

extraction_methods_list = ['correlation']

calc_con_mats.connectivity_matrix_wf(time_series_file,
                                     working_dir=subject_working_dir,
                                     ds_dir=subject_ds_dir,
                                     subject_id=subject_id,
                                     parcellations_list=parcellation_list,
                                     extraction_methods_list=extraction_methods_list,
                                     bp_freq_list=bp_freq_list,
                                     use_n_procs=use_n_procs,
                                     plugin_name=plugin_name)
