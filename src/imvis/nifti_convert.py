import SimpleITK as sitk
import numpy as np
import pydicom
import dicom2nifti
import os
import shutil 
from imvis import utils

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
    if not img_type in ['intensity', 'BQML', 'mask']:
        print("Error: img_type must be 'intensity' (Default), 'BQML', or 'mask'.")
        return -1
    img_in = sitk.ReadImage(nifti_in)
    img_ref = sitk.ReadImage(nifti_ref)
    if img_type=='BQML':
        voxel_size_in = np.prod(img_in.GetSpacing())
        voxel_size_ref = np.prod(img_ref.GetSpacing())
        SUVfactor = voxel_size_ref/voxel_size_in
        img_in = img_in*SUVfactor
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(img_ref)
    resampler.SetInterpolator(sitk.sitkLinear)
    if img_type=='mask':
        resampler.SetInterpolator(sitk.sitkNearestNeighbor)
    img_out = resampler.Execute(img_in)
    img_in.SetOrigin(img_ref.GetOrigin())
    img_in.SetDirection(img_ref.GetDirection())
    img_in.SetSpacing(img_ref.GetSpacing())
    sitk.WriteImage(img_out, fname_out)

def LBW(weight, height, gender):
    """Calculate lean body weight.
    Ref: Lodge, Martin A., and Richard L. Wahl. "Practical PERCIST: a simplified guide to PET response criteria in solid tumors 1.0." Radiology 280.2 (2016): 576.

    Parameters
    ----------
    weight : float
        Total body weight in kg.
    height : float
        Height in cm
    gender : string
        'F' or 'M'
    Returns
    -------
    lbw : float
        Lean body weight in kg.
    """
    if gender=='M':
        lbw = 1.10 * weight  - 128.0 * (weight**2/height**2)
    elif gender=='F':
        lbw = 1.07 * weight  - 148.0 * (weight**2/height**2)
    else:
        print("Wrong gender parameter, should be 'F or 'M'.")
        return -1
    return lbw
        
def dicom2niftiSUV(dicomdir, niftiname,bodyweight="TBW"):
    """Convert a folder of dicom files to nifti files and apply SUV conversion.
    Parameters
    ----------
    dicomdir : string
        Path to the folder containing dicom files.
    niftiname : string
        Path and filename to the output nifti file.
    bodyweight : string, optional
        Type of body weight. Default is "TBW".
        "TBW": total body weight.
        "LBW": lean body weight.
    """
    # Convert dicom to nifti with dicom2nifti
    if utils.newfolder("./tmp/") == -1:
        print("Error: Cannot create folder ./tmp/")
        # return -1
    dicom2nifti.convert_directory(dicomdir, "./tmp/")
    shutil.copyfile(os.path.join("./tmp/", os.listdir("./tmp")[0]), niftiname)
    shutil.rmtree("./tmp/")

    # Get the SUV factor
    ds = pydicom.dcmread(os.path.join(dicomdir, os.listdir(dicomdir)[0]))
    radiopharm_datetime = ds.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartDateTime
    injection_dose = float(ds.RadiopharmaceuticalInformationSequence[0].RadionuclideTotalDose)
    half_life = float(ds.RadiopharmaceuticalInformationSequence[0].RadionuclideHalfLife)
    weight = ds[0x0010, 0x1030].value
    
    # calculate weight
    if bodyweight == "LBW":
        gender = ds.PatientSex
        height = ds.PatientSize * 100
        LBW(weight, height, gender)
    else:
        weight = weight
    
    if half_life <= 0:
        print("Error: Half life is not positive.")
        return -1
    if ds[0x0054, 0x1102].value == 'START':
        try:
            acquisition_datetime = ds[0x0008, 0x002A].value
        except KeyError:
            acquisition_datetime = ds[0x0008, 0x0022].value +\
                  ds[0x0008, 0x0032].value
        dose = injection_dose * 2**(-utils.datetimestr_diff(acquisition_datetime,radiopharm_datetime)/half_life)
    elif ds[0x0054, 0x1102].value == 'ADMIN':
        dose = injection_dose
    else:
        print("Error: Cannot determine the decay correction reference time.")
        return -1
    
    SUVfactor = weight * 1000 / dose

    # Apply SUV conversion to the nifti files
    img = sitk.ReadImage(niftiname)
    img = sitk.Cast(img, sitk.sitkFloat32)
    img = img*SUVfactor
    sitk.WriteImage(img, niftiname)

if __name__ == "__main__":
    nifti_in = "./samples/001_PT.nii.gz"
    nifti_ref = "./samples/001_CT.nii.gz"
    fname_out = "./samples/001_PT_resampled.nii.gz"
    dicomdir = "./samples/OSEM i8s20 nopsf_407"
    # resample_nifti_to(nifti_in, nifti_ref, fname_out, img_type='BQML')
    dicom2niftiSUV(dicomdir, "./samples/converted_nifti_LBM.nii.gz", "LBW")