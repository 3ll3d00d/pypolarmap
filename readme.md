## Setup

### Prerequisites

[Intel Fortran Redist for Parallel XE 2015 Compiler](https://software.intel.com/en-us/articles/redistributables-for-intel-parallel-studio-xe-2015-composer-edition-for-windows) provides libmmd.dll and libifcoremmd.ddl

### Testing Fortran 

install mingw fortran compiler 
add to path

to compile a test dll

    gfortran -shared -static -fPIC Test.f90 -o Test.dll

### Create venv

32bit python is required, with conda this means:

    set CONDA_SUBDIR=win-32
    conda create -n scanner32 numpy matplotlib colorcet qtawesome pyqt5
    activate scanner32
    conda info

## TODO 

* smoothing sends the modal screen crazy
* graph limits aren't updating properly in the multi chart
* reloading data causes the impulse chart to blow up    
* contour chart is not updating if  we  updated the chart y range while offscreen