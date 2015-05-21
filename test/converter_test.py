__author__ = 'franzliem'

from nipype.pipeline.engine import Node, MapNode, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio
import nipype.interfaces.fsl as fsl
from nipype.interfaces.freesurfer.utils import ImageInfo
from nipype.interfaces.dcmstack import DcmStack
#from nipype.interfaces.dcm2nii import Dcm2nii
import os

project_root_dir = '/scr/adenauer1/Franz/NKI_tests'
dicom_dir = os.path.join('/scr/kalifornien1/data/nki_enhanced/dicoms')  # '/scr/kalifornien1/data/nki_enhanced/dicoms'
freesurfer_dir = os.path.join('/scr/kalifornien1/data/nki_enhanced/freesurfer')
use_n_procs = 1 #fixme back to 10
working_dir = os.path.join(project_root_dir, 'wd')
ds_dir = os.path.join(working_dir, 'ds')

print('DCMSTACK LOCATION')
os.system('which dcmstack')

# initiate workflow
converter_wf = Workflow(name='conv')
converter_wf.base_dir = os.path.join(working_dir, 'converter_test')

ds = Node(nio.DataSink(base_directory=ds_dir), name='ds')


converter_t1w = Node(DcmStack(embed_meta=True), name='converter_t1w')
converter_t1w.inputs.out_format = 't1w'
converter_t1w.inputs.dicom_files = os.path.join(dicom_dir, '0103384', 'anat')

converter_wf.connect(converter_t1w, 'out_file', ds, 't1w')

converter_wf.run()
