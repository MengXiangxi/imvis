import numpy as np
from scipy.ndimage import rotate

def mipz(img, rot=0):
    """Maximum intensity projection along the z axis.
    Parameters
    ----------
    img : array_like
        3D array of image data
    rot : int, optional
        Rotation angle in degrees. Default is 0.
    Returns
    -------
    img : array_like
        2D array of image data
    """
    array = np.transpose(img, (1,2,0))
    if rot != 0:
        array = rotate(array, rot, axes=(1,0), reshape=False)
    slice = np.max(array, axis=0)
    return np.rot90(slice)


if __name__ == "__main__":
    import SimpleITK as sitk
    import imagesc3s
    img = sitk.ReadImage("./test/001_PT.nii.gz")
    imarray = sitk.GetArrayFromImage(img)
    mip_array = np.zeros((36, imarray.shape[0], imarray.shape[1]))
    for i in range(0, 360, 10):
        mip_array[int(i/10),:,:] = mipz(imarray, i)
    imagesc3s.imagesc3s(mip_array, [0, 10])
    