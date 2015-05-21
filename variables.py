__author__ = 'franzliem'

import os
import subprocess
import sys
from utils import load_subjects_list, get_subjects_list_fold

pipeline_version = '0.1'

# SUBJECTS LIST FOLD INFO
fold_n = 1
fold_size = 100

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
    dicom_dir = os.path.join(project_root_dir, 'dicoms')
    freesurfer_dir = os.path.join(project_root_dir, 'freesurfer')
    use_n_procs = 3
    plugin_name = 'MultiProc'

    fig_dir = '/Users/franzliem/Dropbox/LeiCA/figs'
    report_base_dir = '/Users/franzliem/Dropbox/LeiCA/QC'

    subjects_file_prefix = 'subjects_2015-05-11'
    subjects_file = subjects_file_prefix + '_test_1_subj_mbp.txt'

else:
    print 'working on %s' % hostname
    project_root_dir = '/scr/adenauer1/Franz/NKI_tests'
    dicom_dir = os.path.join('/scr/kalifornien1/data/nki_enhanced/dicoms')
    freesurfer_dir = os.path.join('/scr/kalifornien1/data/nki_enhanced/freesurfer')
    use_n_procs = 3
    #plugin_name = 'MultiProc'
    plugin_name = 'CondorDAGMan'

    fig_dir = '/home/raid2/liem/Dropbox/LeiCa/figs'
    report_base_dir = '/home/raid2/liem/Dropbox/LeiCa/QC'

    subjects_file_prefix = 'subjects_2015-05-11'
    subjects_file = subjects_file_prefix + '.txt'

# TR LIST
TR_list = ['645']




# CHECK IF DIRS EXIST
check_dir_list = [project_root_dir, dicom_dir, freesurfer_dir]
for d in check_dir_list:
    if not os.path.isdir(d):
        raise Exception('Directory %s does not exist. exit pipeline.' % d)


working_dir = os.path.join(project_root_dir, 'wd')
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