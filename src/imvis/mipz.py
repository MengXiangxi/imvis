import numpy as np
from scipy.ndimage import rotate
from scipy.interpolate import interpn

def mipz(img, rot=0, space=[0, 0]):
    """Maximum intensity projection along the z axis.
    Parameters
    ----------
    img : array_like
        3D array of image data
    rot : int, optional
        Rotation angle in degrees. Default is 0.
    space : list, optional
        [x, y] spacing of the image. Default is [0, 0].
    Returns
    -------
    img : array_like
        2D array of image data
    """
    array = np.transpose(img, (1,2,0))
    if rot != 0:
        array = rotate(array, rot, axes=(1,0), reshape=False)
    slice = np.max(array, axis=0)
    if space!=[0, 0]:
        newsize = [slice.shape[0], round(slice.shape[1]/space[0]*space[1])]
        # stretch the image along the y axis
        slice = interpn((np.arange(0,slice.shape[0]), np.arange(0,slice.shape[1])), slice, np.mgrid[0:slice.shape[0], 0:newsize[1]].T, method='linear', bounds_error=False, fill_value=0.0)
        slice = np.rot90(slice)
        slice = np.flipud(slice)
    return np.rot90(slice)


if __name__ == "__main__":
    import SimpleITK as sitk
    import imagesc3s
    img = sitk.ReadImage("./samples/001_PT.nii.gz")
    imarray = sitk.GetArrayFromImage(img)
    imshape = mipz(imarray, space=[3.125,2.886]).shape
    mip_array = np.zeros((36, imshape[0], imshape[1]))
    for i in range(0, 360, 10):
        mip_array[int(i/10),:,:] = mipz(imarray, i, [3.125,2.886])
    imagesc3s.imagesc3s(mip_array, [0, 10])
    