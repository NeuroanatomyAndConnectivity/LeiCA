__author__ = 'franzliem'
import os
import shutil

def collect_registration_plots(subjects_list, reg_ds_dir, slices_list, out_base_dir, TR_list, collect_struct=True):

    if not os.path.isdir(out_base_dir):
        os.makedirs(out_base_dir)

    for TR in TR_list:
        out_dir = os.path.join(out_base_dir, 'TR_%s'%TR)
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir)
        os.mkdir(out_dir)

        for subject in subjects_list:
            for slices in slices_list:
                print(reg_ds_dir,'slices_%s'%slices, '_TR_id_%s'%TR, subject, 'slices.png')
                in_file = os.path.join(reg_ds_dir,'slices_%s'%slices, '_TR_id_%s'%TR, subject, 'slices.png')
                out_file = os.path.join(out_dir, subject + '.' + slices + '.png')
                shutil.copy(in_file, out_file)

    if collect_struct:
        out_dir = os.path.join(out_base_dir, 'struct_2_MNI')
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir)
        os.mkdir(out_dir)
        for subject in subjects_list:
            in_file = os.path.join(reg_ds_dir,'slices_struct', subject, 'slices.png')
            out_file = os.path.join(out_dir, subject + '.struct.png')
            shutil.copy(in_file, out_file)

#/Users/franzliem/Desktop/test_data/wd/ds/rsfMRI_preproc_wf/registration/slices_bbr/_TR_id_1400/0103384/slices.png