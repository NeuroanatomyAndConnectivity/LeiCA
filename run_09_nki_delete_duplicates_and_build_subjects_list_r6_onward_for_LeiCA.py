import os, glob, datetime, shutil
import json
from variables import dicom_dir, freesurfer_dir, subjects_dir

doDelete = False

def get_max_n_elements_in_dir_index(dir_list):
    import numpy as np
    return np.argmax([len(glob.glob(d)) for d in dir_list])

check_img_list = ['REST_645_*', 'REST_1400_*', 'MPRAGE_SIEMENS_DEFACED*', 'REST_CAP_*', 'DIFF_137_AP_*']

#dicom_dir='/scr/adenauer2/Franz/r7_test/nki/dicom/triotim/mmilham/discoverysci_30001'
#dicom_dir='/scr/adenauer2/Franz/r7_test/nki/dicom/triotim/mmilham/'


os.chdir(dicom_dir)

ugly_subjects_list = [s for s in glob.glob('*/A*')]
no_v2 = [] #subjects without visit2

# remove duplicates
for s in ugly_subjects_list:
    v2 = glob.glob(os.path.join(s, '*_V2'))


    if len(v2)==0:
        no_v2.append(s)

    if len(v2)>1:
        #delete all except directory with largest number of elements
        dirs_to_del = v2
        dirs_to_del.remove(v2[get_max_n_elements_in_dir_index(v2)])
        for dir_del in dirs_to_del:
            print 'deleted %s'%dir_del
            if doDelete:
                shutil.rmtree(dir_del)

    #update v2
    v2 = glob.glob(os.path.join(s, '*_V2'))

    if len(v2) == 1: #only check for duplicates if visit2 is there
        # check sequence duplicates
        for sequence in check_img_list:
            se = glob.glob(os.path.join(s, '*_V2', sequence))
            if len(se)>1: #duplicates: remove all but the last one
                dirs_to_del = list(se)
                dirs_to_del.remove(dirs_to_del[-1])
                print se, dirs_to_del
                for dir_del in dirs_to_del:
                    print 'deleted %s'%dir_del
                    if doDelete:
                        shutil.rmtree(dir_del)


[ugly_subjects_list.remove(rem_subj) for rem_subj in no_v2] #remove no v2 subjects from subject_list
subjects_list = [os.path.basename(s) for s in ugly_subjects_list]


dicom_dict = {'t1w':'MPRAGE_SIEMENS_DEFACED*',
              'rs':'REST_645_*',
              'diffusion':'DIFF_137_AP_*'}
dicom_missing = {'t1w':[], 'rs':[], 'diffusion':[], 'fs':[]}
bad_subjects_list = []

for subject in subjects_list:
    for img, img_file in dicom_dict.items():
        check_file = glob.glob(os.path.join(dicom_dir, '*', subject, '*_V2', img_file))
        if not check_file:
            print ('NOOOK: %s %s does not exist'%(subject, img))
            dicom_missing[img].append(subject)
            if not subject in bad_subjects_list:
                bad_subjects_list.append(subject)

    #check if fs dir exists
    check_file = os.path.join(freesurfer_dir, subject)
    file_exists = os.path.exists(check_file)
    if not file_exists:
        print ('NOOOK: %s %s does not exist'%(subject, 'fs'))
        dicom_missing['fs'].append(subject)
        if not subject in bad_subjects_list:
            bad_subjects_list.append(subject)

print bad_subjects_list
for bad_subject in bad_subjects_list:
    subjects_list.remove(bad_subject)

print len(subjects_list)

td_str = datetime.datetime.isoformat(datetime.datetime.today())[:10] + '_r6_r_7'
filename = os.path.join(subjects_dir, 'subjects_%s.txt'%td_str)
file = open(filename, 'w')
for subject in subjects_list:
    file.write('%s\n'%subject)
file.close()

filename = os.path.join(subjects_dir, 'subjects_%s_excluded.txt'%td_str)
file = open(filename, 'w')
for subject in bad_subjects_list:
    file.write('%s\n'%subject)
file.close()

filename = os.path.join(subjects_dir, 'subjects_%s_missing_files.txt'%td_str)
json.dump(dicom_missing, open(filename,'w'))
