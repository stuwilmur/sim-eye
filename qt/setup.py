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
build_exe_options = {
    "includes": ["gore2"], 
    "include_files": ["splash.png", "icon.icns", "userguide.html"], 
    "excludes": ["tkinter"], 
    "include_msvcr": True,
    }
    
bdist_mac_options = {"iconfile": "icon.icns"}

bdist_dmg_options = {"applications_shortcut": True}
    
directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|My Program"),
]

msi_data = {
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", None, None, "This is a description", "IconId", None),
    ],
    "Icon": [
        ("IconId", "icon.ico"),
    ],
}

bdist_msi_options = {
    "add_to_path": True,
    'skip_build': True,
    "data": msi_data,
    "environment_variables": [
        ("E_MYAPP_VAR", "=-*MYAPP_VAR", "1", "TARGETDIR")
    ],
    "upgrade_code": "{0a7d8a84-077b-4c8d-b9f2-0844899732a9}",
}

# base="Win32GUI" should be used only for Windows GUI app
base = None
icon = "icon.icns"
if sys.platform == "win32":
    base = "Win32GUI"
    icon = "icon.ico" 

executable = Executable(
                "app.py", 
                copyright="Copyright (C) 2022", 
                icon=icon, 
                base=base,
                shortcut_name="Gore Sim Eye",
                shortcut_dir="ProgramMenuFolder",)

setup(
    name="Gore Sim Eye",
    version="0.1",
    description="Gore Sim Eye",
    executables=[executable],
    options={
        "build_exe": build_exe_options, 
        "bdist_mac": bdist_mac_options,
        "bdist_dmg": bdist_dmg_options,
        "bdist_msi": bdist_msi_options,
        },
)