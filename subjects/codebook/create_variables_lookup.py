'''
builds variable lookup dict from DS CODEBOOK.csv (COINS). e.g.
variable_dict=json.load(open('variable_dict.json'))
variable_dict['DEM_002']['label']
variable_dict['DEM_002']['response']['1']
'''
import pandas as pd
import numpy as np
import json, os

codebook_path = '/Users/franzliem/Dropbox/Workspace/LeiCA/subjects/codebook/'
codebook_file = os.path.join(codebook_path, 'DS CODEBOOK.csv')


def make_valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_') # I don't like spaces in filenames.
    return filename



def get_df_cut(df, selection_type, value_list, selection_value):
    start_index = np.where(df[selection_type]==selection_value)[0][0]
    next_value_index = np.where(value_list==selection_value)[0]+1
    if next_value_index>len(value_list)-1: #last item in list
        end_index = len(df)
    else:
        next_value = value_list[next_value_index][0]
        end_index = np.where(df[selection_type]==next_value)[0][0]
    return df.iloc[start_index:end_index]

df = pd.read_csv(codebook_file)

instruments_list = df['Instrument'].loc[~df['Instrument'].isnull()].values
variable_dict = {}
for instrument in instruments_list:
    df_1_instrument = get_df_cut(df, 'Instrument',instruments_list, instrument)   
    q_id_list = df_1_instrument['Question ID'].loc[~df_1_instrument['Question ID'].isnull()].values
    
    for q_id in q_id_list:
        df_1_q = get_df_cut(df_1_instrument, 'Question ID', q_id_list, q_id)

        label = df_1_q['Question Label'].values[0]
        description = df_1_q['Question Description'].values[0]
        
        resp_values_list = df_1_q['Response Value'].values
        resp_values_dict = {}

        for resp_value in resp_values_list:
            #get non nan values
            valid_values = df_1_q[['Response Value']].loc[~df_1_q['Response Value'].isnull()].values
            if len(valid_values)>0:
                for v in valid_values:
                    resp_values_dict[v[0]] = df_1_q['Response Label'][df_1_q['Response Value']==v[0]].values[0]          
        
        variable_dict[q_id] = {'instrument': instrument,
                           'label': label, 
                           'desciption': description,
                           'response': resp_values_dict}


filename = os.path.join(codebook_path, 'variable_dict.json')
json.dump(variable_dict, open(filename,'w'))
