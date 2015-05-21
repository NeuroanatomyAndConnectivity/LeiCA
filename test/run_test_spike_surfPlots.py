
import os
import sys
import shutil
from variables import working_dir, rois_list, TR_list, fig_dir, subjects_list
from plots.plot_resting_correlations import  plot_rs_surf_bh
thr_list = [.2]
spike_list = [True, False]


in_base_dir = '/Users/franzliem/Dropbox/LeiCA/figs/spike_reg_data/'
fig_save_dir = os.path.join(fig_dir, 'spike_reg')

if os.path.isdir(fig_save_dir):
    shutil.rmtree(fig_save_dir)
os.mkdir(fig_save_dir)
os.chdir(fig_save_dir)

os.environ['FREESURFER_HOME'] = '/Applications/freesurfer/'
os.environ['SUBJECTS_DIR'] = '/Applications/freesurfer/subjects'

from surfer import Brain, io

"""Bring up the visualization"""
#brain = Brain("fsaverage", "split", "inflated", views=['lat', 'med'], config_opts=dict(background="white"))

"""Project the volume file and return as an array"""
reg_file = os.path.join(os.environ["FREESURFER_HOME"],"average/mni152.register.dat")

for TR in TR_list:
    for spike in spike_list:
        os.chdir(fig_save_dir)
        out_dir = os.path.join(fig_save_dir, 'spike_reg_%s'%spike)
        os.mkdir(out_dir)
        os.chdir(out_dir)

        for roi in rois_list:

            brain = Brain("fsaverage", "split", "inflated", views=['lat', 'med'], config_opts=dict(background="white"))
            print spike
            mri_file = os.path.join(in_base_dir, '_spike_reg_%s'%spike, '_roi_%s.%s.%s'%roi, 'mean_sca/concat_corr_z_mean.nii.gz')
            print ' '
            print mri_file
            plot_rs_surf_bh(in_file=mri_file, roi_coords=roi, thr_list=[(.1,1)])




####
# comparison to old analysis

fig_save_dir = os.path.join(fig_dir, 'vgl_aroma_stream')

if os.path.isdir(fig_save_dir):
    shutil.rmtree(fig_save_dir)
os.mkdir(fig_save_dir)
os.chdir(fig_save_dir)

roi = (-8,-56,26)
file_list = ['/Users/franzliem/Dropbox/LeiCA/figs/group_test_results/mean/group.mean._TR_id_645._fwhm_0._use_aroma_False._use_friston_True._roi_-8.-56.26.nii.gz',
             '/Users/franzliem/Dropbox/LeiCA/figs/group_test_results/mean/group.mean._TR_id_645._fwhm_6._use_aroma_False._use_friston_True._roi_-8.-56.26.nii.gz']
for file in file_list:
    brain = Brain("fsaverage", "split", "inflated", views=['lat', 'med'], config_opts=dict(background="white"))
    mri_file = file
    print mri_file
    plot_rs_surf_bh(in_file=mri_file, roi_coords=roi,thr_list=[(.1,1)])

####
#SS plots:


in_base_dir = '/Users/franzliem/Dropbox/LeiCA/figs/spike_reg_ss_data/'
fig_save_dir = os.path.join(fig_dir, 'spike_reg_ss')

if os.path.isdir(fig_save_dir):
    shutil.rmtree(fig_save_dir)
os.mkdir(fig_save_dir)
os.chdir(fig_save_dir)

subject_num_list = range(11)
roi = (-8,-56,26)

print'CCCC'
print subject_num_list
for spike in spike_list:
    os.chdir(fig_save_dir)
    out_dir = os.path.join(fig_save_dir, 'spike_reg_%s'%spike)
    os.mkdir(out_dir)
    os.chdir(out_dir)

    for subject_num in subject_num_list:
            brain = Brain("fsaverage", "split", "inflated", views=['lat', 'med'], config_opts=dict(background="white"))
            mri_file = os.path.join(in_base_dir, '_spike_reg_%s'%spike, '_roi_%s.%s.%s'%roi, 'collect_sca/' + 'vol%04d.nii.gz'%subject_num)
            print ' '
            print mri_file
            plot_rs_surf_bh(in_file=mri_file, roi_coords=roi, thr_list=[(.1,1)])

