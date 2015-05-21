import os

from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.fsl as fsl
import nipype.interfaces.utility as util
import nipype.algorithms.rapidart as ra
from nipype.utils.filemanip import list_to_filename
import nipype.interfaces.io as nio

from noise.motreg import motion_regressors
from noise.motionfilter import build_filter1
from noise.compcor import extract_noise_components
from preprocessing.utils import time_normalizer
from variables import working_dir, hp_cutoff_freq, lp_cutoff_freq, ds_dir


'''
Main workflow for denoising
Based on: based on https://github.com/NeuroanatomyAndConnectivity/pipelines/blob/master/src/lsd_lemon/func_preproc/denoise.py

Largely based on https://github.com/nipy/nipype/blob/master/examples/
rsfmri_vol_surface_preprocessing_nipy.py#L261
but denoising in anatomical space
'''



def create_denoise_pipeline():
    # workflow
    denoise_wf = Workflow(name='denoise')
    denoise_wf.base_dir = os.path.join(working_dir, 'rsfMRI_preproc_wf')

    # I/O NODES
    inputnode = Node(interface=util.IdentityInterface(fields=['epi_moco',
                                                              'par_moco',
                                                              't1w_brain_mask_epiSpace',
                                                              'csfwm_mask_epiSpace',
                                                              'mean_epi_moco',
                                                              't1w_2_epi_mat_flirt',
                                                              'TR_ms']),
                     name='inputnode')

    outputnode = Node(interface=util.IdentityInterface(fields=['combined_motion',
                                                               'outlier_files',
                                                               'intensity_files',
                                                               'outlier_stats',
                                                               'outlier_plots',
                                                               'bp_filtered_epi',
                                                               'mc_regressor',
                                                               'comp_regressor',
                                                               'rs_preprocessed',
                                                               'mc_res',
                                                               'comp_res']),
                      name='outputnode')

    ds = Node(nio.DataSink(base_directory=ds_dir), name='ds')
    ds.inputs.substitutions = [('_subject_id_', '')]

    # TR CONVERSION
    def get_TR_in_sec_fct(TR_ms):
        return TR_ms / 1000.0

    get_TR_in_sec = Node(util.Function(input_names=['TR_ms'],
                                       output_names=['TR_sec'],
                                       function=get_TR_in_sec_fct),
                         name='get_TR_in_sec')

    denoise_wf.connect(inputnode, 'TR_ms', get_TR_in_sec, 'TR_ms')


    # RUN ARTIFACT DETECTION
    # todo very different values compared to satra
    artifact = Node(ra.ArtifactDetect(save_plot=True,
                                      use_norm=True,
                                      parameter_source='FSL',
                                      mask_type='file',
                                      norm_threshold=1,
                                      zintensity_threshold=3,
                                      use_differences=[True, False]
                                      ),
                    name='artifact')
    artifact.plugin_args = {'submit_specs': 'request_memory = 17000'}

    denoise_wf.connect([(inputnode, artifact, [('epi_moco', 'realigned_files'),
                                               ('par_moco', 'realignment_parameters'),
                                               ('t1w_brain_mask_epiSpace', 'mask_file')])])

    # todo do we need this one level up?
    # (artifact, outputnode, [('norm_files', 'combined_motion'),
    # ('outlier_files', 'outlier_files'),
    # ('intensity_files', 'intensity_files'),
    #                         ('statistic_files', 'outlier_stats'),
    #                         ('plot_files', 'outlier_plots')])

    denoise_wf.connect([(artifact, ds, [('norm_files', 'denoise.artefact.@combined_motion'),
                                        ('outlier_files', 'denoise.artefact.@outlier'),
                                        ('intensity_files', 'denoise.artefact.@intensity'),
                                        ('statistic_files', 'denoise.artefact.@outlierstats'),
                                        ('plot_files', 'denoise.artefact.@outlierplots')])])


    # COLLECT MOTION REGRESSORS
    collect_mot_regressors = Node(util.Function(input_names=['motion_params', 'order', 'derivatives'],
                                                output_names=['out_files'],
                                                function=motion_regressors),
                                  name='collect_mot_regressors')
    collect_mot_regressors.plugin_args = {'submit_specs': 'request_memory = 17000'}

    denoise_wf.connect(inputnode, 'par_moco', collect_mot_regressors, 'motion_params')



    # CREATE A FILTER TO REMOVE MOTION AND ART CONFOUNDS (filter1)
    create_motion_filter = Node(util.Function(input_names=['motion_params', 'comp_norm',
                                                           'outliers', 'detrend_poly'],
                                              output_names=['out_files'],
                                              function=build_filter1),
                                name='create_motion_filter')  #'makemotionbasedfilter')
    create_motion_filter.inputs.detrend_poly = 2
    create_motion_filter.plugin_args = {'submit_specs': 'request_memory = 17000'}

    denoise_wf.connect(collect_mot_regressors, 'out_files', create_motion_filter, 'motion_params')
    denoise_wf.connect(artifact, 'outlier_files', create_motion_filter, 'outliers')
    denoise_wf.connect(create_motion_filter, 'out_files', ds, 'denoise.regress.@mc_regressor')



    # todo julia commented out (artifact, create_motion_filter, [#('norm_files', 'comp_norm'),. why? its in satras script



    # REGRESS OUT MOTION AND ART CONFOUND
    regress_out_motion = Node(fsl.GLM(out_f_name='F_mc.nii.gz',
                                      out_pf_name='pF_mc.nii.gz',
                                      out_res_name='res_mc.nii.gz',
                                      demean=True),
                              name='regress_out_motion')

    regress_out_motion.plugin_args = {'submit_specs': 'request_memory = 17000'}

    denoise_wf.connect(inputnode, 'epi_moco', regress_out_motion, 'in_file')
    denoise_wf.connect(create_motion_filter, ('out_files', list_to_filename), regress_out_motion, 'design')
    denoise_wf.connect([(regress_out_motion, outputnode, [('out_f', 'mc_F'),
                                                          ('out_pf', 'mc_pF'),
                                                          ('out_res', 'mc_res')])])
    denoise_wf.connect([(regress_out_motion, ds, [('out_f', 'denoise.regress.@mc_F'),
                                                          ('out_pf', 'denoise.regress.@mc_pF'),
                                                          ('out_res', 'denoise.regress.@mc_res')])])



    # CREATE FILTER WITH COMPCOR COMPONENTS (filter2)
    create_comp_filter = Node(util.Function(input_names=['realigned_file',
                                                         'mask_file',
                                                         'num_components',
                                                         'extra_regressors'],
                                            output_names=['out_files'],
                                            function=extract_noise_components),
                              name='create_comp_filter')

    # fixme why 6 components
    #fixme back to 6
    create_comp_filter.inputs.num_components = 5 # 6
    create_comp_filter.plugin_args = {'submit_specs': 'request_memory = 17000'}

    denoise_wf.connect(create_motion_filter, ('out_files', list_to_filename), create_comp_filter, 'extra_regressors')
    denoise_wf.connect(regress_out_motion, 'out_res', create_comp_filter, 'realigned_file')
    denoise_wf.connect(inputnode, 'csfwm_mask_epiSpace', create_comp_filter, 'mask_file')
    denoise_wf.connect(create_comp_filter, 'out_files', ds, 'denoise.regress.@comp_regressor')



    # REGRESS COMPCOR AND OTHER NOISE COMPONENTS
    regress_out_comp = Node(fsl.GLM(out_f_name='F_comp.nii.gz',
                                    out_pf_name='pF_comp.nii.gz',
                                    out_res_name='res_comp.nii.gz',
                                    demean=True),
                            name='regress_out_comp')

    regress_out_comp.plugin_args = {'submit_specs': 'request_memory = 17000'}

    denoise_wf.connect(regress_out_motion, 'out_res', regress_out_comp, 'in_file')
    denoise_wf.connect(create_comp_filter, 'out_files', regress_out_comp, 'design')
    denoise_wf.connect(inputnode, 't1w_brain_mask_epiSpace', regress_out_comp, 'mask')
    denoise_wf.connect([(regress_out_comp, ds, [('out_f', 'denoise.regress.@comp_F'),
                                                        ('out_pf', 'denoise.regress.@comp_pF'),
                                                        ('out_res', 'denoise.regress.@comp_res')]
                         )])
    denoise_wf.connect([(regress_out_comp, outputnode, [('out_f', 'comp_F'),
                                                        ('out_pf', 'comp_pF'),
                                                        ('out_res', 'comp_res')]
                         )])



    # BANDPASS FILTER
    # sigma calculation see
    # https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=ind1205&L=FSL&P=R57592&1=FSL&9=A&I=-3&J=on&d=No+Match%3BMatch%3BMatches&z=4
    def calc_bp_sigma_fct(TR_sec, cutoff_freq):
        sigma = 1. / (2 * TR_sec * cutoff_freq)
        return sigma


    calc_lp_sigma = Node(util.Function(input_names=['TR_sec', 'cutoff_freq'],
                                       output_names=['sigma'],
                                       function=calc_bp_sigma_fct), name='calc_lp_sigma')
    calc_lp_sigma.inputs.cutoff_freq = lp_cutoff_freq

    denoise_wf.connect(get_TR_in_sec, 'TR_sec', calc_lp_sigma, 'TR_sec')


    calc_hp_sigma = Node(util.Function(input_names=['TR_sec', 'cutoff_freq'],
                                       output_names=['sigma'],
                                       function=calc_bp_sigma_fct), name='calc_hp_sigma')
    calc_hp_sigma.inputs.cutoff_freq = hp_cutoff_freq

    denoise_wf.connect(get_TR_in_sec, 'TR_sec', calc_hp_sigma, 'TR_sec')


    bp_filter = Node(fsl.TemporalFilter(), name='bp_filter')
    bp_filter.plugin_args = {'submit_specs': 'request_memory = 17000'}

    denoise_wf.connect(regress_out_comp, 'out_res', bp_filter, 'in_file')
    denoise_wf.connect(calc_lp_sigma, 'sigma', bp_filter, 'lowpass_sigma')
    denoise_wf.connect(calc_hp_sigma, 'sigma', bp_filter, 'highpass_sigma')
    # denoise_wf.connect(bp_filter, 'out_file', outputnode, 'bp_filtered_epi')



    # TIME-NORMALIZE SCAN
    normalize_time = Node(util.Function(input_names=['in_file', 'tr'],
                                        output_names=['out_file'],
                                        function=time_normalizer),
                          name='normalize_time')

    normalize_time.plugin_args = {'submit_specs': 'request_memory = 17000'}
    denoise_wf.connect(bp_filter, 'out_file', normalize_time, 'in_file')
    denoise_wf.connect(get_TR_in_sec, 'TR_sec', normalize_time, 'tr')

    denoise_wf.connect(normalize_time, 'out_file', outputnode, 'rs_preprocessed')
    denoise_wf.connect(normalize_time, 'out_file', ds, 'denoise.rs_preprocessed.@rs_preprocessed')

    denoise_wf.write_graph(dotfilename='denoise', graph2use='flat', format='pdf')

    return denoise_wf