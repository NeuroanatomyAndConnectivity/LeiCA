__author__ = 'franzliem'
'''

run locally on big memory machine
runs around 1.5h/subject
'''

import os

# # LeiCA modules
from metrics import calc_metrics

from variables import dicom_dir, preprocessed_data_dir, working_dir, freesurfer_dir, template_dir, script_dir, ds_dir
from variables import TR_list, full_subjects_list
from variables import plugin_name






# for subject_id in subjects_list:
# subject_working_dir = os.path.join(working_dir,'centrality_test', subject_id)
# subject_ds_dir = os.path.join(ds_dir, subject_id, 'metrics')

working_dir = os.path.join(working_dir, 'centrality')
ds_dir = os.path.join(ds_dir)

# INPUT PARAMETERS for pipeline
cfg = {}

cfg['subjects_list'] = full_subjects_list

cfg['dicom_dir'] = dicom_dir
cfg['preprocessed_data_dir'] = preprocessed_data_dir

cfg['working_dir'] = working_dir  # subject_working_dir #
cfg['freesurfer_dir'] = freesurfer_dir
cfg['template_dir'] = template_dir
cfg['script_dir'] = script_dir
cfg['ds_dir'] = ds_dir

cfg['TR_list'] = TR_list

cfg['use_n_procs'] = 34
cfg['plugin_name'] = 'MultiProc'

# fixme
# ignore warning from np.rank
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    calc_metrics.calc_centrality_metrics(cfg)
