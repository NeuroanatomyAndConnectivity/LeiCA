__author__ = 'franzliem'

from variables import rois_list
from plot_resting_correlations import plot_rs_surf_bh
for roi in rois_list:
    in_file = '/Users/franzliem/Desktop/data_0103384/0103384sca/_roi_%s.%s.%s/_fwhm_1/correlation_map/corr_map.nii.gz' % roi
    plot_rs_surf_bh(in_file, [(.5,1)], roi)
    print in_file
