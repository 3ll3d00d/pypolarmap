import matplotlib
from setuptools import setup

includes = ["sip",
            "PyQt5",
            "PyQt5.QtCore",
            "PyQt5.QtGui",
            "numpy",
            "matplotlib.backends.backend_qt5agg",
            "scipy",
            "scipy.sparse.csgraph._validation",
            "scipy.special._ufuncs_cxx",
            "pandas"]

datafiles = [("", [r"c:\windows\syswow64\MSVCP100.dll",
                   r"c:\windows\syswow64\MSVCR100.dll",
                   r"C:\Users\mattk\github\pypolarmap\dlls\gl\libifcoremdd.dll",
                   r"C:\Users\mattk\github\pypolarmap\dlls\gl\libmmd.dll",
                   r"C:\Users\mattk\github\pypolarmap\dlls\gl\MeasCalcs.dll"])] + \
            matplotlib.get_py2exe_datafiles()

setup(
    name='pypolarmap',
    version='0.1.0',
    packages=['meascalcs', 'model', 'ui'],
    package_dir={'': 'src/python'},
    url='',
    license='',
    windows=[{"script": "app.py"}],
    scripts=['src/python/app.py'],
    data_files=datafiles,
    install_requires=['numpy>=1.14.3',
                      'matplotlib>=2.2.2',
                      'scipy>=1.1.0',
                      'pyqt>=5.9.2', 'qtpy'],
    options={
        "py2exe": {
            "includes": includes,
        }
    }
)
