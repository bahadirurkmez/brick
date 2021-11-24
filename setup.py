import sys, os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only

options = {
    "build_exe": {
        "packages": ["os", "sys", "random", "pickle", "time", "enum", "pygame"],
        "excludes":["tkinter"],
        "include_files": ["resources"]
    }

}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "Alara's Brick Game",
    version = "0.1.2",
    description = "A bit modified brick game",
    options = options,
    executables = [Executable("brick_v3.py", base=base, targetName="Brick")]
)

