## Setup

### Prerequisites

* Intel Fortran Redist provides libmmd.dll and libifcoremmd.ddl
https://software.intel.com/en-us/articles/redistributables-for-intel-parallel-studio-xe-2015-composer-edition-for-windows

### Testing Fortran 

install mingw fortran compiler 
add to path

### Create venv

32bit python is required, with conda this means:

    set CONDA_SUBDIR=win-32
    conda create -n scanner32 numpy
    activate scanner32
    conda info
