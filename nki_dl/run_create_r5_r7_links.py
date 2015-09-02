import pandas as pd
import os, glob, shutil

target_root_path = '/scr/adenauer2/Franz/nki_r5_r6_r7_links'

if os.path.exists(target_root_path):
    shutil.rmtree(target_root_path)
os.makedirs(target_root_path)

source_root_path_list = ['/scr/adenauer2/Franz/NKI_r5_dicoms/dicoms', #r5
                         #'/scr/hugo1/nki/dicoms/triotim/mmilham/discoverysci_30001', #r6
                         '/scr/hugo1/nki/release7/nki/dicom/triotim/mmilham/discoverysci_30001/', #r7
                         ]
duplicates=[]
for source_root_path in source_root_path_list:
    os.chdir(source_root_path)
    #catch all A000... number and all 01... subjects
    subject_list = glob.glob('A0*') + glob.glob('01*')

    for subject in subject_list:
        src_path = os.path.join(os.getcwd(), subject)
        dest_path = os.path.join(target_root_path, subject)
        # print(src_path, dest_path)
        if not os.path.exists(dest_path):
            os.symlink(src_path, dest_path)
        else:
            duplicates.append((src_path,dest_path))

print 'duplicates'
for line in duplicates:
    print line


