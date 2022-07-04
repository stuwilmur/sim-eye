#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 10:54:01 2022

@author: stuart
"""

import sys
from cx_Freeze import setup, Executable

sys.path.append("../gore")

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"includes": ["gore2"], "include_files": ["splash.png", "userguide.html"]}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Gore Sim Eye",
    version="0.1",
    description="Gore Sim Eye",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base=base)],
)