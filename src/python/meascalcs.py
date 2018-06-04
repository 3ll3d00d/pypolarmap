__all__ = ['fft']

import ctypes as ct
import os

import numpy as np

WRITEABLE_ALIGNED = 'F_CONTIGUOUS,WRITEABLE,ALIGNED,OWNDATA'
WRITEABLE_ALIGNED_ARR = WRITEABLE_ALIGNED.split(',')
ALIGNED = 'F_CONTIGUOUS,ALIGNED,OWNDATA'
ALIGNED_ARR = ALIGNED.split(',')

# Load the DLL (from a specific location)
# TODO load from somewhere "official"
_path = os.path.abspath(os.path.join(os.path.dirname('__file__'), '../../dlls/gl'))
lib = np.ctypeslib.load_library('MeasCalcs', _path)

# FFT setup
fft_func = getattr(lib, 'FFT')
fft_func.restype = None
fft_func.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags=WRITEABLE_ALIGNED),
    ct.POINTER(ct.c_int32)
]


def fft(data):
    '''
    :param data: the input data.
    :return: (the complex FFT'ed data, the number of points in the FFT)
    '''
    nextPower = np.ceil(np.log2(data.shape[0]))
    padding = int(np.power(2, nextPower) - data.shape[0])
    paddedData = np.pad(data, (padding, 0), mode='constant')
    numPoints = ct.c_int32(paddedData.shape[0])
    paddedData = np.require(paddedData, dtype=np.float64, requirements=WRITEABLE_ALIGNED_ARR)
    fft_func(paddedData, numPoints)
    return paddedData.view(dtype=np.complex128), numPoints.value
