__author__ = 'franzliem'


def standardize_divide_by_mean(wf_name='standardize_divide_by_mean'):
    # adapten from CPAC.utils.utils.get_zscore
    # function takes
    # 1. input image and mask image
    # 2. calculates mean within mask
    # 3. divides in_file by mean and masks in_file

    from nipype.pipeline.engine import Node, MapNode, Workflow
    import nipype.interfaces.utility as util
    import nipype.interfaces.fsl as fsl

    wf = Workflow(name=wf_name)
    inputnode = Node(util.IdentityInterface(fields=['in_file', 'mask_file']), name='inputnode')
    outputnode = Node(util.IdentityInterface(fields=['out_file']), name='outputnode')

    mean = MapNode(interface=fsl.ImageStats(), name='mean', iterfield=['in_file'])
    mean.inputs.op_string = '-k %s -m'
    wf.connect(inputnode, 'in_file', mean, 'in_file')
    wf.connect(inputnode, 'mask_file', mean, 'mask_file')

    def get_operand_string(mean):
        str1 = '-div %f' % (float(mean))
        op_string = str1 + " -mas %s"
        return op_string

    op_string = MapNode(util.Function(input_names=['mean'],
                                      output_names=['op_string'],
                                      function=get_operand_string),
                        name='op_string', iterfield=['mean'])

    wf.connect(mean, 'out_stat', op_string, 'mean')

    standardized = MapNode(interface=fsl.MultiImageMaths(),
                           name='standardized',
                           iterfield=['in_file', 'op_string'])

    wf.connect(op_string, 'op_string', standardized, 'op_string')
    wf.connect(inputnode, 'in_file', standardized, 'in_file')
    wf.connect(inputnode, 'mask_file', standardized, 'operand_files')
    wf.connect(standardized, 'out_file', outputnode, 'out_file')

    return wf


def calc_variability(in_file):
    '''
    input: preprocessed time series
    returns list of filenames with
    out_file_std, out_file_var, out_file_mssd, out_file_sqrt_mssd
    cf. https://github.com/stefanschmidt/vartbx/blob/master/Variability/shared_var.m
    '''

    import nibabel as nb
    import numpy as np
    import os

    def save_to_nii(out_file_name, out_data, template_img):
        out_img = nb.Nifti1Image(out_data, template_img.get_affine())
        out_img.to_filename(out_file_name)

    img = nb.load(in_file)
    ts = img.get_data()

    out_file_mean = os.path.join(os.getcwd(), 'ts_mean.nii.gz')
    ts_mean = np.mean(ts, 3)
    save_to_nii(out_file_mean, ts_mean, img)

    out_file_std = os.path.join(os.getcwd(), 'ts_std.nii.gz')
    ts_std = np.std(ts, 3)
    save_to_nii(out_file_std, ts_std, img)

    out_file_var = os.path.join(os.getcwd(), 'ts_var.nii.gz')
    ts_var = np.var(ts, 3)
    save_to_nii(out_file_var, ts_var, img)

    out_file_mssd = os.path.join(os.getcwd(), 'ts_mssd.nii.gz')
    ts_mssd = np.sum(np.diff(ts, 3) ** 2, 3) / (ts.shape[3] - 1)
    save_to_nii(out_file_mssd, ts_mssd, img)

    out_file_sqrt_mssd = os.path.join(os.getcwd(), 'ts_sqrt_mssd.nii.gz')
    ts_sqrt_mssd = np.sqrt(ts_mssd)
    save_to_nii(out_file_sqrt_mssd, ts_sqrt_mssd, img)

    out_file_list = [out_file_mean, out_file_std, out_file_var, out_file_mssd, out_file_sqrt_mssd]
    return out_file_list


def extract_data_from_mask_and_make_2d(in_file, mask_file):
    '''
    :param in_file: 4d nii
    :param mask_file: 3d nii
    :return: np.arrays
    data_2d 2d array of size in_file.shape[3] x n_ones_in mask
    mask 3d boolian array

    reshape to full 4d:
    data4d = np.zeros_like(data).astype(np.float64)
    data4d.fill(np.nan)
    data4d[mask] = flat_data_res.T
    '''
    import numpy as np
    import nibabel as nb
    import os

    nii = nb.load(in_file)
    data = nii.get_data().astype(np.float64)
    nii = nb.load(mask_file)
    mask = nii.get_data().astype(np.bool)

    # check if mask is 3d and dimensions of mask and data are matching
    if not (mask.ndim == 3):
        raise Exception('Error. Mask is not 3d. mask.ndim=%s' % mask.ndim)
    if not (mask.shape == data.shape[:3]):
        raise Exception('dimensions of mask and data not matching: %s vs %s' % (mask.shape, data.shape[:3]))

    data_2d = data[mask].T

    if not (data_2d.shape[0] == data.shape[3]):
        raise Exception(
            'something went wrong. data_2d.shape[0] != data.shape[3]: %s %s' % (data_2d.shape[0], data.shape[3]))

    # fixme
    flat_data_file = os.path.join(os.getcwd(), 'flat_data.csv')
    np.savetxt(flat_data_file, data_2d, delimiter='\t')

    return data_2d, mask


def fill_data_to_mask_and_saveas_4d_nii(data_2d, orig_4d_file, mask, filename='data_4d.nii.gz'):
    '''
    uses 2d array and mask to create 4d nifti
    :param data_2d:
    :param orig_4d_file: nii file to get data shape and header
    :param mask: boolean 3d array
    :param filename:
    :return:
    '''
    import numpy as np
    import nibabel as nb
    import os

    nii = nb.load(orig_4d_file)
    orig_data_4d = nii.get_data().astype(np.float64)
    if not (mask.shape == orig_data_4d.shape[:3]):
        raise Exception('dimensions of mask and data not matching: %s vs %s' % (mask.shape, orig_data_4d.shape[:3]))

    data_4d = np.zeros_like(orig_data_4d).astype(np.float64)
    data_4d.fill(np.nan)
    data_4d[mask] = data_2d.T

    out_img = nb.Nifti1Image(data_4d, header=nii.get_header(), affine=nii.get_affine())
    out_file = os.path.join(os.getcwd(), filename)
    out_img.to_filename(out_file)
    return out_file


def residualize_imgs(in_file, mask_file, confounds_file):
    '''
    * takes 4d file, mask file & confounds as np.array
    * regresses out confounds (only within mask)
    * writes residualized nii
    '''
    from nilearn.input_data import NiftiMasker
    import os
    import numpy as np

    confounds = np.loadtxt(confounds_file)
    masker = NiftiMasker(mask_img=mask_file)
    brain_data_2d = masker.fit_transform(in_file, confounds=confounds)
    out_file = os.path.join(os.getcwd(), 'residualized_data.nii.gz')
    out_img = masker.inverse_transform(brain_data_2d)
    out_img.to_filename(out_file)
    return out_file

