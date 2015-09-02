# DOES NOT CHECK FOR MISSING SEQUENCES
# ONLY DELETES DUPLICATES AND BUILDS A LIST OF SUBJECTS
#
import os, glob, shutil
import json

def get_max_n_elements_in_dir_index(dir_list):
    import numpy as np
    return np.argmax([len(glob.glob(d)) for d in dir_list])

dicom_dir='/scr/adenauer2/nki_r5_onwards/r6_onwards/dicoms/nki/dicom/triotim/mmilham/'
out_dir = '/scr/adenauer2/nki_r5_onwards/r6_onwards/scripts'
out_str = 'r6_r7'
doDelete = True # if false only prints list with files to delete


check_img_list = ['REST_645_*', 'REST_1400_*', 'MPRAGE_SIEMENS_DEFACED*', 'REST_CAP_*', 'DIFF_137_AP_*']
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
                for dir_del in dirs_to_del:
                    print 'deleted %s'%dir_del
                    if doDelete:
                        shutil.rmtree(dir_del)


[ugly_subjects_list.remove(rem_subj) for rem_subj in no_v2] #remove no v2 subjects from subject_list
subjects_list = [os.path.basename(s) for s in ugly_subjects_list]

print 'OK subjects:'
print subjects_list
print 'subjects without visit 2:'
print no_v2


filename = os.path.join(out_dir, 'subjects_%s.txt'%out_str)
print filename
with open(filename, 'w') as f:
    for subject in subjects_list:
        f.write('%s\n'%subject)

filename = os.path.join(out_dir, 'subjects_%s_strings.txt'%out_str)
json.dump(subjects_list, open(filename,'w'))

filename = os.path.join(out_dir, 'subjects_%s_no_V2_strings.txt'%out_str)
json.dump(no_v2, open(filename,'w'))

