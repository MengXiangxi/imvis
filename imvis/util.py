import os
import datetime
import re

def sanitize_path_component(name):
    """Sanitize user input for safe use in file paths.

    Removes path separators and dangerous characters to prevent path traversal attacks.

    Parameters
    ----------
    name : str
        The path component to sanitize (e.g., PatientID, StudyDescription).

    Returns
    -------
    str
        Sanitized path component safe for use in file paths.
    """
    # Convert to string and remove path separators and dangerous characters
    safe = re.sub(r'[^\w\s-]', '_', str(name))
    # Remove leading/trailing whitespace and dots
    safe = safe.strip().strip('.')
    # Limit length to avoid filesystem issues
    safe = safe[:255] if safe else 'unnamed'
    return safe

def newfolder2(base, dirname):
    """Create a uniquely named folder, adding numeric suffix if needed.

    Parameters
    ----------
    base : str
        Base directory path.
    dirname : str
        Desired folder name.

    Returns
    -------
    str
        Path to the created folder.
    """
    suffix = 0
    fullpath = os.path.join(base, dirname)
    if not os.path.exists(fullpath):
        os.makedirs(fullpath)
        return fullpath
    while os.path.exists(fullpath + "_" + str(suffix)):
        suffix += 1
    new_path = fullpath + "_" + str(suffix)
    os.makedirs(new_path)
    return new_path

def newfilename(base, fname):
    """Generate a unique filename, adding numeric suffix if needed.

    Parameters
    ----------
    base : str
        Base directory path.
    fname : str
        Desired filename.

    Returns
    -------
    str
        Full path to the unique filename.
    """
    if not os.path.exists(os.path.join(base, fname)):
        return os.path.join(base, fname)

    name, ext = os.path.splitext(fname)
    suffix = 0
    while os.path.exists(os.path.join(base, name + "_" + str(suffix) + ext)):
        suffix += 1
    return os.path.join(base, name + "_" + str(suffix) + ext)
    
def datetimestr_diff(datetimestr1, datetimestr2):
    """Calculate the time difference between two date time strings.
    Parameters
    ----------
    datetimestr1 : string
        Date time string 1.
    datetimestr2 : string
        Date time string 2.
    Returns
    -------
    diff : float
        Time difference in seconds.
    """
    # if decimal point is present, remove the decimal point and the following digits
    if '.' in datetimestr1:
        datetimestr1 = datetimestr1.split('.')[0]
    if '.' in datetimestr2:
        datetimestr2 = datetimestr2.split('.')[0]
    dt1 = datetime.datetime.strptime(datetimestr1, "%Y%m%d%H%M%S")
    dt2 = datetime.datetime.strptime(datetimestr2, "%Y%m%d%H%M%S")
    diff = (dt1 - dt2).total_seconds()
    return diff