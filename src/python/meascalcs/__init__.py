__all__ = ['fft', 'linToLog']

import ctypes as ct
import os

import numpy as np

WRITEABLE_ALIGNED = 'F_CONTIGUOUS,WRITEABLE,ALIGNED,OWNDATA'
WRITEABLE_ALIGNED_ARR = WRITEABLE_ALIGNED.split(',')
ALIGNED = 'F_CONTIGUOUS,ALIGNED,OWNDATA'
ALIGNED_ARR = ALIGNED.split(',')

# Load the DLL (from a specific location)
# TODO load this properly
os.environ['PATH'] = 'C:\\Users\\mattk\\github\\pypolarmap\\dlls\\gl;' + os.environ['PATH']
# _path = os.path.abspath(os.path.join(os.path.dirname('__file__'), '../../dlls/gl'))
# lib = np.ctypeslib.load_library('MeasCalcs', _path)
lib = np.ctypeslib.load_library('MeasCalcs', 'C:\\Users\\mattk\\github\\pypolarmap\\dlls\\gl')

# FFT setup
fft_func = getattr(lib, 'FFT')
fft_func.restype = None
fft_func.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags=WRITEABLE_ALIGNED),
    ct.POINTER(ct.c_int32)
]

# LinToLog setup
linToLog_func = getattr(lib, 'LinToLog')
linToLog_func.restype = None
linToLog_func.argtypes = [
    # COMPLEX(8), intent(in):: DataIn(0:NumFFTPts)        ! FFT data in at all angles
    np.ctypeslib.ndpointer(dtype=np.complex128, ndim=1, flags=ALIGNED),
    # real(8), intent(in) :: DeltaF                      ! the frequency delta
    ct.c_double,
    # integer, intent(in):: NumFFTPts                    ! the number of FFT points in the input
    ct.c_int32,
    # COMPLEX(8), intent(out) :: DataOut(0:NumLogPts)    ! The interpolated log frequency output
    np.ctypeslib.ndpointer(dtype=np.complex128, ndim=1, flags=WRITEABLE_ALIGNED),
    # integer, intent(in) :: NumLogPts                   ! number of smoothed output points ‐ log scaled
    ct.c_int32,
    # real(8), intent(out) :: Freqs(0:NumLogPts)          ! the Array of output frequencies
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags=WRITEABLE_ALIGNED),
]

# smooth setup
smooth_func = getattr(lib, 'Smooth')
smooth_func.restype = None
smooth_func.argtypes = [
    # ByRef Data_in As Double
    ct.POINTER(ct.c_double),
    # ByVal Freqs() As Double
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags=WRITEABLE_ALIGNED),
    # ByVal numpts_ As Integer
    ct.c_int32,
    # ByVal atype As Integer
    ct.c_int32
]


def erbspace(low, high, N, earQ=9.26449, minBW=24.7, order=1):
    '''
    copied from https://github.com/brian-team/brian
    '''
    low = float(low)
    high = float(high)
    cf = -(earQ * minBW) + np.exp(
        (np.arange(N)) * (-np.log(high + earQ * minBW) + np.log(low + earQ * minBW)) / (N - 1)) * (high + earQ * minBW)
    cf = cf[::-1]
    return cf


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


def linToLog(linearFreqs, freqStep):
    '''
    converts a linearly spaced dataset to a log spaced one.
    :param linearFreqs: the input data as a 1 dimensional ndarray of complex numbers (as output by fft)
    :param freqStep: the frequency step in the input data.
    :return: the log spaced complex data.
    '''
    inputData = np.require(linearFreqs, dtype=np.complex128, requirements=ALIGNED_ARR)
    freqStep = ct.c_double(freqStep)
    inputPts = ct.c_int32(linearFreqs.shape[0])
    outputPts = min(200, inputPts.value)
    outputData = np.require(np.zeros(outputPts, dtype=np.complex128), dtype=np.complex128,
                            requirements=WRITEABLE_ALIGNED_ARR)
    logFreqs = np.require(erbspace(20, 24000, outputPts), dtype=np.float64, requirements=WRITEABLE_ALIGNED_ARR)
    logPoints = ct.c_int32(outputPts)
    linToLog_func(inputData, freqStep, inputPts, outputData, logPoints, logFreqs)
    return outputData, logFreqs
