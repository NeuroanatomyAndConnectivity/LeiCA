__author__ = 'franzliem'

import numpy as np
import os, glob
import pandas as pd

df = pd.DataFrame([], columns=['fs_version'])

root_dir='/scr/kalifornien1/data/nki_enhanced/freesurfer'
os.chdir(root_dir)

s_list = glob.glob('0*')

for s in s_list:
    fn=os.path.join(root_dir,s,'scripts/build-stamp.txt')
    if os.path.exists(fn):
        with open(fn, 'r') as f:
            v=f.read().strip('freesurfer-Linux-centos6_x86_64-stable-pub-v').strip()
    else:
        v=np.nan

    df.loc[s,'fs_version'] = v

df.old = df['fs_version'] == '5.1.0'
old_list = df.index[(df.old)].values