__author__ = 'franzliem'

import os
import subprocess
import sys
from utils import load_subjects_list, get_subjects_list_fold
from distutils.version import LooseVersion
import CPAC


pipeline_version = '0.1'


# SUBJECTS LIST FOLD INFO #0-based
fold_n = 0
fold_size = 47

# MOCO PARAMETERS
vols_to_drop = 5

# DENOISE PARAMETERS
hp_cutoff_freq = 0.01
lp_cutoff_freq = 0.1

# STRUCTURAL BRAIN MASK
use_fs_brainmask = True


# SCA PARAMETERS
rois_list = []
# # #lMPFC
# rois_list.append((-6,52,-2))
# # #rMPFC
# rois_list.append((6,52,-2))
# #lPCC
rois_list.append((-8,-56,26))
# # #rPCC
# rois_list.append((8,-56,26))
#
# #Wotruba
rois_list.append((38,22,-10))
# rois_list.append((-1,49,-2))
#
# #fox
# rois_list.append((-5,-49,40))
#



########################################################################################################################
# SET DIRS
hostname = subprocess.check_output('hostname', shell=True)
arch = subprocess.check_output('arch', shell=True)

if arch.startswith('i386'):
    print 'working on MBP13'
    project_root_dir  = '/Users/franzliem/Desktop/test_data'  # LeiCA_test_data'
    project_root_dir_2 = project_root_dir
    dicom_dir = os.path.join(project_root_dir, 'dicoms')
    freesurfer_dir = os.path.join(project_root_dir, 'freesurfer')
    preprocessed_data_dir = os.path.join(project_root_dir, 'results')

    use_n_procs = 3
    plugin_name = 'MultiProc'

    fig_dir = '/Users/franzliem/Dropbox/LeiCA/figs'
    report_base_dir = '/Users/franzliem/Dropbox/LeiCA/QC'

    subjects_file_prefix = 'subjects_2015-05-11'
    subjects_file = subjects_file_prefix + '.txt' #'_test_1_subj_mbp.txt'

else:
    print 'working on %s' % hostname
    project_root_dir = '/scr/adenauer2/Franz/LeiCA_NKI'
    project_root_dir_2 = '/scr/adenauer2/Franz/LeiCA_NKI'
    #dicom_dir = os.path.join('/scr/kalifornien1/data/nki_enhanced/dicoms')
    #freesurfer_dir = os.path.join('/scr/kalifornien1/data/nki_enhanced/freesurfer')

    #r5
    dicom_dir = os.path.join('/scr/adenauer2/nki_r5_onwards/r5/dicoms')
    freesurfer_dir = os.path.join('/scr/adenauer2/nki_r5_onwards/r5/data/freesurfer')

    #r6/7
    dicom_dir = os.path.join('/scr/kaiser2/NKI/nki_r5_onwards/r6_onwards/dicoms/nki/dicom/triotim/mmilham')
    freesurfer_dir = os.path.join('/scr/kaiser2/NKI//scr/adenauer2/nki_r5_onwards/r6_onwards/data/freesurfer')

    preprocessed_data_dir = os.path.join(project_root_dir, 'results')
    use_n_procs = 3
    #plugin_name = 'MultiProc'
    plugin_name = 'CondorDAGMan'

    fig_dir = '/home/raid2/liem/Dropbox/LeiCa/figs'
    report_base_dir = '/home/raid2/liem/Dropbox/LeiCa/QC'
    subjects_file_prefix = 'subjects_2015-08-26'
    subjects_file = subjects_file_prefix + '_redo_r5.txt'

# TR LIST
TR_list = ['645']



# CHECK IF DIRS EXIST
check_dir_list = [project_root_dir] #, dicom_dir, freesurfer_dir]
for d in check_dir_list:
    if not os.path.isdir(d):
        raise Exception('Directory %s does not exist. exit pipeline.' % d)

#fixme _metrics
working_dir = os.path.join(project_root_dir_2)
ds_dir = os.path.join(project_root_dir, 'results')

# OTHER STUFF
# set python path
script_dir = os.path.dirname(os.path.realpath(__file__))

# set subjects_dir
subjects_dir = os.path.join(script_dir, 'subjects')

# set template directory
template_dir = os.path.join(script_dir, 'anat_templates')


# APPEND TO PYHTONPATH
prep_script_dir = os.path.join(script_dir, 'preprocessing')
plots_script_dir = os.path.join(script_dir, 'plots')

sys.path.extend([prep_script_dir, plots_script_dir])


# GET SUBJECT LIST FROM TXT FILE
full_subjects_list = load_subjects_list(subjects_dir, subjects_file)
# reduce subjects list to fold
subjects_list = get_subjects_list_fold(full_subjects_list, fold_n, fold_size)


# METRICS (for collection & stats)
metric_name_dict = {'alff': 'metrics/alff/alff_MNI_3mm/TR_645/residual_filtered_3dT_warp.nii.gz',
                    'alff_z': 'metrics/alff/alff_MNI_3mm_Z/TR_645/alff_MNIspace_3mm_zstd.nii.gz',
                    'alff_standardized_mean': 'metrics/alff/alff_MNI_3mm_standardized_mean/TR_645/_standardized0/residual_filtered_3dT_warp_maths.nii.gz',
                    'falff': 'metrics/alff/falff_MNI_3mm/TR_645/brain_mask_epiSpace_calc_warp.nii.gz',
                    'falff_z': 'metrics/alff/falff_MNI_3mm_Z/TR_645/falff_MNIspace_3mm_zstd.nii.gz',
                    'falff_standardized_mean': 'metrics/alff/falff_MNI_3mm_standardized_mean/TR_645/_standardized0/brain_mask_epiSpace_calc_warp_maths.nii.gz',
                    'reho': 'metrics/reho/reho_MNI_3mm/TR_645/ReHo_warp.nii.gz',
                    'reho_z': 'metrics/reho/reho_MNI_3mm_Z/TR_645/reho_MNIspace_3mm_zstd.nii.gz',
                    'reho_standardized_mean': 'metrics/reho/reho_MNI_3mm_standardized_mean/TR_645/_standardized0/ReHo_warp_maths.nii.gz',
                    'vmhc': 'metrics/vmhc/VMHC_FWHM_img/TR_645/residual_filt_norm_maths_warp_tcorr.nii.gz',
                    'vmhc_z': 'metrics/vmhc/VMHC_Z_FWHM_img/TR_645/residual_filt_norm_maths_warp_tcorr_calc.nii.gz',
                    'vmhc_z_stat': 'metrics/vmhc/VMHC_Z_stat_FWHM_img/TR_645/residual_filt_norm_maths_warp_tcorr_calc_calc.nii.gz',
                    'variability_mean': 'metrics/variability/MNI_3mm/TR_645/ts_mean_warp.nii.gz',
                    'variability_std': 'metrics/variability/MNI_3mm/TR_645/ts_std_warp.nii.gz',
                    'variability_var': 'metrics/variability/MNI_3mm/TR_645/ts_var_warp.nii.gz',
                    'variability_mssd': 'metrics/variability/MNI_3mm/TR_645/ts_mssd_warp.nii.gz',
                    'variability_sqrt_mssd': 'metrics/variability/MNI_3mm/TR_645/ts_sqrt_mssd_warp.nii.gz',
                    'variability_mean_z': 'metrics/variability/MNI_3mm_Z/TR_645/ts_mean_warp_maths.nii.gz',
                    'variability_std_z': 'metrics/variability/MNI_3mm_Z/TR_645/ts_std_warp_maths.nii.gz',
                    'variability_var_z': 'metrics/variability/MNI_3mm_Z/TR_645/ts_var_warp_maths.nii.gz',
                    'variability_mssd_z': 'metrics/variability/MNI_3mm_Z/TR_645/ts_mssd_warp_maths.nii.gz',
                    'variability_sqrt_mssd_z': 'metrics/variability/MNI_3mm_Z/TR_645/ts_sqrt_mssd_warp_maths.nii.gz',
                    'variability_mean_standardized_mean': 'metrics/variability/MNI_3mm_standardized_mean/TR_645/_standardized0/ts_mean_warp_maths.nii.gz',
                    'variability_std_standardized_mean': 'metrics/variability/MNI_3mm_standardized_mean/TR_645/_standardized1/ts_std_warp_maths.nii.gz',
                    'variability_var_standardized_mean': 'metrics/variability/MNI_3mm_standardized_mean/TR_645/_standardized2/ts_var_warp_maths.nii.gz',
                    'variability_mssd_standardized_mean': 'metrics/variability/MNI_3mm_standardized_mean/TR_645/_standardized3/ts_mssd_warp_maths.nii.gz',
                    'variability_sqrt_mssd_standardized_mean': 'metrics/variability/MNI_3mm_standardized_mean/TR_645/_standardized4/ts_sqrt_mssd_warp_maths.nii.gz',
                    'dc_b': 'metrics/centrality/dc/TR_645/degree_centrality_binarize.nii.gz',
                    'dc_w': 'metrics/centrality/dc/TR_645/degree_centrality_weighted.nii.gz',
                    'dc_b_z': 'metrics/centrality/dc_z/TR_645/degree_centrality_binarize_maths.nii.gz',
                    'dc_w_z': 'metrics/centrality/dc_z/TR_645/degree_centrality_weighted_maths.nii.gz',
                    'evc_b': 'metrics/centrality/evc/TR_645/eigenvector_centrality_binarize.nii.gz',
                    'evc_w': 'metrics/centrality/evc/TR_645/eigenvector_centrality_weighted.nii.gz',
                    'evc_b_z': 'metrics/centrality/evc_z/TR_645/eigenvector_centrality_binarize_maths.nii.gz',
                    'evc_w_z': 'metrics/centrality/evc_z/TR_645/eigenvector_centrality_weighted_maths.nii.gz'
}



#check CPAC version
print('Using CPAC version %s' % CPAC.__version__)
if LooseVersion(CPAC.__version__) >= '0.3.9.1':
    print('CPAC version OK')
else:
    raise Exception('CPAC version >= 0.3.9.1 required')

#check pandas version
import pandas as pd
print('Using pandas version %s' % pd.__version__)
if LooseVersion(pd.__version__) >= '0.16':
    print('pandas version OK')
else:
    raise Exception('pandas version >= 0.16 required')

fsl_v_str=subprocess.check_output('cat $FSLDIR/etc/fslversion', shell=True).strip()
print('Using FSL version %s' % fsl_v_str)
if LooseVersion(fsl_v_str) >= '5':
    print('FSL OK')
else:
    raise Exception('FSL >= version 5 required. version %s found'%fsl_v_str)

