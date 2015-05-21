import os
import shutil

from plots.plot_resting_correlations import plot_rs_surf_bh

from variables import subjects_list, dicom_dir, working_dir, vols_to_drop, project_root_dir, \
    TR_list, freesurfer_dir, template_dir, ds_dir, use_n_procs, fig_dir, rois_list, fwhm_list, use_aroma_list, use_friston_list


# collect registration plots

# in_file = os.path.join(working_dir, 'LeiCA_resting/sca', '_TR_id_%s'%TR, '_subject_id_%s'%subject, '_fwhm_%s'%fwhm, \
#                       '_use_aroma_%s'%use_aroma, '_use_friston_%s'%use_friston, '_roi_%s.%s.%s'%roi,\
#          'correlation_map/corr_map.nii.gz')
# plot_rs_surf(in_file, thr_list=[(.2,1)],roi_coords=roi)

out_base_dir = os.path.join(fig_dir, 'group_test_results_figs')
if os.path.isdir(out_base_dir):
    shutil.rmtree(out_base_dir)

out_dir_mean = os.path.join(out_base_dir, 'mean')
out_dir_diff = os.path.join(out_base_dir, 'diff')
os.makedirs(out_dir_mean)
os.makedirs(out_dir_diff)

in_base_dir = os.path.join(fig_dir, 'group_test_results')
in_dir_mean = os.path.join(in_base_dir, 'mean')
in_dir_diff = os.path.join(in_base_dir, 'diff')


# diff files
ti_list = ['aroma_v_friston_a-b', 'smoothing_6_v_0_a-c', 'friston_1_v_0_a-d', 'aroma_1_v_0_a-e']

os.chdir(out_dir_diff)
for roi in rois_list:
    os.chdir(out_dir_diff)
    out_roi_dir = os.path.join(out_dir_diff, 'roi_%s.%s.%s'%roi)
    os.makedirs(out_roi_dir)
    os.chdir(out_roi_dir)
    for ti in ti_list:
        in_file = os.path.join(in_dir_diff, ti + '_roi_%s.%s.%s'%roi + '.nii.gz')
        plot_rs_surf_bh(in_file, thr_list=[(.05,.3)],roi_coords=roi)




# mean files
os.chdir(out_dir_mean)

for TR in TR_list:
    for fwhm in fwhm_list:
        for use_aroma in use_aroma_list:
            for use_friston in use_friston_list:
                for roi in rois_list:
                    os.chdir(out_dir_mean)
                    out_roi_dir = os.path.join(out_dir_mean, 'roi_%s.%s.%s'%roi)
                    if not os.path.isdir(out_roi_dir):
                        os.makedirs(out_roi_dir)
                    os.chdir(out_roi_dir)


                    path_str = os.path.join('_TR_id_%s'%TR, '_fwhm_%s'%fwhm, '_use_aroma_%s'%use_aroma,\
                                   '_use_friston_%s'%use_friston,'_roi_%s.%s.%s'%roi)

                    in_file = 'group.mean.' + path_str.replace('/', '.') + '.nii.gz'
                    in_file_path = os.path.join(in_dir_mean, in_file)
                    plot_rs_surf_bh(in_file_path, thr_list=[(.1,1)],roi_coords=roi)
