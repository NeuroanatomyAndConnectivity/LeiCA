from nipype.pipeline.engine import Node, Workflow, MapNode

import nipype.interfaces.utility as util

'''
Main workflow for denoising
Based on: based on https://github.com/NeuroanatomyAndConnectivity/pipelines/blob/master/src/lsd_lemon/func_preproc/denoise.py

Largely based on https://github.com/nipy/nipype/blob/master/examples/
rsfmri_vol_surface_preprocessing_nipy.py#L261
but denoising in anatomical space
'''


def testNode():
    # workflow
    denoise_wf = Workflow(name='denoise')

    # Define nodes
    inputnode = Node(interface=util.IdentityInterface(fields=['hpval']),
                     name='inputnode')


    print inputnode.inputs.hpval
    return denoise_wf
