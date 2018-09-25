import logging
import math
import os
import sys
import time

from matplotlib.pyplot import box

from model.log import to_millis

__all__ = ['fft', 'linToLog', 'calSpatial', 'calPolar']

import ctypes as ct

import numpy as np

logger = logging.getLogger('meascalcs')

WRITEABLE_ALIGNED = 'F_CONTIGUOUS,WRITEABLE,ALIGNED,OWNDATA'
WRITEABLE_ALIGNED_ARR = WRITEABLE_ALIGNED.split(',')
ALIGNED = 'F_CONTIGUOUS,ALIGNED,OWNDATA'
ALIGNED_ARR = ALIGNED.split(',')

# Load the DLL (from a specific location)
if getattr(sys, 'frozen', False):
    dllPath = sys._MEIPASS
else:
    dllPath = os.path.abspath(os.path.join(os.path.dirname('__file__'), '../resources'))
if os.path.exists(os.path.join(dllPath, 'MeasCalcs.dll')):
    lib = np.ctypeslib.load_library('MeasCalcs', dllPath)
else:
    raise ValueError('oi vey')

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
    start = time.time()
    # minimum size of 512 to provide enough space for the linToLog to work sensibly
    nextPower = np.ceil(max(np.log2(data.shape[0]), 9))
    padding = int(np.power(2, nextPower) - data.shape[0])
    paddedData = np.pad(data, (0, padding), mode='constant') if padding > 0 else data
    numPoints = ct.c_int32(paddedData.shape[0])
    paddedData = np.require(paddedData, dtype=np.float64, requirements=WRITEABLE_ALIGNED_ARR)
    fft_func(paddedData, numPoints)
    result = np.concatenate(
        ([complex(paddedData[0], 0)], paddedData[2:].view(dtype=np.complex128), [complex(paddedData[1], 0)]))
    end = time.time()
    logger.debug(f"fft - {to_millis(start, end)}ms")
    return result, numPoints.value


# no of log spaced points to use given a set number of linear points
logPts = {
    64: 15,
    128: 30,
    256: 50,
    512: 100,
    1024: 200,
    2048: 300,
    4096: 300
}

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


def linToLog(linearFreqs, freqStep):
    '''
    converts a linearly spaced dataset to a log spaced one.
    :param linearFreqs: the input data as a 1 dimensional ndarray of complex numbers (as output by fft)
    :param freqStep: the frequency step in the input data.
    :return: the log spaced complex data.
    '''
    start = time.time()
    inputData = np.require(linearFreqs, dtype=np.complex128, requirements=ALIGNED_ARR)
    freqStep = ct.c_double(freqStep)
    inputPts = ct.c_int32(linearFreqs.shape[0] - 1)
    if inputPts.value in logPts:
        outputPts = logPts[inputPts.value]
    else:
        outputPts = min(128, int(round(linearFreqs.shape[0] / 4)))
    outputData = np.require(np.zeros(outputPts, dtype=np.complex128), dtype=np.complex128,
                            requirements=WRITEABLE_ALIGNED_ARR)
    logFreqs = np.require(np.logspace(math.log10(20), math.log10(20000), num=outputPts, endpoint=True),
                          dtype=np.float64, requirements=WRITEABLE_ALIGNED_ARR)
    logPoints = ct.c_int32(outputPts - 1)
    linToLog_func(inputData, freqStep, inputPts, outputData, logPoints, logFreqs)
    end = time.time()
    logger.debug(f"linToLog - {to_millis(start, end)}ms")
    return outputData.copy(), logFreqs.copy()


# calspatial setup
calspatial_func = getattr(lib, 'CalSpatial')
calspatial_func.restype = None
calspatial_func.argtypes = [
    # DataIn( 0:NumAngleIn-1, 0:NumLogPts-1) - COMPLEX(8), intent(in)
    np.ctypeslib.ndpointer(dtype=np.complex128, ndim=2, flags=ALIGNED),
    # AnglesIn( 0:NumAngleIn-1) - REAL(8), intent(in)
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags=ALIGNED),
    # NumAngleIn - integer, intent(in)
    ct.c_int32,
    # Freqs - REAL(8), intent(in):: Freqs(0:NumLogPts-1)
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags=ALIGNED),
    # NumLogPts - integer, intent(in)
    ct.c_int32,
    # DataOut - COMPLEX(8), intent(out):: DataOut( 0:NumCoefs-1, 0:NumLogPts-1 )
    np.ctypeslib.ndpointer(dtype=np.complex128, ndim=2, flags=WRITEABLE_ALIGNED),
    # NumCoefs - integer, intent(in)
    ct.c_int32,
    # MeasureR - Real(8), intent(in)
    ct.c_double,
    # TransFreq - Real(8), intent(in)
    ct.c_double,
    # LFGain - Real(8), intent(in)
    ct.c_double,
    # BoxRadius - Real(8), intent(in)
    ct.c_double,
    # Radius - Real(8), intent(in)
    ct.c_double,
    # F0 - Real(8), intent(in)
    ct.c_double,
    # Q0 - Real(8), intent(in)
    ct.c_double,
    # SourceType - integer, intent(in)
    ct.c_int32
]


def calSpatial(logSpacedMeasurements, logSpacedFreqs, anglesInRadians, measurementDistance, driverRadius,
               fitCoefficientsExpected=14, transFreq=200, lowFreqGain=0.0, boxRadius=0.25, f0=70, q0=0.7,
               sourceType=0):
    '''
    :param logSpacedMeasurements: The measurement data as output by linToLog
    :param logSpacedFreqs: The frequencies for the logSpaced data
    :param anglesInRadians: the angles the data is taken (radians)
    :param fitCoefficientsExpected: Number of fit coefficients
    :param measurementDistance: Measurement distance in m
    :param transFreq: blend frequency
    :param lowFreqGain: blend adjust
    :param boxRadius: blend adjust
    :param driverRadius: driver radius
    :param f0: source resonance
    :param q0: source Q
    :param sourceType: dipole f
    :return: the modal parameters by frequency.
    '''
    start = time.time()
    if driverRadius >= boxRadius:
        raise ValueError('driverRadius must be less than boxRadius')
    dataOut = np.require(np.zeros((fitCoefficientsExpected, logSpacedFreqs.shape[0]), dtype=np.complex128),
                         dtype=np.complex128, requirements=WRITEABLE_ALIGNED_ARR)
    calspatial_func(np.require(logSpacedMeasurements, dtype=np.complex128, requirements=ALIGNED_ARR),
                    np.require(anglesInRadians, dtype=np.float64, requirements=ALIGNED_ARR),
                    ct.c_int32(anglesInRadians.shape[0]),
                    np.require(logSpacedFreqs, dtype=np.float64, requirements=ALIGNED_ARR),
                    ct.c_int32(logSpacedFreqs.shape[0]),
                    dataOut,
                    ct.c_int32(fitCoefficientsExpected),
                    ct.c_double(measurementDistance),
                    ct.c_double(transFreq),
                    ct.c_double(lowFreqGain),
                    ct.c_double(boxRadius),
                    ct.c_double(driverRadius),
                    ct.c_double(f0),
                    ct.c_double(q0),
                    ct.c_int32(sourceType))
    end = time.time()
    logger.debug(f"calSpatial ({to_millis(start, end)}ms) - numAngleIn: {anglesInRadians.shape[0]}, "
                 f"numLogPts: {logSpacedFreqs.shape[0]}, numCoefs: {fitCoefficientsExpected}, "
                 f"measureR: {measurementDistance}, transFreq: {transFreq}, lfGain: {lowFreqGain}, "
                 f"boxRadius: {boxRadius}, radius: {driverRadius}, F0: {f0}, Q0: {f0}, SourceType: {sourceType}")
    return dataOut.copy()


class Complex64(ct.Structure):
    _fields_ = [("real", ct.c_double), ("imag", ct.c_double)]


# CalPolar setup
calpolar_func = getattr(lib, 'CalPolar')
calpolar_func.restype = Complex64
calpolar_func.argtypes = [
    # ByRef DataIn As Complex
    np.ctypeslib.ndpointer(dtype=np.complex128, ndim=1, flags=ALIGNED),
    # ByVal NumCoef As Integer
    ct.c_int32,
    # ByVal angl As Double
    ct.c_double,
    # ByVal freq As Double
    ct.c_double,
    # ByVal farnum As Double
    ct.c_double,
    # ByVal Velnum As Double
    ct.c_double
]


def calPolar(modalData, angle, freq, boxRadius):
    '''
    :param modalData: a vector of modal parameters at the specified frequency.
    :param angle: the angle we want to calculate the pressure response at.
    :param freq: the frequency we want to calculate the pressure response at.
    :param boxRadius: the radius of a sphere with the same valume as the enclosure.
    :return: the polar response.
    '''
    start = time.time()
    arg1 = np.require(modalData, dtype=np.complex128, requirements=ALIGNED_ARR)
    result = calpolar_func(arg1, modalData.size, math.radians(angle), freq, 0.10, boxRadius)
    retVal = complex(result.real, result.imag)
    end = time.time()
    logger.debug(f"calPolar ({to_millis(start, end)}ms) - numCoef: {modalData.size}, angl: {math.radians(angle):.3f}, "
                 f"freq: {freq:.1f}, farnum: 0.10, velnum: {boxRadius}")
    return retVal


# smooth setup
smooth_func = getattr(lib, 'Smooth')
smooth_func.restype = None
smooth_func.argtypes = [
    # ByRef Data_in As Double
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags=WRITEABLE_ALIGNED),
    # ByVal Freqs() As Double
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags=ALIGNED),
    # ByVal numpts_ As Integer
    ct.c_int32,
    # ByVal atype As Integer
    ct.c_int32
]

# mapping of supporting smoothing types to indexes to pass to the smooth function
SMOOTH_TYPES = dict(
    [(a[1], a[0]) for a in enumerate(['1/3 Octave', '1/6 Octave', '1/12 Octave', 'CB Zwicker', 'CB Moore', 'Narrow'])]
)


def smooth(data, freqs, smoothingType):
    '''
    Smoothes the data according to the specified type.
    :param data: the data to smooth.
    :param freqs: the log spaced frequencies.
    :param smoothingType: the smoothing algorithm to use.
    :return: the smoothed data.
    '''
    start = time.time()
    dataIn = np.require(np.copy(data), dtype=np.float64, requirements=WRITEABLE_ALIGNED_ARR)
    freqs = np.require(freqs, dtype=np.float64, requirements=ALIGNED_ARR)
    if smoothingType in SMOOTH_TYPES:
        smooth_func(dataIn, freqs, ct.c_int32(freqs.size), ct.c_int32(SMOOTH_TYPES[smoothingType]))
        end = time.time()
        logger.debug(f"smooth ({to_millis(start, end)}ms) - {smoothingType}")
        return dataIn.copy()
    else:
        raise ValueError('Unknown smoothing algorithm ' + str(smoothingType))


# CalPower
calpower_func = getattr(lib, 'CalPower')
calpower_func.restype = ct.c_double
calpower_func.argtypes = [
    # ByRef DataIn As Complex
    np.ctypeslib.ndpointer(dtype=np.complex128, ndim=1, flags=ALIGNED),
    # ByVal NumCoef As Integer
    ct.c_int32,
    # ByVal freq As Double
    ct.c_double,
    # ByVal farnum As Double
    ct.c_double
]


def calPower(modalData, freq, boxRadius):
    '''
    Calculates the power response at the given frequency for the modal data.
    :param modalData: the data.
    :param freq: the freq at which we want to calculate the power response.
    :param boxRadius: the radius of a sphere with the same valume as the enclosure.
    :return: the power response.
    '''
    start = time.time()
    arg1 = np.require(modalData, dtype=np.complex128, requirements=ALIGNED_ARR)
    result = calpower_func(arg1, modalData.size, freq, boxRadius)
    end = time.time()
    logger.debug(
        f"calPower ({to_millis(start, end)}ms) - numCoef: {modalData.size}, freq: {freq:.1f}, farnum: {boxRadius}")
    return result

# CalVelocity
# Declare Function CalVelocity Lib "MeasCalcs.dll" (ByRef DataIn As Complex, _
#                                                       ByVal NumCoef As Integer, _
#                                                       ByVal angl As Double, _
#                                                       ByVal freq As Double, _
#                                                       ByVal MeasRad As Double) As Complex
#
#
# Complex(8) function CalVelocity( DataIn, NumCoefs, Theta, Freq, MeasRadius)
#
# IMPLICIT NONE
# ! Specify that CalVelocity is exported to a DLL
# !DEC$ ATTRIBUTES DLLEXPORT :: CalVelocity
# !DEC$ ATTRIBUTES REFERENCE :: DataIn
# !DEC$ ATTRIBUTES Value :: NumCoefs
# !DEC$ ATTRIBUTES Value :: Theta
# !DEC$ ATTRIBUTES Value :: freq
# !DEC$ ATTRIBUTES Value :: MeasRadius
#
# integer, intent(in):: NumCoefs
#
# complex(8), intent(in):: DataIn(0:NumCoefs-1)
# real(8), intent(in) :: Theta,freq, MeasRadius
