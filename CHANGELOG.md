# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2026-03-14

### Security Fixes
- **CRITICAL**: Fixed unsanitized ReferencedFileID in `dicomdir_split.py` that could allow path traversal attacks
- All user-controlled DICOM fields now properly sanitized before use in file paths

### Bug Fixes
- **CRITICAL**: Fixed division by zero vulnerability in `dicom2niftiSUV()` when dose calculation results in zero
- **CRITICAL**: Fixed division by zero vulnerability in `mipz()` when space[0] or space[1] is zero
- **HIGH**: Added missing error handling for DICOM series date/time tags in `dicom2niftiSUV()`
- Fixed incomplete error handling for DICOM tag access in decay correction calculation

### Code Quality Improvements
- Removed dead code: `newfolder()` function that was no longer used anywhere in codebase
- Standardized variable naming to follow PEP 8 snake_case convention:
  - `PatientDict` → `patient_dict`
  - `StudyDict` → `study_dict`
  - `SeriesDict` → `series_dict`
  - `SUVfactor` → `suv_factor`
- Standardized import patterns: replaced `try/except ImportError` with clean relative imports
- Removed commented-out code in `imagesc3s.py` and `nifti_convert.py`
- Improved code readability in `dicomdir_split.py` by breaking complex path construction into multiple lines

### API Changes
- Removed `newfolder()` from public API (was unused and had inconsistent error handling)
- Updated `__all__` exports to reflect removed function

### Documentation
- Added comprehensive code analysis report documenting all issues and fixes
- Updated implementation summary with v0.1.1 improvements

## [0.1.0] - 2026-03-14

### Security Fixes
- **CRITICAL**: Fixed path traversal vulnerability in `dicomdir_split.py` by adding `sanitize_path_component()` function to sanitize user-provided DICOM metadata (PatientID, StudyDescription, SeriesDescription) before using in file paths
- **CRITICAL**: Fixed unsafe temporary directory handling in `nifti_convert.py` by replacing hardcoded `./tmp/` with `tempfile.TemporaryDirectory()` context manager for thread-safe, automatic cleanup

### Bug Fixes
- Fixed `newfolder2()` bug in `util.py` where created folder path didn't match returned path (inconsistent underscore usage)
- Fixed file extension handling in `newfilename()` by replacing `split('.')` with `os.path.splitext()` to properly handle multi-dot filenames (e.g., `file.tar.gz`)
- Fixed dead code in `resample_nifti_to()` that was setting metadata on wrong image object (`img_in` instead of `img_out`)
- Fixed unsafe list indexing in `dicom2niftiSUV()` by adding empty directory checks before accessing `os.listdir()[0]`

### Error Handling Improvements
- Added comprehensive error handling for DICOM tag access in `dicom2niftiSUV()` with specific exception types (AttributeError, IndexError, KeyError)
- Replaced bare `except:` clauses with specific `except AttributeError:` in `dicomdir_split.py`
- Replaced `print()` error messages with proper `raise ValueError()` exceptions in `dicom2niftiSUV()`
- Added informative error messages for missing DICOM tags and empty directories

### Code Quality Improvements
- Fixed mutable default argument anti-pattern in `mipz()` by changing `space=[0, 0]` to `space=None`
- Fixed variable shadowing of built-in `slice` by renaming to `max_slice` in `mipz()`
- Fixed None comparison from `if colorrange == None:` to `if colorrange is None:` in `imagesc3s.py`
- Fixed boolean comparison from `if isBQML==True:` to `if isBQML:` in `nifti_convert.py`
- Replaced wildcard import `from .util import *` with explicit imports in `__init__.py`
- Updated placeholder `__author__ = "Your Name"` to actual author name

### Documentation
- Added comprehensive docstrings to utility functions in `util.py`
- Improved docstring formatting and parameter descriptions across modules
- Fixed typo: "acvitity" → "activity" in `nifti_convert.py`

### API Changes
- Added new public function `sanitize_path_component()` for safe path handling
- Updated `__all__` in `__init__.py` to include explicit utility function exports

## [0.0.10] - Previous Release
- Initial functionality for medical image visualization and processing
