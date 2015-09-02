__author__ = 'franzliem'

import pandas as pd
import os, glob

in_dir = '/Users/franzliem/Dropbox/Workspace/LeiCA/subjects/demographics/orig_files'
out_dir = '/Users/franzliem/Dropbox/Workspace/LeiCA/subjects/demographics/'

os.chdir(in_dir)
demo_files_list = [f for f in glob.iglob('nki-*.csv')]

df = pd.DataFrame()

for demo_file in demo_files_list:
    df_single = pd.read_csv(demo_file, dtype=object)
    df_single['release'] = [demo_file] * df_single.shape[0]
    df_single.rename(columns={'Subject ID': 'subject_id', 'Age': 'age', 'Sex': 'sex', 'Dominant Hand': 'dominant_hand',
                              ' Download Group': 'download_group'}, inplace=True)
    df_single.age = df_single.age.astype('float')
    df_single = df_single.set_index(df_single.subject_id)

    #deal with some weirdness: starting with r6
    # sex is coded as 1 and 2
    # if not('M' in df_single.sex and 'F' in df_single.sex):
    #
    # if df_single.subject_id.loc[0].startswith('A'):
    #     #fixme DO SUBJECTS LIST CONVERSION


    df = pd.concat([df, df_single])

n = df.shape[0]
df.to_pickle(os.path.join(out_dir, 'demographics' + '_n' + str(n) + '.pkl'))
df.to_csv(os.path.join(out_dir, 'demographics' + '_n' + str(n) + '.csv'))




def convert_ids(conversion_csv_file):
    '''

    :param conversion_csv_file:
    :return: df with clean ids. e.g.
    In [49]: ids.clean_id[ids.anonymized_id == 'A00040623'].values
    Out[49]: array(['0188324'], dtype=object)
    '''

    import pandas as pd

    def clean_id(id):
        #fixme
        if not id.startswith('M109'):
            raise Exception('do not understand id: %s'%id)
        return '01' + id[4:]

    ids = pd.read_csv(conversion_csv_file, skiprows=1, dtype=object)
    ids.rename(columns={'Anonymized ID': 'anonymized_id'}, inplace=True)
    ids.drop_duplicates(subset='anonymized_id', inplace=True)

    ids['clean_id'] = ids.NKIURSI_01.apply(clean_id)
    return ids