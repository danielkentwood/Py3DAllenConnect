import pandas as pd
import scipy.ndimage as ndi
import numpy as np
import time

import pyqtgraph as pg
import pyqtgraph.opengl as pgl
pg.mkQApp()

def vis3D(brain_array,inj_array,pad = 30,ds_factor=6):
    
    # set up time variables
    now = time.time()
    now_start = now
    
    view = vis3D_glassBrain(brain_array,pad,ds_factor)
    print "build brain isosurface %0.2f" % (time.time() - now); now = time.time() 
    
    view = vis3D_projections(view,inj_array,ds_factor)
    print "build injection volume %0.2f" % (time.time() - now); now = time.time() 
    
    view.show()
    
    print "rendering %0.2f" % (time.time() - now); now = time.time() 
    print "total run time: %0.2f" % (time.time() - now_start)
    
    return view



def vis3D_glassBrain(brain_array,pad,ds_factor):
    
    # initialize the window
    view = pgl.GLViewWidget()   
    
    # downsample the brain image using the ds_factor
    img = brain_array[::ds_factor,::ds_factor,::ds_factor]
    
    # do padding of the brain to avoid holes during rendering
    pad_img = np.zeros((img.shape[0]+pad, img.shape[1]+pad, img.shape[2]+pad), dtype=img.dtype)
    pad_img[pad/2:pad/2+img.shape[0], pad/2:pad/2+img.shape[1], pad/2:pad/2+img.shape[2]] = img
    
    # build the brain isosurface
    verts, faces = pg.isosurface(ndi.gaussian_filter(pad_img.astype('float32'), (1, 1, 1)), 5.0)
    md = pgl.MeshData(vertexes=verts, faces=faces)
    mesh = pgl.GLMeshItem(meshdata=md, smooth=True, color=[0.5, 0.5, 0.5, 0.1], shader='balloon')
    mesh.setGLOptions('additive')
    mesh.translate(-pad_img.shape[0]*(ds_factor/2.), -pad_img.shape[1]*(ds_factor/2.), -pad_img.shape[2]*(ds_factor/2.))
    mesh.scale(ds_factor,ds_factor,ds_factor)
    mesh.rotate(-90, 1, 0, 0)
    view.addItem(mesh)
    view.setCameraPosition(distance=1000, elevation=20, azimuth=90)
    view.setWindowTitle('Consciousness is a grand illusion')
    view.show()

    return view


def vis3D_projections(view,inj_array,ds_factor=1):
    ds_factor=1 # disabled ds_factor because it isn't implemented
    # render the injection(s) as a volume
    # inj_array should be a list of tuples, with the first element in the tuple
    # being the plotting color (a RGB value), and the second element being the 
    # ND-array of the volumetric data for a given injection
    vols = np.zeros(inj_array[0][1].shape + (4,), dtype='float32')
    for inj in range(len(inj_array)):
        col = inj_array[inj][0]
        vols[...,0] += col[0] * inj_array[inj][1] # red channel
        vols[...,1] += col[1] * inj_array[inj][1] # green channel
        vols[...,2] += col[2] * inj_array[inj][1] # blue channel
        vols[...,3] += inj_array[inj][1] * 255    # alpha channel

    # Set alpha and make sure the maximum alpha is 255
    vols[...,3] *= 5
    vols[...,3] = np.clip(vols[...,3],0,255)

    # now add the volume to the view window
    vi = pgl.GLVolumeItem(vols)
    vi.translate(-vols.shape[0]*(ds_factor/2.), -vols.shape[1]*(ds_factor/2.), -vols.shape[2]*(ds_factor/2.))
    vi.scale(ds_factor,ds_factor,ds_factor)
    vi.setGLOptions('additive')
    vi.rotate(-90, 1, 0, 0)
    view.setCameraPosition(distance=1000, elevation=20, azimuth=90)
    view.addItem(vi)
    
    return view



def vis3D_structureMask(view,mask,maskCol,ds_factor):

    # downsample the brain image using the ds_factor
    img = mask[::ds_factor,::ds_factor,::ds_factor]

    # build the brain isosurface
    verts, faces = pg.isosurface(ndi.gaussian_filter(img.astype('float32'), (0.5, 0.5, 0.5)), .5)
    md = pgl.MeshData(vertexes=verts, faces=faces)
    meshMask = pgl.GLMeshItem(meshdata=md, smooth=True, color=[maskCol[0], maskCol[1], maskCol[2], 0.2], shader='balloon')
    meshMask.setGLOptions('additive')
    meshMask.translate(-img.shape[0]/2., -img.shape[1]/2., -img.shape[2]/2.)
    meshMask.scale(ds_factor,ds_factor,ds_factor)
    meshMask.rotate(-90, 1, 0, 0)
    view.addItem(meshMask)
    view.setCameraPosition(distance=1000, elevation=20, azimuth=90)
    view.show()

    return view


# def vis3D_getPath( target_voxel, experiment_id ) :
#     url = "http://api.brain-map.org/api/v2/data/query.json?criteria=service::mouse_connectivity_target_spatial"
#     url = url + "[seed_point$eq%s]" % ','.join([str(s) for s in target_voxel])
#     url = url + "[section_data_set$eq%d]" % experiment_id
#     response = urllib.urlopen(url)
#     data = json.loads(response.read())
#     data = [s['coord'] for s in data['msg'][0]['path']]
#     return data

# def vis3D_showPaths(view,paths,pathCols,ds_factor):
#     pts = paths[::ds_factor]
#     plt = pgl.GLLinePlotItem(pos=pts, color=pg.glColor([255,0,0,255]), width=2, antialias=True)
#     view.addItem(plt)
#     view.show()

#     return view








