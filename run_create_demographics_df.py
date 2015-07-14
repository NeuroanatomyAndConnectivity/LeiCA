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

    df = pd.concat([df, df_single])

n = df.shape[0]
df.to_pickle(os.path.join(out_dir, 'demographics' + '_n' + str(n) + '.pkl'))
df.to_csv(os.path.join(out_dir, 'demographics' + '_n' + str(n) + '.csv'))