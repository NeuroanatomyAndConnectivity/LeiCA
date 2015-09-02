
__author__ = 'franzliem'
import yaml
import glob
import os
from variables import ds_dir, report_base_dir, subjects_dir, working_dir
from variables import TR_list, subjects_list, subjects_file_prefix






for TR in TR_list:
    for subject_id in subjects_list:
        # get condor exit status
        batch_dir =os.path.join(working_dir, subject_id, 'LeiCA_metrics', 'batch')
        log_file_list = glob.glob(os.path.join(batch_dir, 'workflow*.dag.metrics'))
        for log_file in log_file_list:
            f = open(log_file)
            d = yaml.load(f)
            f.close()
            bad = 0
            if int(d['exitcode']) > 0:
                bad = 1
            if int(d['jobs_failed']) > 0:
                bad = 1
            if bad:
                # print(subject_id)
                # print(log_file)
                # print((d['exitcode'], d['jobs_failed']))
                # print('XXXXXXXXXXXXXXXXXXX')
                # print('')
                print(subject_id) #, d['exitcode'], d['jobs_failed']))
