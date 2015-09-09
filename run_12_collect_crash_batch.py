__author__ = 'franzliem'

'''
Copies batch and crash folder from working_dir to results_dir
'''

import os, shutil

from variables import working_dir, ds_dir
from variables import full_subjects_list





for subject_id in full_subjects_list:
    print(subject_id)
    subject_working_dir = os.path.join(working_dir, 'preprocessing', subject_id)
    subject_ds_dir = os.path.join(ds_dir, subject_id)

    crash_dir = os.path.join(subject_working_dir, 'crash')
    batch_dir = os.path.join(subject_working_dir, 'LeiCA_resting', 'batch')

    target_dir = os.path.join(subject_ds_dir, 'condor', 'LeiCA_resting_preprocessing')
    target_crash_dir = os.path.join(target_dir, 'crash')
    target_batch_dir = os.path.join(target_dir, 'batch')

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # copy crash dir
    if os.path.exists(target_crash_dir):
        shutil.rmtree(target_crash_dir)

    if os.path.exists(crash_dir):
        shutil.copytree(crash_dir, target_crash_dir)

    # copy batch dir
    if os.path.exists(target_batch_dir):
        shutil.rmtree(target_batch_dir)
    shutil.copytree(batch_dir, target_batch_dir)

