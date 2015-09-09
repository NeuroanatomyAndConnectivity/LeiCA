def extract_parcellation_time_series(in_data, parcellation_name, parcellations_dict, bp_freqs, tr):
    '''
    Depending on parcellation['is_probabilistic'] this function chooses either NiftiLabelsMasker or NiftiMapsMasker
    to extract the time series of each parcel
    if bp_freq: data is band passfiltered at (hp, lp), if (None,None): no filter, if (None, .1) only lp...
    tr in ms (e.g. from freesurfer ImageInfo())
    returns np.array with parcellation time series and saves this array also to parcellation_time_series_file, and
    path to pickled masker object
    '''
    from nilearn.input_data import NiftiLabelsMasker, NiftiMapsMasker
    import os, pickle
    import numpy as np

    print(parcellations_dict)
    if parcellations_dict[parcellation_name]['is_probabilistic']:  # use probab. nilearn
        masker = NiftiMapsMasker(maps_img=parcellations_dict[parcellation_name]['nii_path'])
    else:  # 0/1 labels
        masker = NiftiLabelsMasker(labels_img=parcellations_dict[parcellation_name]['nii_path'])

    # add bandpass filter (only executes if freq not None
    hp, lp = bp_freqs
    masker.low_pass = lp
    masker.high_pass = hp
    if tr is not None:
        masker.t_r = float(tr) / 1000.
    else:
        masker.t_r = None

    masker.standardize = True

    masker_file = os.path.join(os.getcwd(), 'masker.pkl')
    with open(masker_file, 'w') as f:
        pickle.dump(masker, f)

    parcellation_time_series = masker.fit_transform(in_data)

    parcellation_time_series_file = os.path.join(os.getcwd(), 'parcellation_time_series.npy')
    np.save(parcellation_time_series_file, parcellation_time_series)

    return parcellation_time_series, parcellation_time_series_file, masker_file


def calculate_connectivity_matrix(in_data, extraction_method):
    '''
    after extract_parcellation_time_series() connectivity matrices are calculated via specified extraction method

    returns np.array with matrixand saves this array also to matrix_file
    '''

    # fixme implement sparse inv covar
    import os
    import numpy as np

    if extraction_method == 'correlation':
        correlation_matrix = np.corrcoef(in_data.T)
        matrix = {'correlation': correlation_matrix}

    if extraction_method == 'sparse_inverse_covariance':
        # Compute the sparse inverse covariance
        from sklearn.covariance import GraphLassoCV
        estimator = GraphLassoCV()
        estimator.fit(in_data)
        matrix = {'covariance': estimator.covariance_,
                  'sparse_inverse_covariance': estimator.precision_}

    else:
        raise (Exception('Unknown extraction method: %s' % extraction_method))

    # load with matrix = np.load('matrix.npy')[np.newaxis][0]
    matrix_file = os.path.join(os.getcwd(), 'matrix.npy')
    np.save(matrix_file, matrix)
    return matrix, matrix_file


#####################################
# WORKFLOW
#####################################
def connectivity_matrix_wf(time_series_file,
                           working_dir,
                           ds_dir,
                           parcellations_dict,
                           extraction_methods_list,
                           bp_freq_list,
                           use_n_procs,
                           plugin_name):
    '''
    Uses nilearn to calculate connectivity matrices
    parcellations_list: list of dicts with keys: name, nii, is_probabilistic
    bp_freq_list: list of tuples of bp cutoff frequencies (hp, lp). e.g. [(), (0.01, 0.1)]. empty tuple-> no bp filter
    '''

    import os
    from nipype import config
    from nipype.pipeline.engine import Node, Workflow, MapNode
    import nipype.interfaces.utility as util
    import nipype.interfaces.io as nio
    from nipype.interfaces.freesurfer.utils import ImageInfo



    #####################################
    # GENERAL SETTINGS
    #####################################
    wf = Workflow(name='calc_con_mats')
    wf.base_dir = os.path.join(working_dir)

    nipype_cfg = dict(logging=dict(workflow_level='DEBUG'), execution={'stop_on_first_crash': True,
                                                                       'remove_unnecessary_outputs': True,
                                                                       'job_finished_timeout': 120})
    config.update_config(nipype_cfg)
    wf.config['execution']['crashdump_dir'] = os.path.join(working_dir, 'crash')

    ds = Node(nio.DataSink(base_directory=ds_dir), name='ds')
    ds.inputs.regexp_substitutions = [
        ('subject_id_', ''),
        ('_parcellation_', ''),
        ('_bp_freqs_', 'bp_'),
        ('_extraction_method_', '')]  # [('_variabilty_MNIspace_3mm[0-9]*/', ''), ('_z_score[0-9]*/', '')]


    #####################################
    # SET ITERATORS
    #####################################

    # PARCELLATION ITERATOR
    parcellation_infosource = Node(util.IdentityInterface(fields=['parcellation']), name='parcellation_infosource')
    parcellation_infosource.iterables = ('parcellation', parcellations_dict.keys())

    # BP FILTER ITERATOR
    bp_filter_infosource = Node(util.IdentityInterface(fields=['bp_freqs']), name='bp_filter_infosource')
    bp_filter_infosource.iterables = ('bp_freqs', bp_freq_list)

    # EXTRACTION METHOD ITERATOR
    extraction_method_infosource = Node(util.IdentityInterface(fields=['extraction_method']),
                                        name='extraction_method_infosource')
    extraction_method_infosource.iterables = ('extraction_method', extraction_methods_list)

    ##############
    ## extract ts
    ##############
    # returns TR in ms
    get_TR = Node(ImageInfo(), name='get_TR')
    get_TR.inputs.in_file = time_series_file

    parcellated_ts = Node(
        util.Function(input_names=['in_data', 'parcellation_name', 'parcellations_dict', 'bp_freqs', 'tr'],
                      output_names=['parcellation_time_series', 'parcellation_time_series_file', 'masker_file'],
                      function=extract_parcellation_time_series),
        name='parcellated_ts')
    parcellated_ts.inputs.in_data = time_series_file
    parcellated_ts.inputs.parcellations_dict = parcellations_dict
    wf.connect(parcellation_infosource, 'parcellation', parcellated_ts, 'parcellation_name')
    wf.connect(bp_filter_infosource, 'bp_freqs', parcellated_ts, 'bp_freqs')
    wf.connect(get_TR, 'TR', parcellated_ts, 'tr')




    ##############
    ## get conmat
    ##############
    con_mat = Node(util.Function(input_names=['in_data', 'extraction_method'],
                                 output_names=['matrix', 'matrix_file'],
                                 function=calculate_connectivity_matrix),
                   name='con_mat')
    wf.connect(parcellated_ts, 'parcellation_time_series', con_mat, 'in_data')
    wf.connect(extraction_method_infosource, 'extraction_method', con_mat, 'extraction_method')


    ##############
    ## ds
    ##############

    wf.connect(parcellated_ts, 'parcellation_time_series_file', ds, 'con_mats.parcellated_time_series.@parc_ts')
    wf.connect(parcellated_ts, 'masker_file', ds, 'con_mats.parcellated_time_series.@masker')
    wf.connect(con_mat, 'matrix_file', ds, 'con_mats.matrix.@mat')



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
