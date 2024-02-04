import pydicom
import pydicom.fileset
import os
import shutil
import imvis.util

def dicomdir_split(dicomdir_path, output_folder):
    ''' Split DICOM files in the DICOMDIR into different folders based according to patient, studies, and series.
    '''
    dicom_dir = os.path.dirname(dicomdir_path)
    ds = pydicom.dcmread(dicomdir_path)
    fs = pydicom.fileset.FileSet(ds)
    
    PatientDict = {}
    StudyDict = {}
    SeriesDict = {}
    for i in fs:
        if i.PatientID in PatientDict:
            patient_folder = PatientDict[i.PatientID]
        else:
            patient_folder = imvis.util.newfolder2(output_folder,i.PatientID)
            PatientDict[i.PatientID] = patient_folder
        if i.PatientID+i.StudyInstanceUID in StudyDict:
            study_folder = StudyDict[i.PatientID+i.StudyInstanceUID]
        else:
            try:
                study_info = str(i.StudyDescription)
            except:
                study_info = str(i.StudyDate)
            study_folder = imvis.util.newfolder2(patient_folder,study_info)
            StudyDict[i.PatientID+i.StudyInstanceUID] = study_folder
        if i.PatientID+i.StudyInstanceUID+i.SeriesInstanceUID in SeriesDict:
            series_folder = SeriesDict[i.PatientID+i.StudyInstanceUID+i.SeriesInstanceUID]
        else:
            try:
                series_info = str(i.SeriesNumber)+'_'+str(i.SeriesDescription)
            except:
                series_info = str(i.SeriesNumber)
            series_folder = imvis.util.newfolder2(study_folder,series_info)
            SeriesDict[i.PatientID+i.StudyInstanceUID+i.SeriesInstanceUID] = series_folder
        dicom_src = os.path.join(dicom_dir, os.path.join(*(i.ReferencedFileID)))
        dicom_destin = imvis.util.newfilename(series_folder,os.path.basename(os.path.join(*(i.ReferencedFileID))))
        shutil.copyfile(dicom_src, dicom_destin)

if __name__ == "__main__":
    dicomdir_split('/path/to/DICOMDIR', './test/output/')