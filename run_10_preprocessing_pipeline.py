__author__ = 'franzliem'
'''
how to run
1. set fold_n in variables
2. run run_preprocessing_pipeline
3. run collect_crash_batch
4. delete working_dir
5. increase fold_n and start from the top
...
99. run run_create_qc_reports.py
'''

import os

# # LeiCA modules
from preprocessing_pipeline import preprocessing_pipeline

from variables import dicom_dir, working_dir, freesurfer_dir, template_dir, script_dir, ds_dir
from variables import TR_list, subjects_list
from variables import vols_to_drop, rois_list, lp_cutoff_freq, hp_cutoff_freq, use_fs_brainmask
from variables import use_n_procs, plugin_name






for subject_id in subjects_list:
    subject_working_dir = os.path.join(working_dir, 'preprocessing', subject_id)
    subject_ds_dir = os.path.join(ds_dir, subject_id)

    # INPUT PARAMETERS for pipeline
    cfg ={}

    cfg['subject_id'] = subject_id

    cfg['dicom_dir'] = dicom_dir
    cfg['working_dir'] = subject_working_dir
    cfg['freesurfer_dir'] = freesurfer_dir
    cfg['template_dir'] = template_dir
    cfg['script_dir'] = script_dir
    cfg['ds_dir'] = subject_ds_dir

    cfg['TR_list'] = TR_list

    cfg['vols_to_drop'] = vols_to_drop
    cfg['rois_list'] = rois_list
    cfg['lp_cutoff_freq'] = lp_cutoff_freq
    cfg['hp_cutoff_freq'] = hp_cutoff_freq
    cfg['use_fs_brainmask'] = use_fs_brainmask

    cfg['use_n_procs'] = use_n_procs
    cfg['plugin_name'] = plugin_name

    preprocessing_pipeline(cfg)

