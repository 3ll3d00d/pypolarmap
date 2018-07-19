import math

__all__ = ['fft', 'linToLog', 'calSpatial', 'calPolar']

import ctypes as ct

import numpy as np

WRITEABLE_ALIGNED = 'F_CONTIGUOUS,WRITEABLE,ALIGNED,OWNDATA'
WRITEABLE_ALIGNED_ARR = WRITEABLE_ALIGNED.split(',')
ALIGNED = 'F_CONTIGUOUS,ALIGNED,OWNDATA'
ALIGNED_ARR = ALIGNED.split(',')

# Load the DLL (from a specific location)
# TODO load this properly
# os.environ['PATH'] = 'C:\\Users\\mattk\\github\\pypolarmap\\dlls\\gl;' + os.environ['PATH']
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


def fft(data):
    '''
    :param data: the input data.
    :return: (the complex FFT'ed data, the number of points in the FFT)
    '''
    # minimum size of 512 to provide enough space for the linToLog to work sensibly
    nextPower = np.ceil(max(np.log2(data.shape[0]), 9))
    padding = int(np.power(2, nextPower) - data.shape[0])
    paddedData = np.pad(data, (0, padding), mode='constant') if padding > 0 else data
    numPoints = ct.c_int32(paddedData.shape[0])
    paddedData = np.require(paddedData, dtype=np.float64, requirements=WRITEABLE_ALIGNED_ARR)
    fft_func(paddedData, numPoints)
    return np.concatenate(([complex(paddedData[0], 0)], paddedData[2:].view(dtype=np.complex128),
                           [complex(paddedData[1], 0)])), numPoints.value


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
    :param boxRadius: the radius of enclosure.
    :return:
    '''
    arg1 = np.require(modalData, dtype=np.complex128, requirements=ALIGNED_ARR)
    result = calpolar_func(arg1, modalData.size, angle, freq, 0.10, boxRadius)
    retVal = complex(result.real, result.imag)
    return retVal


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
