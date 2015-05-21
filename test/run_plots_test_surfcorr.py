import os
from plots.plot_resting_correlations import plot_rs_surf

from variables import subjects_list, dicom_dir, working_dir, vols_to_drop, project_root_dir, \
    TR_list, freesurfer_dir, template_dir, ds_dir, use_n_procs, fig_dir, rois_list


# collect registration plots

TR = 645
use_aroma = True
use_friston = False
roi = rois_list[0]
fwhm = 0
subject = '0183726'

in_file = os.path.join(working_dir, 'LeiCA_resting/sca', '_TR_id_%s'%TR, '_subject_id_%s'%subject, '_fwhm_%s'%fwhm, \
                      '_use_aroma_%s'%use_aroma, '_use_friston_%s'%use_friston, '_roi_%s.%s.%s'%roi,\
         'correlation_map/corr_map.nii.gz')
plot_rs_surf(in_file, thr_list=[(.2,1)],roi_coords=roi)
