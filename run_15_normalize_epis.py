__author__ = 'franzliem'
'''
how to run

'''

import os

# # LeiCA modules
from preprocessing import normalize

from variables import working_dir, ds_dir, preprocessed_data_dir
from variables import subjects_list
from variables import use_n_procs, plugin_name


##############################
#fixme
working_dir = '/scr/adenauer2/Franz/LeiCA_NKI_test/ws'
ds_dir = '/scr/adenauer2/Franz/LeiCA_NKI_test/ds'
subjects_list = subjects_list[0:1]
##############################

working_dir = os.path.join(working_dir, 'normalize')




for subject_id in subjects_list:
    subject_working_dir = os.path.join(working_dir, subject_id)
    subject_ds_dir = os.path.join(ds_dir, subject_id)

    subject_in_data = os.path.join(preprocessed_data_dir,
                                   '%s/rsfMRI_preprocessing/epis/01_denoised/TR_645/residual.nii.gz' % subject_id)
    subject_warpfield = os.path.join(preprocessed_data_dir,
                                     '%s/rsfMRI_preprocessing//registration/epi_2_MNI_warp/TR_645/MNI152_T1_2mm_concatwarp.nii.gz' % subject_id)

    save_name = 'epis.11_denoised_MNI.TR_645.preprocessed_fullspectrum_MNI_2mm.nii.gz'

    fsl_template = 'MNI152_T1_2mm_brain.nii.gz'
    # INPUT PARAMETERS for pipeline

normalize.normalize_epi(in_data=subject_in_data,
                        ref_data=fsl_template,
                        warpfield=subject_warpfield,
                        save_name=save_name,
                        working_dir=subject_working_dir,
                        ds_dir=subject_ds_dir,
                        plugin_name=plugin_name,
                        use_n_procs=use_n_procs)
