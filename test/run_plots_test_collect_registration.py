import os
from plots.collect_registration_plots import collect_registration_plots

from variables import subjects_list, dicom_dir, working_dir, vols_to_drop, project_root_dir, \
    TR_list, freesurfer_dir, template_dir, ds_dir, use_n_procs, fig_dir


# collect registration plots
reg_ds_dir = os.path.join(ds_dir, 'rsfMRI_preproc_wf', 'registration')
slices_list = ['bbr', 'flirt6', 'flirt7', 'flirt9', 'flirt12', 'flirt6MI', 'bbrMI']
out_base_dir = os.path.join(fig_dir, 'registration_slices')

collect_registration_plots(subjects_list, reg_ds_dir, slices_list, out_base_dir, TR_list, collect_struct=True)


