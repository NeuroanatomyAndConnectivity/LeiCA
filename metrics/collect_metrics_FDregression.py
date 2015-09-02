__author__ = 'franzliem'



def collect_3d_metrics_run_glm_meanRegression(cfg):
    import os
    from nipype import config
    from nipype.pipeline.engine import Node, Workflow, MapNode, JoinNode
    import nipype.interfaces.utility as util
    import nipype.interfaces.io as nio
    import nipype.interfaces.fsl as fsl
    import nipype.interfaces.freesurfer as freesurfer

    # INPUT PARAMETERS

    metrics_data_dir = cfg['metrics_data_dir']
    metrics_data_suffix = cfg['metrics_data_suffix']
    metric_name = cfg['metric_name']

    demos_df = cfg['demos_df']
    qc_df = cfg['qc_df']

    working_dir = cfg['working_dir']
    ds_dir = cfg['ds_dir']
    template_dir = cfg['template_dir']

    subjects_list = cfg['subjects_list']

    use_n_procs = cfg['use_n_procs']
    plugin_name = cfg['plugin_name']


    #####################################
    # GENERAL SETTINGS
    #####################################
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')

    wf = Workflow(name='LeiCA_collect_metrics')
    wf.base_dir = os.path.join(working_dir)

    nipype_cfg = dict(logging=dict(workflow_level='DEBUG'), execution={'stop_on_first_crash': True,
                                                                       'remove_unnecessary_outputs': True,
                                                                       'job_finished_timeout': 120})
    config.update_config(nipype_cfg)
    wf.config['execution']['crashdump_dir'] = os.path.join(working_dir, 'crash')

    ds = Node(nio.DataSink(base_directory=ds_dir), name='ds')


    # get atlas data
    templates_atlases = {'GM_mask_MNI_2mm': 'SPM_GM/SPM_GM_mask_2mm.nii.gz',
                         'GM_mask_MNI_3mm': 'SPM_GM/SPM_GM_mask_3mm.nii.gz',
                         'brain_mask_MNI_3mm': 'cpac_image_resources/MNI_3mm/MNI152_T1_3mm_brain_mask.nii.gz',
                         'brain_template_MNI_3mm': 'cpac_image_resources/MNI_3mm/MNI152_T1_3mm.nii.gz'
                         }

    selectfiles_anat_templates = Node(nio.SelectFiles(templates_atlases,
                                                      base_directory=template_dir),
                                      name="selectfiles_anat_templates")

    # EXPORT SUBJECT LIST
    def export_subjects_list_fct(subjects_list):
        import os

        out_file = os.path.join(os.getcwd(), 'subject_list.txt')

        file = open(out_file, 'w')
        for subject in subjects_list:
            file.write('%s\n'%subject)
        file.close()
        return out_file



    # RESTRICT SUBJECTS LIST TO ADULTS
    def get_subjects_list_adults_fct(df_path, df_qc_path, subjects_list):
        '''
        excludes kids and subjects with missing sex or age
        '''
        import pandas as pd
        import numpy as np

        df = pd.read_pickle(df_path)
        df_qc = pd.read_pickle(df_qc_path)
        df = pd.merge(df, df_qc, left_index=True, right_index=True)
        pd.to_pickle(df, 'testdf.pkl')

        df['subject_id'] = df.subject_id_x

        # fixme exclude subjects with mean_FD>.1
        subjects_list_exclude = df[(df.age<18) | (df.mean_FD_Power>.1)].index
        subjects_list_adults = subjects_list

        for exclude_subject in subjects_list_exclude:
            if exclude_subject in subjects_list_adults:
                subjects_list_adults.remove(exclude_subject)

        missing_info = df[(df.age==999) | ((np.logical_or(df.sex=='M', df.sex=='F'))==False)].index
        for missing in missing_info:
            if missing in subjects_list_adults:
                subjects_list_adults.remove(missing)


        # remove subject from subject_list_adults for which no entry exists in df
        for subject in subjects_list_adults:
            if not(subject in df.index):
                subjects_list_adults.remove(subject)

        return subjects_list_adults


    get_subjects_list_adults = Node(util.Function(input_names=['df_path', 'df_qc_path', 'subjects_list'],
                                      output_names=['subjects_list_adults'],
                                      function=get_subjects_list_adults_fct),
                                name='get_subjects_list_adults')
    get_subjects_list_adults.inputs.df_path = demos_df
    get_subjects_list_adults.inputs.df_qc_path = qc_df
    get_subjects_list_adults.inputs.subjects_list = subjects_list



    export_subjects_list = Node(util.Function(input_names=['subjects_list'],
                                      output_names=['out_file'],
                                      function=export_subjects_list_fct),
                                name='export_subjects_list')
    wf.connect(get_subjects_list_adults, 'subjects_list_adults', export_subjects_list,'subjects_list')
    wf.connect(export_subjects_list, 'out_file', ds,'@subjects_list')


    # BUILD FILE LIST FOR MERGER
    def build_file_list_fct(prefix, subjects_list, suffix):
        import os

        out_file_list = []
        for subject in subjects_list:
            out_file_list.append(os.path.join(prefix, subject, suffix))

        return out_file_list



    build_file_list = Node(util.Function(input_names=['prefix', 'subjects_list', 'suffix'],
                                      output_names=['out_file_list'],
                                      function=build_file_list_fct),
                        name='build_file_list')
    build_file_list.inputs.prefix = metrics_data_dir
    wf.connect(get_subjects_list_adults, 'subjects_list_adults', build_file_list,'subjects_list')
    build_file_list.inputs.suffix = metrics_data_suffix



    # MERGE FILES
    merge = Node(fsl.Merge(dimension='t'), name='merge')
    wf.connect(build_file_list, 'out_file_list', merge, 'in_files')
    merge.inputs.merged_file = metric_name + '_merge.nii.gz'
    wf.connect(merge, 'merged_file', ds,'@merge')

    # GET MEAN VALUE WITHIN MASK FOR REGRESSION
    get_mean_values = Node(fsl.ImageStats(), name='get_mean_values')
    get_mean_values.inputs.op_string='-k %s -m'
    get_mean_values.inputs.split_4d=True
    wf.connect(merge, 'merged_file', get_mean_values, 'in_file')
    wf.connect(selectfiles_anat_templates, 'brain_mask_MNI_3mm', get_mean_values, 'mask_file')



    # CALC MEAN
    mean = Node(fsl.MeanImage(), name='mean')
    mean.inputs.out_file = metric_name + '_mean.nii.gz'
    wf.connect(merge, 'merged_file', mean, 'in_file')
    wf.connect(mean, 'out_file', ds,'@mean')



    # CREATE DESIGN FILES
    def create_design_files_fct(df_demographics_path, df_qc_path, subjects_list, mean_values):
        '''
        df_path: df should have columns sex ('M', 'F') & age
        function
            .restricts df to subjects_list
            .creates dummy sex vars, age**2, contrasts
            .writes mat & con files
        '''

        import pandas as pd
        import numpy as np
        import os



        df = pd.read_pickle(df_demographics_path)

        df_qc = pd.read_pickle(df_qc_path)
        df = pd.merge(df, df_qc, left_index=True, right_index=True)


        df['dummy_m'] = (df.sex == 'M').astype('int')
        df['dummy_f'] = (df.sex == 'F').astype('int')
        df['age2'] = df.age**2
        df_use = df.loc[subjects_list]
        df_use['mean_values'] = mean_values


        #fixme
        mat = df_use[['dummy_m', 'dummy_f', 'age','mean_FD_Power']].values

        mat_str = [
            '/NumWaves %s'%str(mat.shape[1]),
            '/NumPoints %s'%str(mat.shape[0]),
            '/Matrix'
        ]

        n_cons = 6
        cons_str = [
            '/ContrastName1 pos_age',
            '/ContrastName2 neg_age',
            '/ContrastName3 m>f',
            '/ContrastName4 f>m',
            '/ContrastName5 pos_mean_FD_Power',
            '/ContrastName6 neg_mean_FD_Power',
            '/NumWaves %s'%str(mat.shape[1]),
            '/NumContrasts %s'%str(n_cons),
            '',
            '/Matrix',
            '0 0 1 0',
            '0 0 -1 0',
            '1 -1 0 0',
            '-1 1 0 0',
            '0 0 0 1',
            '0 0 0 -1'
            ]


        # mat = df_use[['dummy_m', 'dummy_f', 'age', 'age2','mean_FD_Power']].values
        #
        # mat_str = [
        #     '/NumWaves %s'%str(mat.shape[1]),
        #     '/NumPoints %s'%str(mat.shape[0]),
        #     '/Matrix'
        # ]
        #
        # n_cons = 10
        # cons_str = [
        #     '/ContrastName1 pos_age',
        #     '/ContrastName2 pos_age2',
        #     '/ContrastName3 pos_age+age2',
        #     '/ContrastName4 neg_age',
        #     '/ContrastName5 neg_age2',
        #     '/ContrastName6 neg_age+age2',
        #     '/ContrastName7 m>f',
        #     '/ContrastName8 f>m',
        #     '/ContrastName9 pos_mean_FD_Power',
        #     '/ContrastName10 neg_mean_FD_Power',
        #     '/NumWaves %s'%str(mat.shape[1]),
        #     '/NumContrasts %s'%str(n_cons),
        #     '',
        #     '/Matrix',
        #     '0 0 1 0 0',
        #     '0 0 0 1 0',
        #     '0 0 .5 .5 0',
        #     '0 0 -1 0 0',
        #     '0 0 0 -1 0',
        #     '0 0 -.5 -.5 0',
        #     '1 -1 0 0 0',
        #     '1 1 0 0 0',
        #     '0 0 0 0 1',
        #     '0 0 0 0 -1'
        #     ]
        #

        mat_file = os.path.join(os.getcwd(), 'design.mat')
        mat_file_numerical = os.path.join(os.getcwd(), 'design_mat_num.txt')
        con_file = os.path.join(os.getcwd(), 'design.con')
        df_used_file = os.path.join(os.getcwd(), 'df_used.csv')

        # mat_str_out = ''
        # for line in mat_str:
        #     mat_str_out = mat_str_out[:] + line + '\n'

        np.savetxt(mat_file_numerical, mat)
        num_file = open(mat_file_numerical, 'r')
        nums_str = num_file.read()
        num_file.close()

        out_file = open(mat_file, 'w')
        for line in mat_str:
            out_file.write('%s\n' % line)
        out_file.write(nums_str)
        out_file.close()

        out_file = open(con_file, 'w')
        for line in cons_str:
            out_file.write('%s\n' % line)
        out_file.close()

        df_use.to_csv(df_used_file)

        return mat_file, con_file, df_used_file, n_cons


    create_design_files = Node(util.Function(input_names=['df_demographics_path', 'df_qc_path', 'subjects_list', 'mean_values'],
                                      output_names=['mat_file', 'con_file', 'df_used_file', 'n_cons'],
                                      function=create_design_files_fct),
                        name='create_design_files')
    create_design_files.inputs.df_demographics_path = demos_df
    create_design_files.inputs.df_qc_path = qc_df
    wf.connect(get_subjects_list_adults, 'subjects_list_adults', create_design_files,'subjects_list')
    wf.connect(get_mean_values, 'out_stat', create_design_files,'mean_values')
    wf.connect(create_design_files,'df_used_file', ds,'glm.@df_used')



    smooth = Node(fsl.utils.Smooth(fwhm=4), name='smooth')
    wf.connect(merge, 'merged_file', smooth, 'in_file')



    def run_randomise_fct(data_file, mat_file, con_file, mask_file):
        import os
        out_dir = os.path.join(os.getcwd(), 'glm')
        os.mkdir(out_dir)
        cmd_str = 'randomise -i %s -o glm/glm -d %s -t %s -m %s -n 500 -D -T' %(data_file,mat_file, con_file, mask_file)
        file = open('command.txt', 'w')
        file.write(cmd_str)
        file.close()
        os.system(cmd_str)

        return out_dir



    run_randomise = Node(util.Function(input_names=['data_file', 'mat_file', 'con_file', 'mask_file'],
                                      output_names=['out_dir'],
                                      function=run_randomise_fct),
                        name='run_randomise')
    #fixme
    #wf.connect(merge, 'merged_file', run_randomise, 'data_file')
    wf.connect(smooth, 'smoothed_file', run_randomise, 'data_file')
    wf.connect(create_design_files, 'mat_file', run_randomise, 'mat_file')
    wf.connect(create_design_files, 'con_file', run_randomise, 'con_file')
    #wf.connect(selectfiles_anat_templates, 'GM_mask_MNI_3mm', run_randomise, 'mask_file')
    wf.connect(selectfiles_anat_templates, 'brain_mask_MNI_3mm', run_randomise, 'mask_file')



    def create_renders_fct(randomise_dir, n_cons, background_img):
        import os
        thresh = .95
        out_files_list = []
        corr_list = ['glm_tfce_corrp_tstat', 'glm_tfce_p_tstat']
        for corr in corr_list:
            for con in range(1,n_cons+1):
                output_root = corr + str(con)
                in_file = os.path.join(randomise_dir, output_root + '.nii.gz')
                out_file = os.path.join(os.getcwd(), 'rendered_' + output_root + '.png')
                out_files_list.append(out_file)
                cmd_str = 'easythresh %s %s %s %s' % (in_file, str(thresh), background_img, output_root)

                file = open('command.txt', 'w')
                file.write(cmd_str)
                file.close()

                os.system(cmd_str)
        return out_files_list

    create_renders = Node(util.Function(input_names=['randomise_dir', 'n_cons', 'background_img'],
                                        output_names=['out_files_list'],
                                        function=create_renders_fct),
                          name='create_renders')
    wf.connect(run_randomise, 'out_dir', create_renders, 'randomise_dir')
    wf.connect(create_design_files, 'n_cons', create_renders, 'n_cons')
    wf.connect(selectfiles_anat_templates, 'brain_template_MNI_3mm', create_renders, 'background_img')
    wf.connect(create_renders, 'out_files_list', ds, 'glm.@renders')

    wf.write_graph(dotfilename=wf.name, graph2use='colored', format='pdf')  # 'hierarchical')
    wf.write_graph(dotfilename=wf.name, graph2use='orig', format='pdf')
    wf.write_graph(dotfilename=wf.name, graph2use='flat', format='pdf')

    if plugin_name == 'CondorDAGMan':
        wf.run(plugin=plugin_name)
    if plugin_name == 'MultiProc':
        wf.run(plugin=plugin_name, plugin_args={'n_procs': use_n_procs})
