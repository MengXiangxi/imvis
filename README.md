# imvis

Interactive visualization of 3D medical images in python

## Installation

The package can be installed from PyPI using pip:

```bash
pip install imvis
```

## Features

### 3D image visualization

`imagesc3s` is a function that allows to visualize 3D images in a 2D slice-by-slice fashion. It is based on the `matplotlib` library and allows to interactively scroll through the slices of a 3D image. It also allows to change the color map and the windowing of the image.

```python
import imvis as iv
import pydicom

ds = pydicom.dcmread('path/to/dicom/file')
img = ds.pixel_array
iv.imagesc3s(img)
```

![imagesc3s: scroll](https://github.com/MengXiangxi/imvis/raw/main/resources/imagesc3s_window.png)

In cases where scrolling is not possible (e.g. in a Jupyter notebook), the alternative version `imagesc3slider` can be used. It allows to scroll through the slices of a 3D image using a slider.

```python
iv.imagesc3slider(img)
```

When using Jupyter notebook, the matplotlib backend can be changed to `tk` or `qt` to enable scrolling. This can be done using the following magic command:

```python
%matplotlib tk
iv.imagesc3slider(img)
```

### MIP with rotation angles

`mipz` allows the user to obtain a maximum intensity projection (MIP) of a 3D image along the z-axis. The user can also specify the rotation angles of the MIP.

```python
import SimpleITK as sitk
import numpy as np

img = sitk.ReadImage("/path/to/nifti")
imarray = sitk.GetArrayFromImage(img)
mip_array = np.zeros((36, imarray.shape[0], imarray.shape[1]))
for i in range(0, 360, 10):
    mip_array[int(i/10),:,:] = iv.mipz(imarray, i)
iv.imagesc3s(mip_array, [0, 10])
```

### NIFTI image resampling in reference to another image

`resample_nifti_to` allows to resample a NIFTI image in reference to another image. This is useful when you want to resample a NIFTI image to the same resolution as a DICOM image.

```python
def resample_nifti_to(nifti_in, nifti_ref, fname_out, img_type='intensity'):
    """Resample a nifti image to the same space as another nifti image.
    Parameters
    ----------
    nifti_in : string
        Path to the nifti image to be resampled.
    nifti_ref : string
        Path to the nifti image to be used as reference.
    fname_out : string
        Path to the resampled nifti image.
    img_type : string, optional
        Type of the image. Default is 'intensity'.
        'intensity': general type, no conversion.
        'BQML': PET or quantitative SPECT image, total counts are preserved.
        'mask': interger mask, interpolation will not change the value.
    """
```

### Convert PET DICOM to NIFTI with SUV

`dicom2niftiSUV` allows to convert a PET DICOM image to a NIFTI image with SUV values. The SUV values are computed using the corresponding DICOM tags.

```python
def dicom2niftiSUV(dicomdir, niftiname):
    """Convert a folder of dicom files to nifti files and apply SUV conversion.
    Parameters
    ----------
    dicomdir : string
        Path to the folder containing dicom files.
    niftiname : string
        Path and filename to the output nifti file.
    """
```

### Sort files in the DICOMDIR file into hierarchical folders

`dicomdir_split` allows to sort the files in a DICOMDIR file into hierarchical folders in the `Patient/Study/Series` fashion. This might be useful when extracting the desired DICOM series from a DICOMDIR file.

```python
def dicomdir_split(dicomdir_path, output_folder):
    ''' Split DICOM files in the DICOMDIR into different folders based according to patient, studies, and series.
    Parameters
    ----------
    dicomdir_path : string
        Path to the DICOMDIR file.
    output_folder : string
        Path to the output folder.
    '''
```

## Important notes

### Standard orientation

The matrix indices of the 3D images can be confusing. In this project, the author always assumes the following standard orientation, as shown in the figure below.

![Standard orientation](https://github.com/MengXiangxi/imvis/raw/main/resources/orientation.png)
