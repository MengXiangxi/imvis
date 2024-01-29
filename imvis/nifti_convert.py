import SimpleITK as sitk
import pydicom
import dicom2nifti
import os
import shutil 
import imvis.util

def resample_nifti_to(nifti_in, nifti_ref, fname_out):
    """Resample a nifti image to the same space as another nifti image.
    Parameters
    ----------
    nifti_in : string
        Path to the nifti image to be resampled.
    nifti_ref : string
        Path to the nifti image to be used as reference.
    fname_out : string
        Path to the resampled nifti image.
    """
    img_in = sitk.ReadImage(nifti_in)
    img_ref = sitk.ReadImage(nifti_ref)
    img_in.SetOrigin(img_ref.GetOrigin())
    img_in.SetDirection(img_ref.GetDirection())
    img_in.SetSpacing(img_ref.GetSpacing())
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(img_ref)
    resampler.SetInterpolator(sitk.sitkLinear)
    img_out = resampler.Execute(img_in)
    sitk.WriteImage(img_out, fname_out)

def dicom2niftiSUV(dicomdir, niftiname):
    """Convert a folder of dicom files to nifti files and apply SUV conversion.
    """
    # Convert dicom to nifti with
    if imvis.util.newfolder("./tmp/") == -1:
        print("Error: Cannot create folder ./tmp/")
        return -1
    dicom2nifti.convert_directory(dicomdir, "./tmp/")
    shutil.copyfile(os.path.join("./tmp/", os.listdir("./tmp")[0]), niftiname)
    shutil.rmtree("./tmp/")

    # Get the SUV factor
    ds = pydicom.dcmread(os.path.join(dicomdir, os.listdir(dicomdir)[0]))
    radiopharm_datetime = ds.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartDateTime
    injection_dose = float(ds.RadiopharmaceuticalInformationSequence[0].RadionuclideTotalDose)
    half_life = float(ds.RadiopharmaceuticalInformationSequence[0].RadionuclideHalfLife)
    weight = ds[0x0010, 0x1030].value
    if half_life <= 0:
        print("Error: Half life is not positive.")
        return -1
    if ds[0x0054, 0x1102].value == 'START':
        acquisition_datetime = ds[0x0008, 0x002A].value
        dose = injection_dose * 2**(-imvis.util.datetimestr_diff(acquisition_datetime,radiopharm_datetime)/half_life)
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
    nifti_in = "./test/001_PT.nii.gz"
    nifti_ref = "./test/001_CT.nii.gz"
    fname_out = "./test/001_PT_resampled.nii.gz"
    dicomdir = "./test/OSEM i8s20 nopsf_407"
    # resample_nifti_to(nifti_in, nifti_ref, fname_out)
    dicom2niftiSUV(dicomdir, "./test/converted_nifti.nii.gz")