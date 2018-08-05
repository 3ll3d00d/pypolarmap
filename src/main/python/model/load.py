import logging
import os
import re
import struct
import time
from abc import ABC, abstractmethod

import numpy as np
from scipy.io import wavfile

from model.log import to_millis
from model.measurement import Measurement

logger = logging.getLogger('loader')


class RawDataLoader(ABC):
    '''
    Base type for loaders.
    '''

    @abstractmethod
    def load(self):
        pass

    def asMeasurement(self, fileName, **kwargs):
        '''
        Converts a file into a measurement object.
        :param fileName: the filename.
        :return: the measurement if there is one.
        '''
        name, _ = os.path.splitext(fileName)
        h = self._getAngle(fileName, 'H')
        v = self._getAngle(fileName, 'V')
        meas = None
        if h is not None:
            meas = Measurement(name, h=h)
        elif v is not None:
            meas = Measurement(name, v=v)
        else:
            pass  # ignore - filename format is invalid
        if meas is not None:
            logger.info(f"Loaded {meas}")
        return meas

    def _getAngle(self, fileName, angle):
        '''
        Extracts the specified angle from the filename, expects angle to be embedded in the form _<ANGLE><DEGREES>
        :param fileName:
        :param angle:
        :return:
        '''
        matches = re.match('.*_?(' + angle + '([0-9]+)).*', fileName)
        if matches:
            return int(matches.group(2))
        else:
            return None


class FileLoader(RawDataLoader):
    '''
    A loader that loads files from a single directory where each file conains nothing but raw data.
    '''

    def __init__(self, listener, dir, ext):
        self.dir = dir
        self.ext = ext
        self.listener = listener

    def load(self):
        '''
        :return: the loaded measurements (if any), default implementation loads each measurement from a separate file.
        '''
        results = []
        for fileName in os.listdir(self.dir):
            if fileName.endswith('.' + self.ext):
                m = self.asMeasurement(fileName)
                if m is None:
                    self.listener(fileName, False)
                else:
                    self.listener(fileName, True)
                    results.append(m)
            else:
                self.listener(fileName, False)
        return sorted(results, key=lambda m: (m._h, m._v))

    def asMeasurement(self, fileName, **kwargs):
        measurement = super().asMeasurement(fileName)
        if measurement is not None:
            fs, samples = self.loadFsAndSamples(fileName)
            measurement._fs = fs
            measurement.samples = samples
        return measurement

    @abstractmethod
    def loadFsAndSamples(self, fileName):
        pass


class ConstantFsLoader(FileLoader):
    def __init__(self, listener, dir, fs, ext):
        super().__init__(listener, dir, ext)
        self.__fs = fs

    def loadFsAndSamples(self, fileName):
        start = time.time()
        samples = self.loadSamples(fileName)
        end = time.time()
        logger.debug(f"Loaded {fileName} in {to_millis(start, end)}ms")
        return self.__fs, samples

    @abstractmethod
    def loadSamples(self, fileName):
        pass


class TxtLoader(ConstantFsLoader):
    '''
    handles a text file
    '''

    def __init__(self, listener, dir, fs):
        super().__init__(listener, dir, fs, 'txt')

    def loadSamples(self, fileName):
        return np.genfromtxt(os.path.join(self.dir, fileName), delimiter="\n")


class DblLoader(ConstantFsLoader):
    '''
    handles a binary file full of doubles
    '''

    def __init__(self, listener, dir, fs):
        super().__init__(listener, dir, fs, 'dbl')

    def loadSamples(self, fileName):
        return np.fromfile(os.path.join(self.dir, fileName), dtype=np.float64)


class WavLoader(FileLoader):
    '''
    A loader that loads wav files from a single directory.
    '''

    def __init__(self, listener, dir):
        super().__init__(listener, dir, 'wav')

    def loadFsAndSamples(self, fileName):
        '''
        Loads the data using scipy, assumes the file is a wav (not a pcm for example).
        :param fileName: the file name.
        :return: fs, data
        '''
        start = time.time()
        fs, samples = wavfile.read(os.path.join(self.dir, fileName))
        samples = np.require(samples, dtype=np.float64, requirements=['W', 'O'])
        end = time.time()
        logger.debug(f"Read {fileName} in {to_millis(start, end)}ms")
        return fs, samples


class HolmLoader(RawDataLoader):
    '''
    A loader that loads single holm impulse files. This involves parsing the header comments to extract the sample rate
    and measurement names and then loading the data from the file. The header in a HolmImpulse file looks like

        # Measurement exported using HOLM Acoustics software
        # http://www.holmacoustics.com
        #
        # First sample number in file: -400
        # Last sample number in file: 4000
        # Samplerate: 44100
        #
        ## sample;0 (00) ;1 (05) ;2 (10) ;3 (15) ;4 (20) ;5 (30) ;6 (40) ;7 (50) ;8 (60) ;9 (80) ;10 (100) ;11 (120) ;12 (150) ;13 (180)

    which means the measurement names are embedded in parentheses in the last header row.
    '''

    def __init__(self, listener, file):
        self.__file = file
        self.__listener = listener

    def load(self):
        '''
        :return: the loaded measurements (if any)
        '''
        # read the comments first to find the sample rate and check it really is a holm file
        fs = None
        names = None
        with open(self.__file) as fp:
            for line in fp:
                if line.startswith('#'):
                    if line.startswith('# Samplerate: '):
                        try:
                            fs = int(line.strip('\n')[14:])
                        except Exception as e:
                            self.__listener(self.__file, False)
                            raise ValueError(self.__file + ' has comments but no Samplerate') from e
                    elif line.startswith('## sample;'):
                        vals = line.strip('\n')[10:].split(';')
                        regex = r".*\((.*)\)"
                        src = re.search
                        names = [m.group(1) for val in vals for m in [src(regex, val)] if m and m.lastindex == 1]
                else:
                    break
        if fs and names:
            data = np.loadtxt(self.__file, delimiter=';', unpack=True)
            self.__listener(self.__file, True)
            return [self.asMeasurement(name, fs=fs, samples=data[idx + 1]) for idx, name in enumerate(names)]
        else:
            self.__listener(self.__file, False)
            raise ValueError(self.__file + ' is not a HolmImpulse export file, no Samplerate found')

    def asMeasurement(self, fileName, **kwargs):
        measurement = super().asMeasurement(fileName)
        if measurement is not None:
            measurement._fs = kwargs['fs']
            measurement.samples = kwargs['samples']
        return measurement


class REWLoader(FileLoader):
    '''
    A loader that loads impulses exported by REW in txt format.
    '''

    def __init__(self, listener, dir):
        super().__init__(listener, dir, 'txt')

    def loadFsAndSamples(self, fileName):
        '''
        Parses the header generated by REW to find fs and then loads the data
        :param fileName:
        :return:
        '''
        fs = None
        ignoreLines = 0
        fullPath = os.path.join(self.dir, fileName)
        with open(fullPath) as fp:
            for line in fp:
                line = line.strip('\n')
                if len(line) == 0:
                    break
                else:
                    ignoreLines += 1
                    idx = line.find(' // Sample interval (seconds)')
                    if idx != -1:
                        fs = int(1 / float(line[0:idx]))
        if fs is not None:
            start = time.time()
            samples = np.genfromtxt(fullPath, skip_header=ignoreLines + 1)
            end = time.time()
            logger.debug(f"Loaded {fileName} in {to_millis(start, end)}ms")
            return fs, samples
        return None


class ARTALoader(FileLoader):
    def __init__(self, listener, dir):
        super().__init__(listener, dir, 'pir')

    def loadFsAndSamples(self, fileName):
        '''
        PIR is a binary format as follows, we only really need samplerate, length and pir out of this

        char filesignature[4] // four signature characters: 'P','I','R','\0'
        unsigned int version; // version of file format starting from 0x0100
        int infosize; // length of user defined text at end of file
        int reserved1; // 0;
        int reserved2 // 0;
        float fskHz; // sampling frequency in kHz
        int samplerate; // sampling rate in Hz
        int length; // pir length
        int inputdevice; // 0 - voltprobe, 1-mic, 2-accelerometer
        float devicesens; // V/V or V/Pa ( for mic input)
        int measurement_type; // 0- signal recorded - external excitation
         // 1- IR - single channel correlation
         // 2- IR - dual channel correlation IR
        int avgtype; // type of averaging (0-time or 1-freq)
        int numavg; // number of averages used in measurements
        int bfiltered; // forced antialiasing filtering in 2ch
        int genused; // generator type
        float peakleft; // peak value (ref. 1.0) in left input channel
        float peakright; // peak value (ref. 1.0) in right input channel
        float reserved1; // 0
        float reserved2; // 0
        float reserved3; // 0
        float pir[length]; // pir data itself
        char infotext[infosize]; // user defined text
        :return:
        '''
        fullPath = os.path.join(self.dir, fileName)
        statinfo = os.stat(fullPath)
        size = statinfo.st_size
        if size > 68:
            start = time.time()
            with open(fullPath, "rb") as f:
                f.seek(24, 1)
                fs = struct.unpack('i', f.read(4))[0]
                n = struct.unpack('i', f.read(4))[0]
                f.seek(44, 1)
                data = np.array(struct.unpack('f' * n, f.read(4 * n)))
                end = time.time()
                logger.debug(f"Loaded {fileName} in {to_millis(start, end)}ms")
                return fs, data
        else:
            return None
