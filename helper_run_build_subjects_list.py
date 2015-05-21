import os, glob, datetime
import json
from variables import dicom_dir, freesurfer_dir, subjects_dir

os.chdir(dicom_dir)

subjects_list = [s for s in glob.iglob('0*')]



dicom_dict = {'t1w':'anat', 'rs':'session_1/RfMRI_mx_645', 'diffusion':'session_1/DTI_mx_137'}
dicom_missing = {'t1w':[], 'rs':[], 'diffusion':[], 'fs':[]}
bad_subjects_list = []

for subject in subjects_list:
    for img, img_file in dicom_dict.items():
        check_file = os.path.join(dicom_dir, subject, img_file)
        file_exists = os.path.exists(check_file)

        if not file_exists:
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

td_str = datetime.datetime.isoformat(datetime.datetime.today())[:10]
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
