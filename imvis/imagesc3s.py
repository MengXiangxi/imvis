import matplotlib.pyplot as plt
import numpy as np

class IndexTracker:
    def __init__(self, ax, X, colormin, colormax, colormap):
        self.index = np.round(X.shape[-1] / 2).astype(int)
        self.X = X
        self.ax = ax
        self.im = ax.imshow(self.X[:, :, self.index], vmin=colormin, vmax=colormax, cmap=colormap)
        self.colorbar = plt.colorbar(self.im, ax=self.ax)
        ax.set_xticks([])
        ax.set_yticks([])
        self.update()

    def on_scroll(self, event):
        # print(event.button, event.step)
        increment = 1 if event.button == 'up' else -1
        max_index = self.X.shape[-1] - 1
        if self.index == 0 and increment == -1:
            self.index = max_index
        else:
            self.index = np.clip(self.index + increment, 0, max_index)
        self.update()

    def update(self):
        self.im.set_data(self.X[:, :, self.index])
        self.ax.set_title(
            f'Use scroll wheel to navigate\nindex {self.index}')
        self.im.axes.figure.canvas.draw()

def imagesc3s(mat3d, colorrange=None, cmap='hot'):
    """Display a 3D image stack as a series of 2D images in a scrollable window.
    The scroll wheel can be used to navigate through the stack.
    Parameters
    ----------
    mat3d : array_like
        3D array of image data
    colorrange : list, optional
        [min, max] of the color bar.
    cmap : string, optional
        Colormap to use. Default is 'hot'.
    """
    if not isinstance(mat3d, np.ndarray):
        mat3d = np.array(mat3d)

    if colorrange == None:
        colorrange = [0, np.max(mat3d)*0.1]

    if len(colorrange) != 2 or colorrange[0] > colorrange[1]:
        raise ValueError('colorrange must be a list of two numbers, with the first number smaller than the second number.')

    colormin = colorrange[0]
    colormax = colorrange[1]

    X = np.transpose(mat3d, (1,2,0))

    fig, ax = plt.subplots()
    # create an IndexTracker and make sure it lives during the whole
    # lifetime of the figure by assigning it to a variable
    tracker = IndexTracker(ax, X, colormin, colormax, cmap)

    fig.canvas.mpl_connect('scroll_event', tracker.on_scroll)
    plt.show()


if __name__ == '__main__':
    ### Based on the example from the matplotlib documentation
    ### https://matplotlib.org/stable/gallery/event_handling/image_slices_viewer.html
    import pydicom
    fname = "/path/to/dicom/file.dcm"
    fname = "//192.168.2.88/home/.Qsync/Sync/Research/20231019TCHAH/visualizeTomo/869"
    ds = pydicom.dcmread(fname)
    img = ds.pixel_array
    imagesc3s(img, [0, 6000])