import SimpleITK as sitk
import numpy as np
import pydicom
import dicom2nifti
import os
import shutil
import tempfile
from . import util

def resample_nifti_to(nifti_in, nifti_ref, fname_out, isBQML=False):
    """Resample a nifti image to the same space as another nifti image.

    Parameters
    ----------
    nifti_in : string
        Path to the nifti image to be resampled.
    nifti_ref : string
        Path to the nifti image to be used as reference.
    fname_out : string
        Path to the resampled nifti image.
    isBQML : bool, optional
        If the nifti image takes a Bq/mL unit, interpolation changes the voxel size,
        thus the value must be adjusted to ensure the same total activity in the image.
        Default is False.
    """
    img_in = sitk.ReadImage(nifti_in)
    img_ref = sitk.ReadImage(nifti_ref)
    if isBQML:
        voxel_size_in = np.prod(img_in.GetSpacing())
        voxel_size_ref = np.prod(img_ref.GetSpacing())
        suv_factor = voxel_size_ref/voxel_size_in
        img_in = img_in*suv_factor
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(img_ref)
    resampler.SetInterpolator(sitk.sitkLinear)
    img_out = resampler.Execute(img_in)
    sitk.WriteImage(img_out, fname_out)

def dicom2niftiSUV(dicomdir, niftiname):
    """Convert a folder of dicom files to nifti files and apply SUV conversion.

    Parameters
    ----------
    dicomdir : str
        Path to directory containing DICOM files.
    niftiname : str
        Output path for the converted NIfTI file.

    Raises
    ------
    ValueError
        If required DICOM tags are missing or invalid.
    FileNotFoundError
        If no files are found in the directories.
    """
    # Convert dicom to nifti with dicom2nifti using temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        dicom2nifti.convert_directory(dicomdir, tmpdir)
        tmp_files = os.listdir(tmpdir)
        if not tmp_files:
            raise ValueError(f"No files generated in temporary directory from {dicomdir}")
        shutil.copyfile(os.path.join(tmpdir, tmp_files[0]), niftiname)

    # Get the SUV factor
    dicom_files = os.listdir(dicomdir)
    if not dicom_files:
        raise FileNotFoundError(f"No DICOM files found in {dicomdir}")

    ds = pydicom.dcmread(os.path.join(dicomdir, dicom_files[0]))

    # Extract required DICOM tags with error handling
    try:
        radiopharm_seq = ds.RadiopharmaceuticalInformationSequence[0]
        radiopharm_datetime = radiopharm_seq.RadiopharmaceuticalStartDateTime
        injection_dose = float(radiopharm_seq.RadionuclideTotalDose)
        half_life = float(radiopharm_seq.RadionuclideHalfLife)
    except (AttributeError, IndexError, KeyError) as e:
        raise ValueError(f"Missing required DICOM radiopharmaceutical tag: {e}")

    try:
        weight = ds[0x0010, 0x1030].value
    except (AttributeError, KeyError) as e:
        raise ValueError(f"Missing required DICOM patient weight tag: {e}")

    if half_life <= 0:
        raise ValueError("Half life is not positive")

    try:
        decay_correction = ds[0x0054, 0x1102].value
    except (AttributeError, KeyError) as e:
        raise ValueError(f"Missing decay correction tag: {e}")

    if decay_correction == 'START':
        try:
            series_date = ds[0x0008, 0x0021].value
            series_time = ds[0x0008, 0x0031].value
            series_datetime = series_date + series_time
        except (AttributeError, KeyError) as e:
            raise ValueError(f"Missing required DICOM series date/time tags: {e}")
        dose = injection_dose * 2**(-util.datetimestr_diff(series_datetime, radiopharm_datetime)/half_life)
    elif decay_correction == 'ADMIN':
        dose = injection_dose
    else:
        raise ValueError(f"Cannot determine the decay correction reference time. Value: {decay_correction}")

    if dose <= 0:
        raise ValueError(f"Calculated dose is not positive: {dose}")

    suv_factor = weight * 1000 / dose

    # Apply SUV conversion to the nifti files
    img = sitk.ReadImage(niftiname)
    img = sitk.Cast(img, sitk.sitkFloat32)
    img = img*suv_factor
    sitk.WriteImage(img, niftiname)

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from imvis import dicom2niftiSUV

    # Example usage - update paths to your actual data location
    nifti_in = "./samples/001_PT.nii.gz"
    nifti_ref = "./samples/001_CT.nii.gz"
    fname_out = "./samples/001_PT_resampled.nii.gz"
    dicomdir = "./samples/OSEM i8s20 nopsf_407"
    dicom2niftiSUV(dicomdir, "./samples/converted_nifti1.nii.gz")
