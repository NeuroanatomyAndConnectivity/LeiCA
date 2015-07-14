


def plot_rs_surf(in_file, thr_list=[(.2,1)],roi_coords=(), fwhm=0):
    # in_file .nii to be projected on surface
    # list of tuples defining min and max thr_list=[(.2,1)]
    import os
    import subprocess
    from surfer import Brain, io

    arch = subprocess.check_output('arch')
    if arch.startswith('x86_'): # set offscrene rendering to avoid intereference on linux
        from mayavi import mlab
        mlab.options.offscreen = True

    out_file_list = []
    in_file_name = os.path.basename(in_file)

    reg_file = os.path.join(os.environ["FREESURFER_HOME"],"average/mni152.register.dat")
    for thr in thr_list:
        min_thr = thr[0]
        max_thr = thr[1]
        print(min_thr)
        print(max_thr)

        for hemi in ['lh', 'rh']:
            brain = Brain("fsaverage", hemi, "inflated", views=['lat', 'med'], config_opts=dict(background="white"))

            surf_data = io.project_volume_data(in_file, hemi, reg_file, smooth_fwhm=fwhm)

            brain.add_overlay(surf_data, min=min_thr, max=max_thr, name="ang_corr", hemi=hemi)

            roi_str = ''
            if not(roi_coords == ()):
                if roi_coords[0] <0: #lh
                    hemi_str = 'lh'
                else:
                    hemi_str = 'rh'
                roi_str = '_roi_%s.%s.%s' % roi_coords

                if hemi_str == hemi:
                    brain.add_foci(roi_coords, map_surface="white", hemi=hemi_str, color='red', scale_factor=2)


            out_filename = os.path.join(os.getcwd(), in_file_name + roi_str + '_thr_%s' % min_thr + '_' + hemi + '.png')
            out_file_list += [out_filename]
            brain.save_image(out_filename)
            brain.close()
    return out_file_list



def plot_rs_surf_bh(in_file, thr_list=[(.2,1)],roi_coords=(), fwhm=0):
    # in_file .nii to be projected on surface
    # list of tuples defining min and max thr_list=[(.2,1)]
    import os
    from surfer import Brain, io

    out_file_list = []
    in_file_name = os.path.basename(in_file)

    reg_file = os.path.join(os.environ["FREESURFER_HOME"],"average/mni152.register.dat")
    for thr in thr_list:
        min_thr = thr[0]
        max_thr = thr[1]
        print(min_thr)
        print(max_thr)

        brain = Brain("fsaverage", "split", "inflated", views=['lat', 'med'], config_opts=dict(background="white"))

        surf_data_lh = io.project_volume_data(in_file, "lh", reg_file, smooth_fwhm=fwhm)
        surf_data_rh = io.project_volume_data(in_file, "rh", reg_file, smooth_fwhm=fwhm)

        brain.add_overlay(surf_data_lh, min=min_thr, max=max_thr, name="ang_corr_lh", hemi='lh')
        brain.add_overlay(surf_data_rh, min=min_thr, max=max_thr, name="ang_corr_rh", hemi='rh')

        roi_str = ''
        if not(roi_coords == ()):
            if roi_coords[0] <0: #lh
                hemi_str = 'lh'
            else:
                hemi_str = 'rh'
            roi_str = '_roi_%s.%s.%s' % roi_coords

            brain.add_foci(roi_coords, map_surface="white", hemi=hemi_str, color='red', scale_factor=2)


        out_filename = os.path.join(os.getcwd(), in_file_name + roi_str + '_thr_%s' % min_thr + '.png')
        out_file_list += [out_filename]
        brain.save_image(out_filename)
        brain.close()
    return out_file_list




def plot_data_surf_bh(in_file, colormap='jet', thr_list=[(None, None, None)],roi_coords=(), fwhm=0):
    '''
    allows more flexible visualization than plot_rs_surf_bh
    thr_list = [(min, max, thresh)]
    colormap: matplotlib colormap (http://matplotlib.org/examples/color/colormaps_reference.html)
    '''

    # in_file .nii to be projected on surface


    import os
    from surfer import Brain, io

    out_file_list = []
    in_file_name = os.path.basename(in_file)

    reg_file = os.path.join(os.environ["FREESURFER_HOME"],"average/mni152.register.dat")
    for thr in thr_list:
        min_thr = thr[0]
        max_thr = thr[1]
        thr_thr = thr[2]


        brain = Brain("fsaverage", "split", "inflated", views=['lat', 'med'], config_opts=dict(background="white"))

        surf_data_lh = io.project_volume_data(in_file, "lh", reg_file, smooth_fwhm=fwhm)
        surf_data_rh = io.project_volume_data(in_file, "rh", reg_file, smooth_fwhm=fwhm)

        brain.add_data(surf_data_lh, min=min_thr, max=max_thr, thresh=thr_thr, colormap=colormap, hemi='lh')
        brain.add_data(surf_data_rh, min=min_thr, max=max_thr, thresh=thr_thr, colormap=colormap, hemi='rh')

        roi_str = ''
        if not(roi_coords == ()):
            if roi_coords[0] <0: #lh
                hemi_str = 'lh'
            else:
                hemi_str = 'rh'
            roi_str = '_roi_%s.%s.%s' % roi_coords

            brain.add_foci(roi_coords, map_surface="white", hemi=hemi_str, color='red', scale_factor=2)


        out_filename = os.path.join(os.getcwd(), in_file_name + roi_str + '_thr_%s' % min_thr + '.png')
        out_file_list += [out_filename]
        brain.save_image(out_filename)
        brain.close()
    return out_file_list


