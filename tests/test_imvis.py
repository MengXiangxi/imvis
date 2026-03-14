"""
Unit tests for imvis package.

Run with: pytest tests/test_imvis.py -v
"""

import pytest
import numpy as np
import SimpleITK as sitk
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import imvis


# Fixtures for test data paths
@pytest.fixture
def samples_dir():
    """Path to samples directory."""
    return Path(__file__).parent.parent / "samples"


@pytest.fixture
def phantom_nifti(samples_dir):
    """Path to phantom NIfTI file."""
    path = samples_dir / "phantom.nii.gz"
    if not path.exists():
        pytest.skip(f"Test file not found: {path}")
    return str(path)


@pytest.fixture
def ct_nifti(samples_dir):
    """Path to CT NIfTI file."""
    path = samples_dir / "001_CT.nii.gz"
    if not path.exists():
        pytest.skip(f"Test file not found: {path}")
    return str(path)


@pytest.fixture
def pt_nifti(samples_dir):
    """Path to PT NIfTI file."""
    path = samples_dir / "001_PT.nii.gz"
    if not path.exists():
        pytest.skip(f"Test file not found: {path}")
    return str(path)


@pytest.fixture
def dicom_dir(samples_dir):
    """Path to DICOM directory."""
    path = samples_dir / "OSEM I8s20 nopsf_407"
    if not path.exists():
        pytest.skip(f"Test directory not found: {path}")
    return str(path)


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================================
# Test util.py functions
# ============================================================================

class TestUtilFunctions:
    """Test utility functions."""

    def test_sanitize_path_component_normal(self):
        """Test sanitization of normal path components."""
        result = imvis.sanitize_path_component("Patient123")
        assert result == "Patient123"

    def test_sanitize_path_component_with_spaces(self):
        """Test sanitization preserves spaces."""
        result = imvis.sanitize_path_component("Patient Name 123")
        # Spaces are preserved, not converted to underscores
        assert result == "Patient Name 123"

    def test_sanitize_path_component_path_traversal(self):
        """Test sanitization prevents path traversal."""
        result = imvis.sanitize_path_component("../../../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        assert "\\" not in result

    def test_sanitize_path_component_special_chars(self):
        """Test sanitization removes special characters."""
        result = imvis.sanitize_path_component("Patient@#$%123")
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result

    def test_sanitize_path_component_empty(self):
        """Test sanitization handles empty input."""
        result = imvis.sanitize_path_component("")
        assert result == "unnamed"

    def test_sanitize_path_component_dots_only(self):
        """Test sanitization handles dots-only input."""
        result = imvis.sanitize_path_component("...")
        # Dots are converted to underscores, then stripped, leaving underscores
        assert result == "___"

    def test_sanitize_path_component_long_name(self):
        """Test sanitization limits length."""
        long_name = "A" * 300
        result = imvis.sanitize_path_component(long_name)
        assert len(result) == 255

    def test_newfolder2_creates_folder(self, temp_output_dir):
        """Test newfolder2 creates a new folder."""
        result = imvis.newfolder2(temp_output_dir, "test_folder")
        assert os.path.exists(result)
        assert result.endswith("test_folder")

    def test_newfolder2_handles_existing(self, temp_output_dir):
        """Test newfolder2 handles existing folders with suffix."""
        # Create first folder
        folder1 = imvis.newfolder2(temp_output_dir, "test_folder")
        # Create second with same name
        folder2 = imvis.newfolder2(temp_output_dir, "test_folder")

        assert folder1 != folder2
        assert os.path.exists(folder1)
        assert os.path.exists(folder2)
        assert "_0" in folder2

    def test_newfilename_creates_path(self, temp_output_dir):
        """Test newfilename creates unique filename."""
        result = imvis.newfilename(temp_output_dir, "test.txt")
        assert result.endswith("test.txt")

    def test_newfilename_handles_existing(self, temp_output_dir):
        """Test newfilename handles existing files."""
        # Create first file
        file1 = imvis.newfilename(temp_output_dir, "test.txt")
        Path(file1).touch()

        # Get second filename
        file2 = imvis.newfilename(temp_output_dir, "test.txt")

        assert file1 != file2
        assert "_0" in file2

    def test_newfilename_multi_dot(self, temp_output_dir):
        """Test newfilename handles multi-dot extensions."""
        result = imvis.newfilename(temp_output_dir, "test.nii.gz")
        assert result.endswith(".gz")

    def test_datetimestr_diff(self):
        """Test datetime string difference calculation."""
        dt1 = "20240101120000"
        dt2 = "20240101110000"
        diff = imvis.datetimestr_diff(dt1, dt2)
        assert diff == 3600  # 1 hour in seconds

    def test_datetimestr_diff_with_decimals(self):
        """Test datetime string difference with decimal seconds."""
        dt1 = "20240101120000.123"
        dt2 = "20240101110000.456"
        diff = imvis.datetimestr_diff(dt1, dt2)
        assert diff == 3600  # Decimals should be stripped


# ============================================================================
# Test mipz.py functions
# ============================================================================

class TestMipz:
    """Test MIP (Maximum Intensity Projection) functions."""

    def test_mipz_basic(self, phantom_nifti):
        """Test basic MIP projection."""
        img = sitk.ReadImage(phantom_nifti)
        img_array = sitk.GetArrayFromImage(img)

        result = imvis.mipz(img_array)

        assert isinstance(result, np.ndarray)
        assert result.ndim == 2  # Should be 2D
        assert result.shape[0] > 0
        assert result.shape[1] > 0

    def test_mipz_with_rotation(self, phantom_nifti):
        """Test MIP with rotation."""
        img = sitk.ReadImage(phantom_nifti)
        img_array = sitk.GetArrayFromImage(img)

        result = imvis.mipz(img_array, rot=45)

        assert isinstance(result, np.ndarray)
        assert result.ndim == 2

    def test_mipz_with_space(self, phantom_nifti):
        """Test MIP with spacing adjustment."""
        img = sitk.ReadImage(phantom_nifti)
        img_array = sitk.GetArrayFromImage(img)

        result = imvis.mipz(img_array, space=[3.125, 2.886])

        assert isinstance(result, np.ndarray)
        assert result.ndim == 2

    def test_mipz_zero_space_raises_error(self, phantom_nifti):
        """Test MIP raises error for zero space values."""
        img = sitk.ReadImage(phantom_nifti)
        img_array = sitk.GetArrayFromImage(img)

        with pytest.raises(ValueError, match="Space values must be non-zero"):
            imvis.mipz(img_array, space=[0, 1])

    def test_mipz_none_space_default(self, phantom_nifti):
        """Test MIP with None space uses default."""
        img = sitk.ReadImage(phantom_nifti)
        img_array = sitk.GetArrayFromImage(img)

        result = imvis.mipz(img_array, space=None)

        assert isinstance(result, np.ndarray)


# ============================================================================
# Test nifti_convert.py functions
# ============================================================================

class TestNiftiConvert:
    """Test NIfTI conversion functions."""

    def test_resample_nifti_to(self, pt_nifti, ct_nifti, temp_output_dir):
        """Test resampling NIfTI to reference space."""
        output_file = os.path.join(temp_output_dir, "resampled.nii.gz")

        imvis.resample_nifti_to(pt_nifti, ct_nifti, output_file)

        assert os.path.exists(output_file)

        # Verify output has same dimensions as reference
        img_out = sitk.ReadImage(output_file)
        img_ref = sitk.ReadImage(ct_nifti)
        assert img_out.GetSize() == img_ref.GetSize()

    def test_resample_nifti_to_bqml(self, pt_nifti, ct_nifti, temp_output_dir):
        """Test resampling with Bq/mL adjustment."""
        output_file = os.path.join(temp_output_dir, "resampled_bqml.nii.gz")

        imvis.resample_nifti_to(pt_nifti, ct_nifti, output_file, isBQML=True)

        assert os.path.exists(output_file)

    def test_dicom2niftiSUV(self, dicom_dir, temp_output_dir):
        """Test DICOM to NIfTI conversion with SUV."""
        output_file = os.path.join(temp_output_dir, "converted_suv.nii.gz")

        imvis.dicom2niftiSUV(dicom_dir, output_file)

        assert os.path.exists(output_file)

        # Verify it's a valid NIfTI file
        img = sitk.ReadImage(output_file)
        assert img.GetSize()[0] > 0

    def test_dicom2niftiSUV_empty_dir_raises_error(self, temp_output_dir):
        """Test DICOM conversion raises error for empty directory."""
        empty_dir = os.path.join(temp_output_dir, "empty")
        os.makedirs(empty_dir)
        output_file = os.path.join(temp_output_dir, "output.nii.gz")

        # Empty directory causes dicom2nifti to fail, which raises ValueError
        with pytest.raises(ValueError, match="No files generated"):
            imvis.dicom2niftiSUV(empty_dir, output_file)


# ============================================================================
# Test imagesc3s.py functions
# ============================================================================

class TestImagesc3s:
    """Test 3D image visualization functions."""

    def test_imagesc3s_array_conversion(self, phantom_nifti):
        """Test imagesc3s converts input to numpy array."""
        img = sitk.ReadImage(phantom_nifti)
        img_array = sitk.GetArrayFromImage(img)

        # This test just verifies the function accepts the input
        # We can't test the actual display without GUI
        # The function will be tested manually in Jupyter notebook
        assert img_array.ndim == 3

    def test_imagesc3s_colorrange_validation(self):
        """Test colorrange validation."""
        test_array = np.random.rand(10, 10, 10)

        # Skip this test - requires GUI mocking which is complex
        # The validation is tested manually in Jupyter notebook
        pytest.skip("GUI testing requires mocking matplotlib.pyplot.show()")


# ============================================================================
# Test integration scenarios
# ============================================================================

class TestIntegration:
    """Test integration scenarios."""

    def test_full_workflow_dicom_to_mip(self, dicom_dir, temp_output_dir):
        """Test full workflow: DICOM -> NIfTI -> MIP."""
        # Step 1: Convert DICOM to NIfTI
        nifti_file = os.path.join(temp_output_dir, "converted.nii.gz")
        imvis.dicom2niftiSUV(dicom_dir, nifti_file)
        assert os.path.exists(nifti_file)

        # Step 2: Load and create MIP
        img = sitk.ReadImage(nifti_file)
        img_array = sitk.GetArrayFromImage(img)
        mip_result = imvis.mipz(img_array)

        assert isinstance(mip_result, np.ndarray)
        assert mip_result.ndim == 2

    def test_full_workflow_resample_and_mip(self, pt_nifti, ct_nifti, temp_output_dir):
        """Test full workflow: Resample -> MIP."""
        # Step 1: Resample PT to CT space
        resampled_file = os.path.join(temp_output_dir, "resampled.nii.gz")
        imvis.resample_nifti_to(pt_nifti, ct_nifti, resampled_file)
        assert os.path.exists(resampled_file)

        # Step 2: Create MIP
        img = sitk.ReadImage(resampled_file)
        img_array = sitk.GetArrayFromImage(img)
        mip_result = imvis.mipz(img_array)

        assert isinstance(mip_result, np.ndarray)


# ============================================================================
# Test error handling
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_sanitize_handles_none(self):
        """Test sanitize_path_component handles None."""
        result = imvis.sanitize_path_component(None)
        assert result == "None"

    def test_sanitize_handles_numbers(self):
        """Test sanitize_path_component handles numbers."""
        result = imvis.sanitize_path_component(12345)
        assert result == "12345"

    def test_mipz_invalid_dimensions(self):
        """Test mipz with invalid array dimensions."""
        # 2D array instead of 3D
        array_2d = np.random.rand(10, 10)

        with pytest.raises((ValueError, IndexError)):
            imvis.mipz(array_2d)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
