__author__ = 'franzliem'

def convert_ids(conversion_csv_file):
    '''
    converts A000...-style ids to 01...-style ids
    :param conversion_csv_file:
    :return: df with clean ids. e.g.
    In [49]: ids.clean_id[ids.anonymized_id == 'A00040623'].values[0]
    Out[49]: array(['0188324'], dtype=object)
    '''

    import pandas as pd

    def clean_id(id):
        #fixme
        if not id.startswith('M109'):
            raise Exception('do not understand id: %s'%id)
        return '01' + id[4:]
    #fixme
    print(conversion_csv_file)

    ids = pd.read_csv(conversion_csv_file, dtype=object)
    ids.drop_duplicates(subset='a_number', inplace=True)

    ids['clean_id'] = ids.m_number.apply(clean_id)
    #fixme
    print ids.head()

    return ids




import pandas as pd
import os, glob, shutil

source_root_path = '/scr/hugo1/nki/release7/nki/dicom/triotim/mmilham/discoverysci_30001/'
target_root_path = '/scr/adenauer2/nki_r7/test'

if not os.path.exists(target_root_path):
    os.makedirs(target_root_path)

conversion_csv_file = '/scr/adenauer2/nki_r7/nki_r1_r7_matched_ids_unq.csv'
ids = convert_ids(conversion_csv_file)
#fixme
ids.head()
print('XXXXXSXSSEARFAFASDFASDFASDADFSAFSDDSAF')

#mapping from type: (source, target)
mapping_dict = {'t1w':('MPRAGE_SIEMENS_DEFACED_0003','anat'),
                'rs645': ('REST_645_0002','session_1/RfMRI_mx_645'),
                'rs1400': ('REST_1400_0004','session_1/RfMRI_mx_1400'),
                'dwi': ('DIFF_137_AP_0009','session_1/DTI_mx_137'),
                }





os.chdir(source_root_path)
subject_list = glob.glob('A*')
#fixme
#subject_list = subject_list[:2]

ok=[]
notok=[]

for a_number in subject_list:
    print a_number
    if not any(ids.a_number == a_number):
        notok.append(a_number)
        #raise Exception('no conversion id found %s'%anonymized_id)

    else:
        ok.append(a_number)


        clean_id =  ids.clean_id[ids.a_number == a_number].values[0]
        # if os.path.exists(os.path.join(target_root_path, clean_id)):
        #     shutil.rmtree(os.path.join(target_root_path, clean_id))
        #
        # os.makedirs(os.path.join(target_root_path, clean_id,'session_1'))
        #
        # print('\n')
        # print(clean_id)
        # for key in mapping_dict.keys():
        #     source_str = mapping_dict[key][0]
        #     target_str = mapping_dict[key][1]
        #
        #
        #     in_path_list = glob.glob(os.path.join(source_root_path, a_number, '*',source_str))
        #     target_path = os.path.join(target_root_path, clean_id, target_str)
        #
        #     if in_path_list[0] == []:
        #         print ('missing: %s'%key)
        #
        #     if len(in_path_list)>1:
        #         raise Exception('ambigous path: %s %s'%(anonymized_id, key))
        #     if len(in_path_list)==0:
        #         print('no folder foud: %s %s'%(anonymized_id, key))
        #     print('%s copied to \n%s \n\n'%(in_path_list[0], target_path))
        #     #shutil.copytree(in_path_list[0], target_path)
        #     os.symlink(in_path_list[0], target_path)


print 'ok'
print(ok)
print 'nook'
print notok