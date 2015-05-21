__author__ = 'franzliem'

def preprocessing_pipeline(cfg):
    import os

    from nipype import config
    from nipype.pipeline.engine import Node, Workflow, JoinNode
    import nipype.interfaces.utility as util
    import nipype.interfaces.io as nio
    import nipype.interfaces.fsl as fsl
    import nipype.interfaces.freesurfer as freesurfer

    # LeiCA modules
    from utils import zip_and_save_running_scripts
    from preprocessing.rsfMRI_preprocessing import create_rsfMRI_preproc_pipeline
    from preprocessing.converter import create_converter_structural_pipeline, create_converter_functional_pipeline, \
        create_converter_diffusion_pipeline
    from sca import create_sca_pipeline

    # INPUT PARAMETERS
    dicom_dir = cfg['dicom_dir']
    working_dir = cfg['working_dir']
    freesurfer_dir = cfg['freesurfer_dir']
    template_dir = cfg['template_dir']
    script_dir = cfg['script_dir']
    ds_dir = cfg['ds_dir']

    subject_id = cfg['subject_id']
    TR_list = cfg['TR_list']

    vols_to_drop = cfg['vols_to_drop']
    rois_list = cfg['rois_list']
    lp_cutoff_freq = cfg['lp_cutoff_freq']
    hp_cutoff_freq = cfg['hp_cutoff_freq']
    use_fs_brainmask = cfg['use_fs_brainmask']

    use_n_procs = cfg['use_n_procs']
    plugin_name = cfg['plugin_name']


    #####################################
    # GENERAL SETTINGS
    #####################################
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    freesurfer.FSCommand.set_default_subjects_dir(freesurfer_dir)

    wf = Workflow(name='LeiCA_resting')
    wf.base_dir = os.path.join(working_dir)

    nipype_cfg = dict(logging=dict(workflow_level = 'DEBUG'), execution={'stop_on_first_crash': True,
                                                                  'remove_unnecessary_outputs': True,
                                                                  'job_finished_timeout': 120})
    config.update_config(nipype_cfg)
    wf.config['execution']['crashdump_dir'] = os.path.join(working_dir, 'crash')

    ds = Node(nio.DataSink(base_directory=ds_dir), name='ds')


    #####################################
    # SET ITERATORS
    #####################################
    # GET SCAN TR_ID ITERATOR
    scan_infosource = Node(util.IdentityInterface(fields=['TR_id']), name='scan_infosource')
    scan_infosource.iterables = ('TR_id', TR_list)




    #####################################
    # FETCH MRI DATA
    #####################################
    # GET LATERAL VENTRICLE MASK
    templates_atlases = {'lat_ventricle_mask_MNI': 'HarvardOxford-lateral-ventricles-thr25-2mm.nii.gz'}
    selectfiles_templates = Node(nio.SelectFiles(templates_atlases,
                                                 base_directory=template_dir),
                                 name="selectfiles_templates")


    # GET FUNCTIONAL DATA
    templates_funct = {'funct_dicom': '{subject_id}/session_1/RfMRI_*_{TR_id}'}

    selectfiles_funct = Node(nio.SelectFiles(templates_funct,
                                             base_directory=dicom_dir),
                             name="selectfiles_funct")
    selectfiles_funct.inputs.subject_id = subject_id

    wf.connect(scan_infosource, 'TR_id', selectfiles_funct, 'TR_id')


    # GET STRUCTURAL DATA
    templates_struct = {'t1w_dicom': '{subject_id}/anat',
                        'dMRI_dicom': '{subject_id}/session_1/DTI_mx_137/*.dcm'} # *.dcm for dMRI as Dcm2nii requires this

    selectfiles_struct = Node(nio.SelectFiles(templates_struct,
                                              base_directory=dicom_dir),
                              name="selectfiles_struct")
    selectfiles_struct.inputs.subject_id = subject_id




    #####################################
    # COPY RUNNING SCRIPTS
    #####################################
    copy_scripts = Node(util.Function(input_names=['subject_id', 'script_dir'], output_names=['zip_file'], function=zip_and_save_running_scripts), name='copy_scripts')
    copy_scripts.inputs.script_dir = script_dir
    copy_scripts.inputs.subject_id = subject_id
    wf.connect(copy_scripts, 'zip_file', ds, 'scripts')



    #####################################
    # CONVERT DICOMs
    #####################################
    # CONVERT STRUCT 2 NIFTI
    converter_struct = create_converter_structural_pipeline(working_dir, ds_dir, 'converter_struct')
    wf.connect(selectfiles_struct, 't1w_dicom', converter_struct, 'inputnode.t1w_dicom')

    # CONVERT dMRI 2 NIFTI
    converter_dMRI = create_converter_diffusion_pipeline(working_dir, ds_dir, 'converter_dMRI')
    wf.connect(selectfiles_struct, 'dMRI_dicom', converter_dMRI, 'inputnode.dMRI_dicom')


    # CONVERT FUNCT 2 NIFTI
    converter_funct = create_converter_functional_pipeline(working_dir, ds_dir, 'converter_funct')
    wf.connect(selectfiles_funct, 'funct_dicom', converter_funct, 'inputnode.epi_dicom')
    wf.connect(scan_infosource, 'TR_id', converter_funct, 'inputnode.out_format')



    #####################################
    # START RSFMRI PREPROCESSING ANALYSIS
    #####################################
    # rsfMRI PREPROCESSING
    rsfMRI_preproc = create_rsfMRI_preproc_pipeline(working_dir,freesurfer_dir, ds_dir, use_fs_brainmask, 'rsfMRI_preprocessing')
    rsfMRI_preproc.inputs.inputnode.vols_to_drop = vols_to_drop
    rsfMRI_preproc.inputs.inputnode.lp_cutoff_freq = lp_cutoff_freq
    rsfMRI_preproc.inputs.inputnode.hp_cutoff_freq = hp_cutoff_freq
    rsfMRI_preproc.inputs.inputnode.subject_id = subject_id

    wf.connect(converter_struct, 'outputnode.t1w', rsfMRI_preproc, 'inputnode.t1w')
    wf.connect(converter_funct, 'outputnode.epi', rsfMRI_preproc, 'inputnode.epi')
    wf.connect(converter_funct, 'outputnode.TR_ms', rsfMRI_preproc, 'inputnode.TR_ms')
    #wf.connect(subjects_infosource, 'subject_id', rsfMRI_preproc, 'inputnode.subject_id')
    wf.connect(selectfiles_templates, 'lat_ventricle_mask_MNI', rsfMRI_preproc, 'inputnode.lat_ventricle_mask_MNI')





    #####################################
    # SCA
    #####################################

    sca = create_sca_pipeline(working_dir, rois_list, ds_dir, name='sca')
    wf.connect(rsfMRI_preproc, 'outputnode.rs_preprocessed', sca, 'inputnode.rs_preprocessed')
    wf.connect(rsfMRI_preproc, 'outputnode.epi_2_MNI_warp', sca, 'inputnode.epi_2_MNI_warp')

    # if len(subjects_list)>1:
    #     def test_fct(in_files):
    #         print('cxcxcx')
    #         print in_files
    #         out_files = in_files
    #         return out_files
    #
    #     collect_files = JoinNode(util.Function(input_names=['in_files'],
    #                                   output_names=['out_files'],
    #                                   function=test_fct),
    #                            joinsource='subjects_infosource', #'selectfiles_funct',
    #                            joinfield='in_files',
    #                     name='collect_files')
    #     wf.connect(sca, 'outputnode.seed_based_z', collect_files, 'in_files')
    #
    #
    #     collect_sca = Node(fsl.Merge(dimension='t', merged_file='concat_corr_z.nii.gz'),
    #                            joinsource='subjects_infosource', #'selectfiles_funct',
    #                            joinfield='in_files',
    #                            name='collect_sca')
    #     wf.connect(collect_files, 'out_files', collect_sca, 'in_files')
    #
    #     mean_sca = Node(fsl.MeanImage(), name='mean_sca')
    #     wf.connect(collect_sca, 'merged_file', mean_sca, 'in_file')



    #####################################
    # RUN WF
    #####################################
    wf.write_graph(dotfilename=wf.name, graph2use='colored', format='pdf')  # 'hierarchical')
    wf.write_graph(dotfilename=wf.name, graph2use='orig', format='pdf')
    wf.write_graph(dotfilename=wf.name, graph2use='flat', format='pdf')

    if plugin_name == 'CondorDAGMan':
        wf.run(plugin=plugin_name)
    if plugin_name == 'MultiProc':
        wf.run(plugin=plugin_name, plugin_args={'n_procs': use_n_procs})
