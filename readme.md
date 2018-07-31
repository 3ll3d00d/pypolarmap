## Setup

### Prerequisites

[Intel Fortran Redist for Parallel XE 2015 Compiler](https://software.intel.com/en-us/articles/redistributables-for-intel-parallel-studio-xe-2015-composer-edition-for-windows) provides libmmd.dll and libifcoremmd.ddl

### Testing Fortran 

install mingw fortran compiler 
add to path

to compile a test dll

    gfortran -shared -static -fPIC Test.f90 -o Test.dll

### Create venv

32bit python is required so use a 32bit installation of anaconda

    conda create -n scanner32 numpy colorcet qtawesome scipy qtpy mkl==2018.0.2
    pip install pyqt5 matplotlib
    activate scanner32
    python -m pip install --upgrade pip
    pip install https://github.com/pyinstaller/pyinstaller/tarball/develop

Note 

* the specific mkl version is required atm because of https://github.com/spyder-ide/spyder/issues/7357
* we use the development build of pyinstaller because we need some fixes in the 3.4 release (e.g. https://github.com/pyinstaller/pyinstaller/issues/2526)
* we use pip to install pyqt5 because the conda pyqt is borked as per https://github.com/pyinstaller/pyinstaller/issues/3479

## TODO 

* multi chart still not redrawing properly as the dB range changes
