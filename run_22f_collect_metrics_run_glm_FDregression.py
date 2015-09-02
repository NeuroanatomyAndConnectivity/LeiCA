__author__ = 'franzliem'

import os

# # LeiCA modules
from metrics import collect_metrics_FDregression

from variables import preprocessed_data_dir, working_dir, ds_dir, script_dir, template_dir, report_base_dir
from variables import full_subjects_list, metric_name_dict
from variables import use_n_procs, plugin_name

#fixme do in variables eventually
# METRICS (for collection & stats)
metric_name_dict = {'alff': 'metrics/alff/alff_MNI_3mm/TR_645/residual_filtered_3dT_warp.nii.gz',
                   'falff': 'metrics/alff/falff_MNI_3mm/TR_645/brain_mask_epiSpace_calc_warp.nii.gz',
                   'reho': 'metrics/reho/reho_MNI_3mm/TR_645/ReHo_warp.nii.gz',
                   'vmhc': 'metrics/vmhc/VMHC_FWHM_img/TR_645/residual_filt_norm_maths_warp_tcorr.nii.gz',
                    'variability_std': 'metrics/variability/MNI_3mm/TR_645/ts_std_warp.nii.gz',
                    'dc_b': 'metrics/centrality/dc/TR_645/degree_centrality_binarize.nii.gz',
                    'evc_b': 'metrics/centrality/evc/TR_645/eigenvector_centrality_binarize.nii.gz'
}



working_dir = os.path.join(working_dir, 'group_metric_FDregression')
ds_dir = os.path.join(ds_dir, 'group_metric_FDregression')

demos_df = os.path.join(script_dir, 'subjects/demographics/demographics_n415.pkl')
qc_df = os.path.join(report_base_dir, 'rsfMRI_preprocessing_TR_645/group.QC.pkl')

for metric_name in metric_name_dict:
    metric_working_dir = os.path.join(working_dir, metric_name)
    metric_ds_dir = os.path.join(ds_dir, metric_name)

    # INPUT PARAMETERS for pipeline
    cfg ={}

    cfg['subjects_list'] = full_subjects_list

    cfg['metrics_data_dir'] = preprocessed_data_dir
    cfg['metrics_data_suffix'] = metric_name_dict[metric_name]
    cfg['metric_name'] = metric_name
    cfg['demos_df'] = demos_df
    cfg['qc_df'] = qc_df
    cfg['template_dir'] = template_dir

    cfg['working_dir'] = metric_working_dir
    cfg['ds_dir'] = metric_ds_dir

    cfg['use_n_procs'] = use_n_procs
    cfg['plugin_name'] = plugin_name


    collect_metrics_FDregression.collect_3d_metrics_run_glm_meanRegression(cfg)
