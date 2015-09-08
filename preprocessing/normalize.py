
def normalize_epi(in_data,
                  ref_data,
                  warpfield,
                  save_name,
                  working_dir,
                  ds_dir,
                  plugin_name,
                  use_n_procs):

    import os
    from nipype import config
    from nipype.pipeline.engine import Node, Workflow
    import nipype.interfaces.io as nio
    from nipype.interfaces import fsl


    #####################################
    # GENERAL SETTINGS
    #####################################
    wf = Workflow(name='normalize')
    wf.base_dir = os.path.join(working_dir)

    nipype_cfg = dict(logging=dict(workflow_level='DEBUG'), execution={'stop_on_first_crash': True,
                                                                       'remove_unnecessary_outputs': True,
                                                                       'job_finished_timeout': 120})
    config.update_config(nipype_cfg)
    wf.config['execution']['crashdump_dir'] = os.path.join(working_dir, 'crash')


    ds = Node(nio.DataSink(base_directory=ds_dir), name='ds')
    # ds.inputs.regexp_substitutions = [
    #     ('subject_id_', '')]  # [('_variabilty_MNIspace_3mm[0-9]*/', ''), ('_z_score[0-9]*/', '')]


    # fixme
    # CREATE TS IN MNI SPACE
    # is it ok to apply the 2mm warpfield to the 3mm template?
    # seems ok: https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=ind0904&L=FSL&P=R14011&1=FSL&9=A&J=on&d=No+Match%3BMatch%3BMatches&z=4
    epi_MNI = Node(fsl.ApplyWarp(), name='epi_MNI')
    epi_MNI.inputs.interp = 'spline'
    epi_MNI.plugin_args = {'submit_specs': 'request_memory = 4000'} #{'dagman_args': 'request_memory = 4000'}
    epi_MNI.inputs.in_file = in_data
    epi_MNI.inputs.ref_file = fsl.Info.standard_image(ref_data)
    epi_MNI.inputs.field_file = warpfield


    wf.connect(epi_MNI, 'out_file', ds, save_name)


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
