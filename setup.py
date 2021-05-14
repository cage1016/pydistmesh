#!/usr/bin/env python

#-----------------------------------------------------------------------------
#  Copyright (C) 2012 Bradley Froehle

#  Distributed under the terms of the GNU General Public License. You should
#  have received a copy of the license along with this program. If not,
#  see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import os
from distutils import log

try:
    from numpy.distutils.core import setup
    from distutils.extension import Extension
except ImportError:
    raise RuntimeError('Numpy Needs to be installed for extensions')


WANT_LAPACK_LINKING = False

# from MDAnalysis setup.py (http://www.mdanalysis.org/)
def get_numpy_include():
    try:
        # Obtain the numpy include directory. This logic works across numpy
        # versions.
        # setuptools forgets to unset numpy's setup flag and we get a crippled
        # version of it unless we do it ourselves.
        try:
            import __builtin__  # py2
            __builtin__.__NUMPY_SETUP__ = False
        except:
            import builtins  # py3
            builtins.__NUMPY_SETUP__ = False
        import numpy as np
        from numpy.distutils import system_info
    except ImportError as e:
        print(e)
        print('*** package "numpy" not found ***')
        print('pymolfile requires a version of NumPy, even for setup.')
        print('Please get it from http://numpy.scipy.org/ or install it through '
              'your package manager.')
        sys.exit(-1)
    try:
        numpy_include = np.get_include()
    except AttributeError:
        numpy_include = np.get_numpy_include()
    return numpy_include


# from SimpleTraj setup.py (https://github.com/arose/simpletraj)
if __name__ == '__main__':
    # Read version from distmesh/__init__.py
    with open(os.path.join('distmesh', '__init__.py')) as f:
        line = f.readline()
        while not line.startswith('__version__'):
            line = f.readline()
    exec(line, globals())


    # Build list of cython extensions
    ext_modules = [
        Extension(
            'distmesh._distance_functions',
            sources=[os.path.join('distmesh', '_distance_functions.c')],
            depends=[os.path.join('distmesh', 'src', 'distance_functions.c')],
            include_dirs=[get_numpy_include()],
        ),
    ]

    # distmesh._distance_functions needs LAPACK
    # See ('https://github.com/nipy/nipy/blob/91fddffbae25a5ca3a5b35db2a7c605b8db9014d/nipy/labs/setup.py#L44')
    lapack_info = system_info.get_info('lapack_opt', 0)
    if 'libraries' not in lapack_info:
        lapack_info = system_info.get_info('lapack', 0)

    if not lapack_info:
        log.info('Building Lapack lite distribution')
        # sources.append(os.path.join(LIBS,'lapack_lite','*.c'))
        library_dirs = []
        libraries = []

    else:
        log.info('Linking with system Lapack')
        library_dirs = lapack_info['library_dirs']
        libraries = lapack_info['libraries']
        if 'include_dirs' in lapack_info:
            ext_modules[0].include_dirs.extend(lapack_info['include_dirs'])

    ext_modules[0].libraries.extend(libraries)
    ext_modules[0].library_dirs.extend(library_dirs)


    install_requires = []

    try:
        import matplotlib
    except ImportError:
        install_requires.append('matplotlib>=1.2')

    try:
        import numpy
    except ImportError:
        install_requires.append('numpy')

    long_description = open('README.rst').read()

    setup(name='PyDistMesh',
        version=__version__,
        description="A Simple Mesh Generator in Python",
        long_description=long_description,
        classifiers=[
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.2',
            'Operating System :: POSIX :: Linux',
            'Topic :: Scientific/Engineering :: Mathematics',
        ],
        keywords='meshing',
        author='Bradley Froehle',
        author_email='brad.froehle@gmail.com',
        url='https://github.com/bfroehle/pydistmesh',
        install_requires=install_requires,
        license='GPL',
        packages=['distmesh'],
        ext_modules=ext_modules,
    )    