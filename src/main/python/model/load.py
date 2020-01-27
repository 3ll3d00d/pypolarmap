import logging

import numpy as np

from model.measurement import Measurement

logger = logging.getLogger('loader')


class NFSLoader:
    '''
    A loader that loads single Klippel Near Field Scanner directivity file.
    '''

    def __init__(self, file):
        self.__file = file

    def load(self):
        '''
        :return: the loaded measurements (if any)
        '''
        angles = []
        with open(self.__file) as fp:
            for line in fp:
                if line.startswith('On-Axis') or line.startswith('"On-Axis"'):
                    from re import sub
                    for txt in line.strip().split('\t'):
                        if 'On-Axis' in txt:
                            angles.append(0)
                        else:
                            txt = sub(r"[^0-9\-]", "", txt)
                            if txt:
                                angles.append(int(txt))
                    break
        if angles:
            data = np.loadtxt(self.__file, delimiter='\t', unpack=True, skiprows=3, dtype=np.str)
            data = np.char.replace(data, ',', '')
            data = np.char.replace(data, '"', '').astype(np.float64)
            measurements = [self.convert(data, angle, 0, idx) for idx, angle in enumerate(angles)]
            return self.mirrored(measurements) if min(angles) == 0 else measurements
        else:
            raise ValueError(self.__file + ' is not an NFS export file, no angles found')

    @staticmethod
    def mirrored(measurements):
        mirrored = [x.mirror() for x in measurements if x.h != 0]
        mirrored.reverse()
        return mirrored + measurements

    @staticmethod
    def convert(cols, h, v, idx):
        return Measurement('NFS', h=h, v=v, freq=cols[idx * 2], spl=cols[(idx * 2) + 1])
