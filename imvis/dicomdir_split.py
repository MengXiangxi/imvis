import pydicom
import pydicom.fileset
import os
import shutil
from . import util

def dicomdir_split(dicomdir_path, output_folder):
    """Split DICOM files in the DICOMDIR into different folders based on patient, studies, and series.

    Parameters
    ----------
    dicomdir_path : str
        Path to the DICOMDIR file.
    output_folder : str
        Path to the output folder where split files will be stored.
    """
    dicom_dir = os.path.dirname(dicomdir_path)
    ds = pydicom.dcmread(dicomdir_path)
    fs = pydicom.fileset.FileSet(ds)

    patient_dict = {}
    study_dict = {}
    series_dict = {}
    for i in fs:
        # Sanitize PatientID to prevent path traversal
        safe_patient_id = util.sanitize_path_component(i.PatientID)

        if i.PatientID in patient_dict:
            patient_folder = patient_dict[i.PatientID]
        else:
            patient_folder = util.newfolder2(output_folder, safe_patient_id)
            patient_dict[i.PatientID] = patient_folder

        if i.PatientID+i.StudyInstanceUID in study_dict:
            study_folder = study_dict[i.PatientID+i.StudyInstanceUID]
        else:
            try:
                study_info = str(i.StudyDescription)
            except AttributeError:
                study_info = str(i.StudyDate)
            # Sanitize study info
            safe_study_info = util.sanitize_path_component(study_info)
            study_folder = util.newfolder2(patient_folder, safe_study_info)
            study_dict[i.PatientID+i.StudyInstanceUID] = study_folder

        if i.PatientID+i.StudyInstanceUID+i.SeriesInstanceUID in series_dict:
            series_folder = series_dict[i.PatientID+i.StudyInstanceUID+i.SeriesInstanceUID]
        else:
            try:
                series_info = str(i.SeriesNumber)+'_'+str(i.SeriesDescription)
            except AttributeError:
                series_info = str(i.SeriesNumber)
            # Sanitize series info
            safe_series_info = util.sanitize_path_component(series_info)
            series_folder = util.newfolder2(study_folder, safe_series_info)
            series_dict[i.PatientID+i.StudyInstanceUID+i.SeriesInstanceUID] = series_folder

        # Sanitize ReferencedFileID components to prevent path traversal
        safe_ref_id = [util.sanitize_path_component(part) for part in i.ReferencedFileID]
        ref_path = os.path.join(*safe_ref_id)
        dicom_src = os.path.join(dicom_dir, ref_path)
        ref_basename = os.path.basename(ref_path)
        dicom_destin = util.newfilename(series_folder, ref_basename)
        shutil.copyfile(dicom_src, dicom_destin)

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from imvis import dicomdir_split

    # Example usage - update paths to your actual DICOMDIR location
    dicomdir_split('/path/to/DICOMDIR', './test/output/')