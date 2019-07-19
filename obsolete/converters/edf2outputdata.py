#!/usr/bin/env python
#
# Convert edf data to text files to load into OutputData from GISASFW 

import sys
import edf_reader
#from numpy import *
import matplotlib
import gzip
from libBornAgainCore import *

import pylab
import numpy
import math


DISTANCE = 0.909  # m
PIX_SIZE = 4*41.74e-6  # m
CENTER_X = 108.2
CENTER_Y = 942.0

# 004_230_P144_im_full.edf - Fig 4.17 on page 64 of Elisabeth's PhD
# 001_150_P109_im_full.edf - Fig 4.19 on page 65 of Elisabeth's PhD


def plot_with_pylab(data):
    result = data.getArray() +1 # for log scale
    axis_phi = data.getAxis(0)
    axis_alpha = data.getAxis(1)

    #im = pylab.imshow(numpy.rot90(result, 1),
    #             extent=[axis_phi.getMin(), axis_phi.getMax(), axis_alpha.getMin(), axis_alpha.getMax()], interpolation='None', norm=matplotlib.colors.LogNorm(), aspect='auto')

    im = pylab.imshow(numpy.rot90(result, 1), norm=matplotlib.colors.LogNorm(vmin=100, vmax=1e6),
             extent=[axis_phi.getMin(), axis_phi.getMax(), axis_alpha.getMin(), axis_alpha.getMax()])


    pylab.colorbar(im)
    pylab.xlabel(r'$\phi_f$', fontsize=20)
    pylab.ylabel(r'$\alpha_f$', fontsize=20)


#-----------------------------------------------------------------------------
# converting edf data to another formats
# (png, txt) for the moment
#-----------------------------------------------------------------------------
def make_file(filename):
    data,info=edf_reader.import_edf_file(filename)
    file_title=info['Title'].split('(')[0]
    lamda=info['lambda'] # in A
    t=info['ExposureTime']
    data/=t

    nx = info['xdim']
    ny = info['ydim']

    if 'Center_1' in info:
        exit("Wrong format")

    # The grid orientation follows the MATLAB convention: an array C with shape (nrows, ncolumns) is plotted
    # with the column number as X and the row number as Y, increasing up; hence it is plotted the way the
    # array would be printed, except that the Y axis is reversed.
    # e.g. here we have data[Qz][Qy] (data[theta][phi])
    data=data[ ::-1,:]

    nphi = nx
    ntheta = ny

    # xedges = numpy.arange(nphi+1) - CENTER_X
    # yedges = -numpy.arange(ntheta+1) + CENTER_Y
    #
    # print numpy.arange(ntheta+1)
    # print yedges
    #
    # phi_edges=numpy.arctan2(PIX_SIZE*xedges,DISTANCE)
    # tth_edges=numpy.arctan2(PIX_SIZE*yedges,DISTANCE)
    # tth_edges=tth_edges[ ::-1]

    y_shift = -(1024.0 - CENTER_Y)*PIX_SIZE
    print "y_shift", y_shift
    tth_edges = []
    for i_theta in range(0, ntheta+1):
        tth_edges.append(numpy.arctan2(y_shift + i_theta*PIX_SIZE, DISTANCE) - 0.4*numpy.pi/180.)

    phi_edges = []
    x_shift = CENTER_X*PIX_SIZE
    print "x_shift", x_shift
    for i_phi in range(0, nphi+1):
        phi_edges.append(numpy.arctan2(i_phi*PIX_SIZE - x_shift, DISTANCE))

    intensity = IntensityData()
    intensity.addAxis(VariableBinAxis("phi_f", nphi, phi_edges))
    intensity.addAxis(VariableBinAxis("alpha_f", ntheta, tth_edges))

    for i_phi in range(0, nphi):
        for i_theta in range(0, ntheta):
            index = i_theta + ntheta*i_phi
            intensity[index] = data[i_theta][i_phi]

    clip = IntensityDataFunctions.createClippedDataSet(intensity, 0.014, 0.0, 0.051, 0.048)  # 004_230_P144_cut1.int

    IntensityDataIOFactory.writeIntensityData(clip, filename.rsplit('.',1)[0]+'.int')

    fig = pylab.figure(1)
    plot_with_pylab(intensity)
    pylab.grid(b=True, which='major', color='k', linestyle='-', zorder=1)
    pylab.figure(2)
    plot_with_pylab(clip)

    pylab.show()


def run(args=None):
    for filename in args:
        print filename, '->', filename.rsplit('.',1)[0]+'.png'
        make_file(filename)

if __name__ == '__main__':
    if len(sys.argv)==1:
        exit('Usage: edf2png.py name1.edf name2.edf ...')
    run(sys.argv[1:])

