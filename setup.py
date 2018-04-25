from cx_Freeze import setup, Executable
import os.path

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

exe = Executable(
    script="hp4195a_reader.py",
    base="Win32GUI",
    icon="hp_icon.ico"
    )

options = {
    'build_exe': {
        'include_files':[
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
            os.path.join(os.path.dirname(__file__), 'logging.conf')
         ],
    },
}

setup(
    options = options,
    name = "hp4185a-reader",
    version = "0.1",
    description = "A basic program for connecting to and interfacing with a HP4195A Network/Spectrum Analyser.",
    executables = [exe]
    )
