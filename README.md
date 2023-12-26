# imvis

Interactive visualization of 3D medical images in python

## Installation

First, clone the repository and install the dependencies:

```bash
git clone xxx
```

Then, build and install the package (in your favorite conda env or venv):

```bash
pip install --upgrade setuptools
pip install --upgrade build

python -m build
pip install --force-reinstall ./dist/imvis-x-x-x-py3-none-any.whl
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

![imagesc3s: scroll](resources/imagesc3s_window.png)
