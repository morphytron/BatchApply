import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "sys", "IOFile", "ArgumentMatcher", "BatchApply", "subprocess", "threading", "random", "re"], "optimize": 2, "excludes": ["tkinter, http"], "include_files": ["help.txt"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = "Console"
#if sys.platform == "win32":
#    base = "Win32GUI"

setup(  name = "BatchApply",
        author_email="atomhid@gmail.com",
        author = "Daniel Alexander Apatiga",
        version = "1.0.6",
        description = "BatchApply, a helpful script for recursively doing the same command over large numbers of files.",
        long_description = "This script is useful when you need to apply the same algorithm(s) on multiple files.",
        options = {"build_exe": build_exe_options},
        executables = [Executable(script="ba.py", copyright="2018", trademarks="Atomhid/Atomnia", base=base),
                       Executable(script='echofile.py', copyright='2018', trademarks='Atomhid/Atomnia', base=base)]
        )
