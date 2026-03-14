import numpy as np
from scipy.ndimage import rotate
from scipy.interpolate import interpn

def mipz(img, rot=0, space=None):
    """Maximum intensity projection along the z axis.

    Parameters
    ----------
    img : array_like
        3D array of image data
    rot : int, optional
        Rotation angle in degrees. Default is 0.
    space : list, optional
        [x, y] spacing of the image. Default is None (equivalent to [0, 0]).

    Returns
    -------
    array_like
        2D array of image data
    """
    if space is None:
        space = [0, 0]

    array = np.transpose(img, (1, 2, 0))
    if rot != 0:
        array = rotate(array, rot, axes=(1, 0), reshape=False)
    max_slice = np.max(array, axis=0)
    if space != [0, 0]:
        if space[0] == 0 or space[1] == 0:
            raise ValueError("Space values must be non-zero")
        newsize = [max_slice.shape[0], round(max_slice.shape[1]/space[0]*space[1])]
        # stretch the image along the y axis
        max_slice = interpn((np.arange(0, max_slice.shape[0]), np.arange(0, max_slice.shape[1])),
                           max_slice,
                           np.mgrid[0:max_slice.shape[0], 0:newsize[1]].T,
                           method='linear', bounds_error=False, fill_value=0.0)
        max_slice = np.rot90(max_slice)
        max_slice = np.flipud(max_slice)
    return np.rot90(max_slice)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    import SimpleITK as sitk
    from imvis import imagesc3s, mipz as mipz_func

    img = sitk.ReadImage("./samples/001_PT.nii.gz")
    imarray = sitk.GetArrayFromImage(img)
    imshape = mipz_func(imarray, space=[3.125, 2.886]).shape
    mip_array = np.zeros((36, imshape[0], imshape[1]))
    for i in range(0, 360, 10):
        mip_array[int(i/10), :, :] = mipz_func(imarray, i, [3.125, 2.886])
    imagesc3s.imagesc3s(mip_array, [0, 10])
    