__author__ = 'franzliem'

    # fs_source = Node(interface=nio.FreeSurferSource(), name='fs_source')
    # fs_source.inputs.subjects_dir = freesurfer_dir
    # reg_wf.connect(inputnode, 'subject_id', fs_source, 'subject_id')
    #
    # # 3. EXTRACT FS -> STRUCT MAT
    # fs_2_struct_mat = Node(util.Function(input_names=['moving_image', 'target_image'],
    #                                      output_names=['fsl_file'],
    #                                      function=tkregister2_fct),
    #                        name='fs_2_struct_mat')
    #
    # reg_wf.connect([(fs_source, fs_2_struct_mat, [('T1', 'moving_image'),
    #                                               ('rawavg','target_image')])])
    #
    # reg_wf.connect(fs_2_struct_mat, 'fsl_file', outputnode, 'fs_2_struct_mat')
    #
    #
    # # 4. REGISTER EPI -> FS with BBREGISTER
    # epi_2_fs_mat = Node(interface=freesurfer.BBRegister(init='fsl',
    #                                                     contrast_type='t2',
    #                                                     registered_file=True,
    #                                                     out_fsl_file=True),
    #                     name='epi_2_fs_mat')
    #
    # reg_wf.connect(inputnode, 'mean_epi_moco', epi_2_fs_mat, 'source_file')
    # reg_wf.connect(inputnode, 'subject_id', epi_2_fs_mat, 'subject_id')
    #
    #
    #
    # # 5. COMBINE MATS: EPI -> FS -> STRUCT
    # epi_2_struct_mat = Node(fsl.ConvertXFM(concat_xfm=True), name='epi_2_struct_mat')
    # reg_wf.connect(epi_2_fs_mat, 'out_fsl_file', epi_2_struct_mat, 'in_file')
    # reg_wf.connect(fs_2_struct_mat, 'fsl_file', epi_2_struct_mat, 'in_file2')
    # reg_wf.connect(epi_2_struct_mat, 'out_file', outputnode, 'epi_2_struct_mat')
    # # output: out_file
    #
    #
    # # 6. INVERT to get: STRUCT -> EPI
    # struct_2_epi_mat = Node(fsl.ConvertXFM(invert_xfm=True), name='struct_2_epi_mat')
    # reg_wf.connect(epi_2_struct_mat, 'out_file', struct_2_epi_mat, 'in_file')
    # reg_wf.connect(struct_2_epi_mat, 'out_file', outputnode, 'struct_2_epi_mat')
    # # output: out_file
    #




    # # CREATE EPI IN FS SPACE FOR DEBUGGING
    # fs_2_nii = Node(freesurfer.MRIConvert(out_type='niigz', out_file='T1.nii.gz'), name='fs_2_nii')
    # reg_wf.connect(fs_source, 'T1', fs_2_nii, 'in_file')
    #
    # epi_2_fs_trans = Node(fsl.ApplyXfm(), name='epi_2_fs_trans')
    # reg_wf.connect(inputnode, 'mean_epi_moco', epi_2_fs_trans, 'in_file')
    # reg_wf.connect(fs_2_nii, 'out_file', epi_2_fs_trans, 'reference')
    # reg_wf.connect(epi_2_fs_mat, 'out_fsl_file', epi_2_fs_trans, 'in_matrix_file')
    # reg_wf.connect(epi_2_fs_trans, 'out_file', ds, 'registration.epi_fsSpace')
    #
    # # CREATE EPI IN FS SPACE FOR DEBUGGING (BBR)
    # epi_2_struct_bbr_trans = Node(fsl.ApplyXfm(), name='epi_2_struct_bbr_trans')
    # reg_wf.connect(inputnode, 'mean_epi_moco', epi_2_struct_bbr_trans, 'in_file')
    # reg_wf.connect(inputnode, 't1w_brain', epi_2_struct_bbr_trans, 'reference')
    # reg_wf.connect(epi_2_struct_mat, 'out_file', epi_2_struct_bbr_trans, 'in_matrix_file')
    # reg_wf.connect(epi_2_struct_bbr_trans, 'out_file', ds, 'registration.epi_structSpace_bbr')




    #
    # ## CREATE SLICES OVERLAY
    # slices_epi_structSpace = Node(util.Function(input_names=['in_file', 'in_file2'], output_names=['out_file'],
    #                                function=fsl_slices_fct), name='slices_epi_structSpace')
    # reg_wf.connect(epi_2_struct_bbr_mat, 'out_file', slices_epi_structSpace, 'in_file')
    # reg_wf.connect(inputnode, 't1w_brain', slices_epi_structSpace, 'in_file2')
    # reg_wf.connect(slices_epi_structSpace, 'out_file', ds, 'QC.slices.epi_structSpace')
    #
    #
    #
    # slices_epi_MNIspace = Node(util.Function(input_names=['in_file', 'in_file2'], output_names=['out_file'],
    #                                function=fsl_slices_fct), name='slices_epi_MNIspace')
    # slices_epi_MNIspace.inputs.in_file2 = fsl.Info.standard_image('MNI152_T1_2mm_brain.nii.gz')
    # reg_wf.connect(epi_2_MNI_trans, 'out_file', slices_epi_MNIspace, 'in_file')
    # reg_wf.connect(slices_epi_MNIspace, 'out_file', ds, 'QC.slices.epi_MNIspace')
    #
    #
    #
    # slices_struct_MNIspace = Node(util.Function(input_names=['in_file', 'in_file2'], output_names=['out_file'],
    #                                function=fsl_slices_fct), name='slices_struct_MNIspace')
    # reg_wf.connect(struct_2_MNI_warp, 'warped_file', slices_struct_MNIspace, 'in_file')
    # slices_struct_MNIspace.inputs.in_file2 = fsl.Info.standard_image('MNI152_T1_2mm_brain.nii.gz')
    # reg_wf.connect(slices_struct_MNIspace, 'out_file', ds, 'QC.slices.struct_MNIspace')
    #
    #
    #
    # def similarity_to_file_fct(similarity):
    #     import os
    #     import numpy as np
    #     out_file = os.path.join(os.getcwd(), 'similarity.txt')
    #     np.savetxt(out_file, np.array(similarity))
    #     return out_file
    #
    #
    # # CALCULATE SIMILARITY FOR QC
    # similarity_epi_struct = Node(interface = Similarity(metric = 'nmi'),
    #                              name = 'similarity_epi_struct')
    # reg_wf.connect(epi_2_struct_bbr_mat, 'out_file', similarity_epi_struct, 'volume1')
    # reg_wf.connect(inputnode, 't1w_brain', similarity_epi_struct, 'volume2')
    # reg_wf.connect(inputnode, 'struct_brain_mask', similarity_epi_struct, 'mask1')
    # reg_wf.connect(inputnode, 'struct_brain_mask', similarity_epi_struct, 'mask2')
    #
    #
    # similarity_epi_struct_txt = Node(util.Function(input_names=['similarity'],
    #                                                output_names=['out_file'],
    #                                                function=similarity_to_file_fct),
    #                                  name='similarity_epi_struct_txt')
    # reg_wf.connect(similarity_epi_struct, 'similarity', similarity_epi_struct_txt, 'similarity')
    # reg_wf.connect(similarity_epi_struct_txt, 'out_file', ds, 'QC.similarity.epi_struct')
    #
    #
    #
    #
    #
    # similarity_struct_MNI = Node(interface = Similarity(metric = 'nmi'),
    #                              name = 'similarity_struct_MNI')
    # reg_wf.connect(struct_2_MNI_trans, 'out_file', similarity_struct_MNI, 'volume1')
    # similarity_struct_MNI.inputs.volume2 = fsl.Info.standard_image('MNI152_T1_2mm_brain.nii.gz')
    #
    #
    # similarity_struct_MNI_txt = Node(util.Function(input_names=['similarity'],
    #                                                output_names=['out_file'],
    #                                                function=similarity_to_file_fct),
    #                                  name='similarity_struct_MNI_txt')
    # reg_wf.connect(similarity_struct_MNI, 'similarity', similarity_struct_MNI_txt, 'similarity')
    # reg_wf.connect(similarity_struct_MNI_txt, 'out_file', ds, 'QC.similarity.struct_MNI')


    # ####### CALC SIMILARITY #####
    # metrics_list = ['mi','nmi','cr']
    # similarity_bbr = MapNode(interface = Similarity(),
    #                   name = 'similarity_bbr',
    #                   iterfield=['metric'])
    # similarity_bbr.inputs.metric = metrics_list
    #
    # reg_wf.connect(epi_2_struct_bbr_trans, 'out_file', similarity_bbr, 'volume1')
    # reg_wf.connect(inputnode, 't1w_brain', similarity_bbr, 'volume2')
    #
    # similarity_flirt6 = similarity_bbr.clone(name='similarity_flirt6')
    # reg_wf.connect(epi_2_struct_flirt6_mat, 'out_file', similarity_flirt6, 'volume1')
    # reg_wf.connect(inputnode, 't1w_brain', similarity_flirt6, 'volume2')
    #
    # similarity_flirt7 = similarity_bbr.clone(name='similarity_flirt7')
    # reg_wf.connect(epi_2_struct_flirt7_mat, 'out_file', similarity_flirt7, 'volume1')
    # reg_wf.connect(inputnode, 't1w_brain', similarity_flirt7, 'volume2')
    #
    # similarity_flirt9 = similarity_bbr.clone(name='similarity_flirt9')
    # reg_wf.connect(epi_2_struct_flirt9_mat, 'out_file', similarity_flirt9, 'volume1')
    # reg_wf.connect(inputnode, 't1w_brain', similarity_flirt9, 'volume2')
    #
    # similarity_flirt12 = similarity_bbr.clone(name='similarity_flirt12')
    # reg_wf.connect(epi_2_struct_flirt12_mat, 'out_file', similarity_flirt12, 'volume1')
    # reg_wf.connect(inputnode, 't1w_brain', similarity_flirt12, 'volume2')
    #
    # similarity_flirt6MI = similarity_bbr.clone(name='similarity_flirt6MI')
    # reg_wf.connect(epi_2_struct_flirt6MI_mat, 'out_file', similarity_flirt6MI, 'volume1')
    # reg_wf.connect(inputnode, 't1w_brain', similarity_flirt6MI, 'volume2')
    #
    # similarity_bbrMI = similarity_bbr.clone(name='similarity_bbrMI')
    # reg_wf.connect(epi_2_struct_bbrMI_mat, 'out_file', similarity_bbrMI, 'volume1')
    # reg_wf.connect(inputnode, 't1w_brain', similarity_bbrMI, 'volume2')
    #
    #
    # # write values to one text file per subject
    # def write_text_fct(similarity_bbr, similarity_flirt6, similarity_flirt7,similarity_flirt9,similarity_flirt12,similarity_flirt6MI, similarity_bbrMI):
    #     '''
    #     writes file of format:
    #     bbr_mi  flirt6_mi ...
    #     bbr_nmi ..
    #     bbr_cr ..
    #
    #     '''
    #     import numpy as np
    #     import os
    #     filename = os.path.join(os.getcwd(), 'similarity.txt')
    #     similarity_bbr_array = np.array(similarity_bbr)
    #     similarity_bbr_array=similarity_bbr_array.reshape(np.size(similarity_bbr_array),1)
    #
    #     similarity_flirt6_array = np.array(similarity_flirt6)
    #     similarity_flirt6_array=similarity_flirt6_array.reshape(np.size(similarity_flirt6_array),1)
    #     similarity_flirt7_array = np.array(similarity_flirt7)
    #     similarity_flirt7_array=similarity_flirt7_array.reshape(np.size(similarity_flirt7_array),1)
    #     similarity_flirt9_array = np.array(similarity_flirt9)
    #     similarity_flirt9_array=similarity_flirt9_array.reshape(np.size(similarity_flirt9_array),1)
    #     similarity_flirt12_array = np.array(similarity_flirt12)
    #     similarity_flirt12_array=similarity_flirt12_array.reshape(np.size(similarity_flirt12_array),1)
    #
    #     similarity_flirt6MI_array = np.array(similarity_flirt6MI)
    #     similarity_flirt6MI_array=similarity_flirt6MI_array.reshape(np.size(similarity_flirt6MI_array),1)
    #
    #     similarity_bbrMI_array = np.array(similarity_bbrMI)
    #     similarity_bbrMI_array=similarity_bbrMI_array.reshape(np.size(similarity_bbrMI_array),1)
    #
    #
    #     metrics=np.concatenate((similarity_bbr_array, similarity_flirt6_array, similarity_flirt7_array, similarity_flirt9_array, similarity_flirt12_array, similarity_flirt6MI_array, similarity_bbrMI_array),axis=1)
    #     np.savetxt(filename, metrics, delimiter=' ', fmt='%f')
    #     return os.path.abspath(filename)
    #
    # write_txt = Node(interface=util.Function(input_names=['similarity_bbr', 'similarity_flirt6', 'similarity_flirt7', 'similarity_flirt9','similarity_flirt12', 'similarity_flirt6MI', 'similarity_bbrMI'],
    #                                    output_names=['out_file'],
    #                                    function=write_text_fct),
    #                 name='write_file')
    #
    # reg_wf.connect(similarity_bbr, 'similarity', write_txt, 'similarity_bbr')
    # reg_wf.connect(similarity_flirt6, 'similarity', write_txt, 'similarity_flirt6')
    # reg_wf.connect(similarity_flirt7, 'similarity', write_txt, 'similarity_flirt7')
    # reg_wf.connect(similarity_flirt9, 'similarity', write_txt, 'similarity_flirt9')
    # reg_wf.connect(similarity_flirt12, 'similarity', write_txt, 'similarity_flirt12')
    # reg_wf.connect(similarity_bbrMI, 'similarity', write_txt, 'similarity_bbrMI')
    # reg_wf.connect(similarity_flirt6MI, 'similarity', write_txt, 'similarity_flirt6MI')
