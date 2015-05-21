import os

#print os.system('tcsh')

os.environ['FSLDIR'] = '/Applications/FSL'

setenv_dict=

setenv PATH /Applications/AFNI/abin:$PATH
setenv DYLD_FALLBACK_LIBRARY_PATH /Applications/AFNI/abin
setenv PYTHONPATH /usr/local/lib/python2.7/site-packages

setenv PATH /Applications/circos-0.67-4/bin:$PATH
setenv PATH /opt/local/bin:$PATH
setenv PKG_CONFIG_PATH /usr/local/lib/pkgconfig

setenv FSLDIR /Applications/FSL
source ${FSLDIR}/etc/fslconf/fsl.csh
setenv PATH ${FSLDIR}/bin:${PATH}
setenv PATH  /Applications/workbench/bin_macosx64:$PATH

source /Applications/freesurfer/FSstartup.tcsh