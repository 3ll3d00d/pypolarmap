# -*- mode: python -*-
import os
import platform
import distro

# work-around for https://github.com/pyinstaller/pyinstaller/issues/4064
import distutils

distutils_dir = getattr(distutils, 'distutils_path', None)
if distutils_dir is not None and distutils_dir.endswith('__init__.py'):
    distutils.distutils_path = os.path.dirname(distutils.distutils_path)


generic_linux_excludes = [
    'libstdc++.so.',
    'libtinfo.so.',
    'libreadline.so.',
    'libdrm.so.'
]
fedora_excludes = [
    'libgio-2.0.so.',
    'libglib-2.0.so.',
    'libfreetype.so.',
    'libssl.so.',
    'libfontconfig.so.'
]
debian_excludes = [
    'libfontconfig.so.'
]
ubuntu_excludes = [
    'libgpg-error.so.',
    'libgtk-3.so.*',
    'libgio-2.0.so.*'
]
linux_excludes = {
    'ubuntu': generic_linux_excludes + ubuntu_excludes,
    'linuxmint': generic_linux_excludes + ubuntu_excludes,
    'fedora': generic_linux_excludes + fedora_excludes,
    'centos': generic_linux_excludes + fedora_excludes,
    'debian': generic_linux_excludes + debian_excludes
}

# helper functions



def get_icon_file():
    '''
    :return: the full path to the icon file for the current platform.
    '''
    return f"src/main/icons/{'icon.icns' if platform.system() == 'Darwin' else 'Icon.ico'}"


def use_nsis():
    '''
    :return: true if pyinstaller is being run in order to create an installer.
    '''
    return platform.system() == 'Windows' and 'USE_NSIS' in os.environ


def get_exe_args():
    '''
    :return: the *args to pass to EXE, varies according to whether we are in "create an installer" mode or not.
    '''
    return (a.scripts,) if use_nsis() is True else (a.scripts, a.binaries, a.zipfiles, a.datas)


def get_data_args():
    '''
    :return: the data array for the analysis.
    '''
    return [
        ('src/main/icons/Icon.ico', '.'),
        ('src/main/python/style', 'style'),
        ('src/main/python/VERSION', '.'),
    ]


def should_keep_binary(x):
    '''
    :param x: the binary (from Analysis.binaries)
    :return: True if we should keep the given binary in the resulting output.
    '''
    if platform.system().lower().startswith('linux'):
        dist = distro.linux_distribution(full_distribution_name=False)[0]
        return not __is_exclude(x, linux_excludes.get(dist, generic_linux_excludes))
    return True


def __is_exclude(x, excludes):
    for exclude in excludes:
        if x[0].startswith(exclude):
            import sys
            print(f"EXCLUDING {x}", file=sys.stderr)
            return True
    return False


def remove_platform_specific_binaries(a):
    '''
    Removes elements from the analysis based on the current platform.
    Provides equivalent behaviour to https://github.com/mherrmann/fbs/tree/master/fbs/freeze
    :param a: the pyinstaller analysis.
    '''
    a.binaries = [x for x in a.binaries if should_keep_binary(x) is True]


def get_exe_name():
    '''
    Gets the executable name which is pypolarmap for osx & windows and has some dist specific suffix for linux.
    '''
    if platform.system().lower().startswith('linux'):
        linux_dist = distro.linux_distribution(full_distribution_name=False)
        return f"pypolarmap_{'_'.join((x for x in linux_dist if x is not None and len(x) > 0))}"
    return 'pypolarmap'


def get_binaries():
    '''
    :return: the ssl binaries if we're on windows and they exist.
    '''
    if platform.system() == 'Windows':
        import os
        ssl_dll = 'c:/Windows/System32/libssl-1_1-x64.dll'
        crypto_dll = 'c:/Windows/System32/libcrypto-1_1-x64.dll'
        if os.path.isfile(ssl_dll):
            if os.path.isfile(crypto_dll):
                return [
                    (ssl_dll, '.'),
                    (crypto_dll, '.'),
                ]
            else:
                print(f"MISSING libcrypto-1_1-x64.dll")
        else:
            print(f"MISSING libssl-1_1-x64.dll")
    return None


block_cipher = None
spec_root = os.path.abspath(SPECPATH)

a = Analysis(['src/main/python/app.py'],
             pathex=[spec_root],
             binaries=get_binaries(),
             datas=get_data_args(),
             hiddenimports=['numpy.random'],
             hookspath=['hooks/'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

remove_platform_specific_binaries(a)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          *get_exe_args(),
          name=get_exe_name(),
          debug=False,
          strip=False,
          upx=False,
          console=True,
          exclude_binaries=use_nsis(),
          icon=get_icon_file())

if platform.system() == 'Darwin':
    app = BUNDLE(exe,
                 name='pypolarmap.app',
                 bundle_identifier='com.3ll3d00d.pypolarmap',
                 icon='src/main/icons/icon.icns',
                 info_plist={
                     'NSHighResolutionCapable': 'True',
                     'LSBackgroundOnly': 'False',
                     'NSRequiresAquaSystemAppearance': 'False',
                     'LSEnvironment': {
                         'PATH': '/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:'
                     }
                 })

if use_nsis() is True:
    coll = COLLECT(exe,
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   strip=False,
                   upx=False,
                   name='pypolarmap')
