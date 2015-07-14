
__author__ = 'franzliem'
import os
import shutil

import numpy as np
import pandas as pd
from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.utility as util

from utils import get_condor_exit_status, check_if_wf_crashed, load_subjects_list
from qc_reports.create_qc_report_pdf import create_qc_report_pdf
from variables import ds_dir, report_base_dir, subjects_dir, working_dir
from variables import TR_list, subjects_list, subjects_file_prefix
from variables import plugin_name, use_n_procs




#fixme
plugin_name = 'MultiProc'
use_n_procs = 3


subjects_missing_files_list = load_subjects_list(subjects_dir, subjects_file_prefix + '_excluded.txt')


report_str = 'rsfMRI_preprocessing'


wf = Workflow('qc_reports_wf')
wf.base_dir = report_base_dir
wf.config['execution']['crashdump_dir'] = os.path.join(report_base_dir, 'crash')
wf.config['execution']['stop_on_first_crash'] = False

# collect dfs
df = pd.DataFrame()
print subjects_list

for TR in TR_list:
    rel_report_dir = os.path.join('WD_' + report_str + '_TR_%s'%TR)
    os.chdir(report_base_dir)
    if os.path.isdir(rel_report_dir):
        shutil.rmtree(rel_report_dir)
    os.mkdir(rel_report_dir)
    os.chdir(rel_report_dir)
    os.mkdir('reports')

    for subject_id in subjects_list:
        print(subject_id)

        # get condor exit status
        batch_dir =os.path.join(working_dir, subject_id, 'LeiCA_resting', 'batch')
        if os.path.exists(batch_dir):
            try:
                condor_exitcode, condor_n_jobs_failed = get_condor_exit_status(batch_dir)
            except:
                condor_exitcode, condor_n_jobs_failed = (np.nan, np.nan)
        else:
            condor_exitcode = np.nan
            condor_n_jobs_failed = np.nan
        print batch_dir
        print((condor_exitcode, condor_n_jobs_failed))
        print ' '
        df_ss = pd.DataFrame([subject_id], columns=['subject_id'])
        df_ss = df_ss.set_index(df_ss.subject_id)
        df_ss['condor_exitcode'] = condor_exitcode
        df_ss['condor_n_jobs_failed'] = condor_n_jobs_failed



        ######

        df = pd.concat([df, df_ss])

    df.to_pickle('group.QC.pkl')
    df.to_csv('group.QC.csv', sep='\t')
    df.to_excel('group.QC.xlsx')