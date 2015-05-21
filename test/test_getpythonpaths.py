

import os

from nipype import config
from nipype.pipeline.engine import Node, Workflow, JoinNode
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio
import nipype.interfaces.fsl as fsl
import nipype.interfaces.freesurfer as freesurfer
from variables import subjects_list, dicom_dir, working_dir, vols_to_drop, project_root_dir, \
    TR_list, freesurfer_dir, template_dir, ds_dir, use_n_procs, fwhm_list, plugin_name

import sys
print sys.path
#from ICA_AROMA import ICA_AROMA_functions

form ICA_AROMA.ICA_AROMA_functions import runICA
runICA()


def gpp():
    import sys, os
    pa = sys.path
    filename=os.path.join(os.getcwd(), 'python_paths.txt')
    f = open(filename, 'w')
    f.write("\n".join(pa))
    f.close()
    return filename


wf = Workflow(name='python_path_test')
wf.base_dir = os.path.join(working_dir)

ds = Node(nio.DataSink(base_directory=ds_dir), name='python_paths_test_ds')

getpythonpath = Node(util.Function(input_names=[''],
                                       output_names=['filename'],
                                       function=gpp), name='gpp')

wf.connect(getpythonpath, 'filename', ds, 'python_paths')
wf.run() #(plugin='CondorDAGMan')

