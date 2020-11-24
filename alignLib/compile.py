#!/usr/bin/env python

import os
import sys
import platform


def compile(includePath=None, libPath=None):
    # search and set the relevant env variables
    # for the include files
    to_find_headers = {}
    to_find_headers["Python.h"] = ""  # python
    to_find_headers["arrayobject.h"] = ""  # numpy
    to_find_headers["fftw3.h"] = ""  # FFTW3

    # for the lib files
    # determine the platform
    if platform.system() == "Linux":
        lib_suffix = '.so'
    elif platform.system() == 'Darwin':
        lib_suffix = '.dylib'
    else:
        raise RuntimeError("Platform not supported!")

    to_find_libs = {}
    to_find_libs["libfftw3" + lib_suffix] = ""
    py_version = str(sys.version_info[0]) + '.' + str(sys.version_info[1])
    to_find_libs["libpython" + py_version + lib_suffix] = ""

    # get the HOME directory and try to deduce the Numpy position
    scpionHome = os.environ.get('SCIPION_HOME')
    homeDir = '' if scpionHome is None else os.path.join(scpionHome, 'software')
    try:
        import numpy
        numpySearchPath = os.path.dirname(
            numpy.__file__) + "/core/include/numpy/"
    except:
        print("No numpy found. Please install numpy.")

    # append some common dirs in the end to search
    print("Search include files ...")
    if includePath is None:
        includePath = []
    includePath += ["/usr/include/", homeDir + "/include/", numpySearchPath]
    for path in includePath:
        for header_file in to_find_headers:
            if to_find_headers[header_file] == "":
                dir = find_file(header_file, path)
                print('Dir: ', dir, header_file, path)
                if dir:
                    to_find_headers[header_file] = dir
        all_found = True
        for value in to_find_headers.values():
            if value == "":
                all_found = False
        if all_found:
            break
    else:
        for file in to_find_headers:
            if to_find_headers[file] == "":
                raise RuntimeError("File %s cannot be found!" % file)

    # get the parent directory for numpy header file
    if to_find_headers["arrayobject.h"][-5:] == "numpy":
        to_find_headers["arrayobject.h"] = to_find_headers["arrayobject.h"][:-5]
    elif to_find_headers["arrayobject.h"][-6:] == "numpy/":
        to_find_headers["arrayobject.h"] = to_find_headers["arrayobject.h"][:-6]
    else:
        raise RuntimeError(
            "Numpy header file arrayobject.h is in the wrong place!")

    # append some common dirs in the end to search
    print("Search dynamic library files ...")
    if libPath is None:
        libPath = []
    libPath += ["/usr/lib/", "/usr/lib64/",
                homeDir + "/lib/", homeDir + "/lib64/"]
    for path in libPath:
        for lib_file in to_find_libs:
            if to_find_libs[lib_file] == "":
                dir = find_file(lib_file, path)
                if dir:
                    to_find_libs[lib_file] = dir
        all_found = True
        for value in to_find_libs.values():
            if value == "":
                all_found = False
        if all_found:
            break
    else:
        for file in to_find_libs:
            if to_find_libs[file] == "":
                raise RuntimeError("File %s cannot be found!" % file)

    # start compilation
    print("Compile ......")
    environ = os.environ
    environ.update({
        'PYTHON_INCLUDE_PATH': to_find_headers["Python.h"],
        'NUMPY_INCLUDE_PATH': to_find_headers["arrayobject.h"],
        'FFTW_INCLUDE_PATH': to_find_headers["fftw3.h"],
        'FFTW_LIB_PATH': to_find_libs["libfftw3" + lib_suffix],
        'PYTHON_LIB_PATH': to_find_libs["libpython" + py_version + lib_suffix],
        'PYTHON_VERSION': 'python' + py_version,
    })

    try:
        # compile
        os.system("cd alignLib/SpharmonicKit27 && make all")
        os.system("cd alignLib/frm/src/ && make lib")
        os.system("cd alignLib/frm/swig/ && ./mkswig.sh")

        # check if the library is successfully compiled
        if not os.path.isfile('alignLib/frm/swig/_swig_frm.so'):
            raise Exception('Failed! Please check the compilation flags!')

        # # done, get the paths for setting up
        # current_path = os.getcwd()
        # parent_path = os.path.split(current_path)[0]
        # ld_library_path = to_find_libs[
        #                       "libfftw3" + lib_suffix] + ':' + current_path + '/SpharmonicKit27/' + ':' + current_path + '/frm/swig/'
        # python_path = parent_path + ':' + current_path + '/frm/swig/'
        # print
        print("Successfully finished!")
        # print "In order to use this library, you might need to add the following settings into your enviroment:"
        # print "LD_LIBRARY_PATH/DYLD_LIBRARY_PATH =", ld_library_path
        # print "PYTHONPATH =", python_path
        # print
        # return ld_library_path, python_path
    except:
        print("Failed!")
        return None, None


def find_file(filename, dir):
    for dirpath, dirnames, filenames in os.walk(dir):
        if filename in filenames:
            return dirpath
    else:
        return None


if __name__ == '__main__':
    # parse command line options
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", metavar="dirs",
                      help="add the dirs into the include search path, "
                           "multiple dirs please seperate by ','")
    parser.add_option("-l", metavar="dirs",
                      help="add the dirs into the library search path, "
                           "multiple dirs please seperate by ','")
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("incorrect number of arguments")

    include_path = None
    library_path = None
    if options.i:
        include_path = options.i.split(',')
    if options.l:
        library_path = options.l.split(',')

    # compile
    compile(include_path, library_path)
