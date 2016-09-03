import pyqtgraph as pg
import pyqtgraph.metaarray as metaarray
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as pgl
import scipy.ndimage as ndi
import numpy as np

pg.mkQApp()


view = pgl.GLViewWidget()

atlas = metaarray.MetaArray(file='ccf.ma', readAllData=True)

img = np.ascontiguousarray(atlas.asarray()[::8,::8,::8])

# render volume
#vol = np.empty(img.shape + (4,), dtype='ubyte')
#vol[:] = img[..., None]
#vol = np.ascontiguousarray(vol.transpose(1, 2, 0, 3))
#vi = pgl.GLVolumeItem(vol)
#self.glView.addItem(vi)
#vi.translate(-vol.shape[0]/2., -vol.shape[1]/2., -vol.shape[2]/2.)

verts, faces = pg.isosurface(ndi.gaussian_filter(img.astype('float32'), (2, 2, 2)), 5.0)
md = pgl.MeshData(vertexes=verts, faces=faces)
mesh = pgl.GLMeshItem(meshdata=md, smooth=True, color=[0.5, 0.5, 0.5, 0.2], shader='balloon')
mesh.setGLOptions('additive')
mesh.translate(-img.shape[0]/2., -img.shape[1]/2., -img.shape[2]/2.)
view.addItem(mesh)

view.show()
