'''
Lifted from mindwandering.calculate_measures
'''
import os
from nipype.pipeline.engine import Node, Workflow, MapNode
import nipype.interfaces.utility as util
import nipype.interfaces.fsl as fsl
import nipype.interfaces.afni as afni
import nipype.interfaces.io as nio

from plots.plot_resting_correlations import plot_rs_surf



def create_sca_pipeline(working_dir, rois_list, ds_dir, name='sca'):
    afni.base.AFNICommand.set_default_output_type('NIFTI_GZ')
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')

    sca_wf = Workflow(name=name)
    sca_wf.base_dir = os.path.join(working_dir, 'LeiCA_resting')

    # inputnode
    inputnode = Node(util.IdentityInterface(fields=['rs_preprocessed',
                                                    'epi_2_MNI_warp']),
                     name='inputnode')

    # outputnode
    outputnode = Node(util.IdentityInterface(fields=['functional_mask',
                                                     'seed_based_z']),
                      name='outputnode')

    ds = Node(nio.DataSink(base_directory=ds_dir), name='ds')
    ds.inputs.substitutions = [('_TR_id_', 'TR_')]

    epi_MNIspace = Node(fsl.ApplyWarp(), name='epi_MNIspace')
    epi_MNIspace.inputs.ref_file = fsl.Info.standard_image('MNI152_T1_2mm_brain.nii.gz')
    sca_wf.connect(inputnode, 'rs_preprocessed', epi_MNIspace, 'in_file')
    sca_wf.connect(inputnode, 'epi_2_MNI_warp' , epi_MNIspace, 'field_file')


    epi_mask = Node(interface=afni.Automask(), name='epi_mask')
    sca_wf.connect(epi_MNIspace, 'out_file', epi_mask, 'in_file')
    sca_wf.connect(epi_mask, 'out_file', outputnode, 'functional_mask')

    roi_infosource = Node(util.IdentityInterface(fields=['roi']), name='roi_infosource')
    roi_infosource.iterables = ('roi', rois_list)

    point = Node(afni.Calc(), name='point')
    point.inputs.in_file_a = fsl.Info.standard_image('MNI152_T1_2mm_brain.nii.gz')
    point.inputs.outputtype = 'NIFTI_GZ'
    point.inputs.out_file = 'roi_point.nii.gz'
    def roi2exp(coord):
        return 'step(4-(x%+d)*(x%+d)-(y%+d)*(y%+d)-(z%+d)*(z%+d))'%(coord[0], coord[0], coord[1], coord[1], -coord[2], -coord[2])
    sca_wf.connect(roi_infosource, ('roi', roi2exp), point, 'expr')

    def format_filename(roi_str):
        import string
        valid_chars = '-_.%s%s' % (string.ascii_letters, string.digits)
        return 'roi_'+''.join(c for c in str(roi_str).replace(',','_') if c in valid_chars)+'_roi.nii.gz'

    sphere = Node(fsl.ImageMaths(), name='sphere')
    sphere.inputs.out_data_type = 'float'
    sphere.inputs.op_string = '-kernel sphere 8 -fmean -bin'
    sca_wf.connect(point, 'out_file', sphere, 'in_file')
    sca_wf.connect(roi_infosource, ('roi', format_filename), sphere, 'out_file')

    #fixme
    # smoothing = Node(fsl.maths.IsotropicSmooth(), name='smoothing')
    # smoothing.iterables = ('fwhm', [1, 6])
    # sca_wf.connect(epi_MNIspace, 'out_file', smoothing, 'in_file')

    extract_timeseries = Node(afni.Maskave(), name='extract_timeseries')
    extract_timeseries.inputs.quiet = True
    sca_wf.connect(sphere, 'out_file', extract_timeseries, 'mask')
    #fixme
    sca_wf.connect(epi_MNIspace, 'out_file', extract_timeseries, 'in_file')
    #sca_wf.connect(smoothing, 'out_file', extract_timeseries, 'in_file')

    correlation_map = Node(afni.Fim(), name='correlation_map')
    correlation_map.inputs.out = 'Correlation'
    correlation_map.inputs.outputtype = 'NIFTI_GZ'
    correlation_map.inputs.out_file = 'corr_map.nii.gz'
    sca_wf.connect(extract_timeseries, 'out_file', correlation_map, 'ideal_file')
    sca_wf.connect(epi_MNIspace, 'out_file', correlation_map, 'in_file')

    z_trans = Node(interface=afni.Calc(), name='z_trans')
    z_trans.inputs.expr = 'log((1+a)/(1-a))/2'
    z_trans.inputs.outputtype = 'NIFTI_GZ'
    sca_wf.connect(correlation_map, 'out_file', z_trans, 'in_file_a')
    sca_wf.connect(z_trans, 'out_file', outputnode, 'seed_based_z')
    sca_wf.connect(z_trans, 'out_file', ds, 'sca.seed_based_z')


    # # plot rs corr on surf
    # plot_rs = Node(interface=util.Function(input_names=['in_file', 'thr_list','roi_coords'],
    #                                        output_names=['out_file_list'],
    #                                        function=plot_rs_surf),
    #                name='plot_rs')
    # plot_rs.inputs.thr_list = [(.2,1)]
    # sca_wf.connect(correlation_map, 'out_file', plot_rs, 'in_file')
    # sca_wf.connect(roi_infosource, 'roi', plot_rs, 'roi_coords')




    sca_wf.write_graph(dotfilename='sca', graph2use='flat', format='pdf')


    return sca_wf

