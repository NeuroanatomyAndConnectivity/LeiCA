import os
import pandas as pd

__author__ = 'franzliem'


def read_nki_cvs(filename):
    '''
    imports nki csv and returns pandas data frame with 'Anonymous ID' as index
    csv files with header like:
        "","","Calculated Age"
        "Anonymized ID","Subject Type","AGE_04"
        "A000355xx","Child-Age 11","11.183561643836"
    '''

    df = pd.read_csv(filename, header=1, index_col='Anonymized ID')
    df['origin_file'] = os.path.basename(filename)
    return df


def merge_dataframes(df1, df2):
    '''
    returns merged data frame
    with outer: also returns subjects that are only included in one df (with nans)
    '''
    return pd.merge(df1, df2, left_index=True, right_index=True, how='outer')


def leica_id_to_a_number_mapping(leica_subjects_file, nki_id_mapping_file):
    '''
    for release 1...5 nki subjects '010...' finds 'A...' number
    for > r5 subjects
    returns dataframe with index is leica_subject_id and a_number
    '''
    leica_subjects = pd.read_csv(leica_subjects_file, header=None, names=['leica_id'])
    leica_subjects.set_index(leica_subjects.leica_id, inplace=True)

    nki_id_mapping = pd.read_csv(nki_id_mapping_file)
    nki_id_mapping.set_index(nki_id_mapping.a_number, inplace=True)
    nki_id_mapping['zero_number'] = ['01'+ v[4:] for v in  nki_id_mapping.m_number.values]


    for l in leica_subjects.index:
        if l.startswith('A'): #use A number a
            leica_subjects.loc[l,'a_number'] = l
        else:
            leica_subjects.loc[l,'a_number'] = \
                nki_id_mapping.loc[nki_id_mapping.zero_number=='0161348', 'a_number'].index[0]

    return leica_subjects