
import os
import sys


os.environ['FREESURFER_HOME'] = '/Applications/freesurfer/'
os.environ['SUBJECTS_DIR'] = '/Applications/freesurfer/subjects'
from surfer import Brain, io

# SCA PARAMETERS
rois = []
# #lMPFC
rois.append((-6,52,-2))
# #rMPFC
rois.append((6,52,-2))
#


brain = Brain("fsaverage", "split", "inflated", views=['lat', 'med'], config_opts=dict(background="white"))
brain.add_foci(rois[0], map_surface="white", hemi='lh', color='red', scale_factor=1)
brain.add_foci(rois[1], map_surface="white", hemi='rh', color='red', scale_factor=2)

#
#
# fwhm_list = [1,6]
# thr_list = [.2]
# fig_dir = '/Users/franzliem/Desktop/test_data/figs/raw'
#
# os.environ['FREESURFER_HOME'] = '/Applications/freesurfer/'
# os.environ['SUBJECTS_DIR'] = '/Applications/freesurfer/subjects'
#
# from surfer import Brain, io
#
# """Bring up the visualization"""
# brain = Brain("fsaverage", "split", "inflated", views=['lat', 'med'], config_opts=dict(background="white"))
#
# """Project the volume file and return as an array"""
# reg_file = os.path.join(os.environ["FREESURFER_HOME"],"average/mni152.register.dat")
#
# for TR in TR_list:
#     for roi in rois:
#         for fwhm in fwhm_list:
#             for thr in thr_list:
#                 brain = Brain("fsaverage", "split", "inflated", views=['lat', 'med'], config_opts=dict(background="white"))
#
#                 mri_file = os.path.join(working_dir, 'LeiCA_resting/sca_raw/','_TR_id_%s'%TR, '_subject_id_0103384',
#                  '_roi_%s.%s.%s'%(roi[0],roi[1],roi[2]), '_fwhm_%s'%fwhm, 'correlation_map/corr_map.nii.gz')
#                 print ' '
#                 print mri_file
#
#                 surf_data_lh = io.project_volume_data(mri_file, "lh", reg_file)
#                 surf_data_rh = io.project_volume_data(mri_file, "rh", reg_file)
#
#                 """
#                 You can pass this array to the add_overlay method for a typical activation
#                 overlay (with thresholding, etc.).
#                 """
#                 brain.add_overlay(surf_data_lh, min=thr, max=.7, name="ang_corr_lh", hemi='lh')
#                 brain.add_overlay(surf_data_rh, min=thr, max=.7, name="ang_corr_rh", hemi='rh')
#
#                 if roi[0] <0: #lh
#                     hemi_str = 'lh'
#                 else:
#                     hemi_str = 'rh'
#                 print 'XXXXX XXXXX XXXX '
#                 print(roi)
#                 print hemi_str
#                 brain.add_foci(roi, map_surface="white", hemi=hemi_str, color='red', scale_factor=2)
#
#
#                 out_filename = os.path.join(fig_dir, 'test_TR_%s_%s.%s.%s_fwhm%s_thr%s.png'%(TR, roi[0],roi[1],roi[2], fwhm, thr))
#                 brain.save_image(out_filename)
#                 brain.close()
#
#
# # """
# # You can also pass it to add_data for more control
# # over the visualization. Here we'll plot the whole
# # range of correlations
# # """
# # for overlay in brain.overlays_dict["ang_corr_lh"]:
# #     overlay.remove()
# # for overlay in brain.overlays_dict["ang_corr_rh"]:
# #     overlay.remove()
# #
# # """
# # We want to use an appropriate color map for these data: a divergent map that
# # is centered on 0, which is a meaningful transition-point as it marks the change
# # from negative correlations to positive correlations.
# #
# # We'll also plot the map with some transparency so that we can see through to
# # the underlying anatomy.
# # """
# # brain.add_data(surf_data_lh, -.7, .7, thresh=0.2, colormap="coolwarm", alpha=.75,
# #                hemi='lh')
# # brain.add_data(surf_data_rh, -.7, .7, thresh=0.2, colormap="coolwarm", alpha=.75,
# #                hemi='rh')
#
# # """
# # This overlay represents resting-state correlations with a
# # seed in left angular gyrus. Let's plot that seed.
# # """
# # seed_coords = (-45, -67, 36)
# # brain.add_foci(seed_coords, map_surface="white", hemi='lh', color='red', scale_factor=2)
# #
# #
# # out_filename = '/Users/franzliem/Desktop/br.png'
# # brain.save_image(out_filename)
#
# #
# # # 1. create single imgs
# # for h in hemis:
# #     for iLine in range (1, nMeas):
# #         for iCol in range(iLine):
# #             print h, iLine , iCol, meas[iLine], meas[iCol]
# #             #create overlay img
# #             fileName = os.path.join(outPath, (h + '.corr.' + meas[iLine] + '.X.' + meas[iCol] + '.R.mgh' ))
# #             overlayData = np.nan_to_num( nb.freesurfer.mghformat.load(fileName).get_data().squeeze())#.T
# #             brain = Brain(subject_id, h, surface, config_opts=dict(background="white"))
# #             brain.add_annotation("aparc")
# # #            brain.add_data(overlayData, -1, 1, colormap="RdBu", alpha=.9, hemi=h, thresh=.000000001)
# #             brain.add_data(overlayData, -1, 1, colormap="RdBu", alpha=.9, hemi=h)
# #             for cbar in brain.data_dict[h]['colorbars']:
# #                 cbar.reverse_lut = True
# #             brain.add_annotation("aparc.a2009s")
# #             #gray out medial wall
# #             fileName = os.path.join(subjects_dir, subject_id,'label', (h + '.Medial_wall.label'))
# #             brain.add_label(fileName, color = 'gray')
# #             #save single img
# #             outFileName = os.path.join(figPath, ('1.single.' + h + '.' +  meas[iLine] + '.X.' + meas[iCol] + '.png'))
# #             im = brain.save_montage(outFileName, order=theViews,orientation='v', border_size=15, colorbar=[])
# #
# # outFileName = os.path.join(figPath, ('99.colorbar.png'))
# # im = brain.save_montage(outFileName, order=theViews,orientation='v', border_size=15, colorbar='auto')
