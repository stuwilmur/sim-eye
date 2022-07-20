#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 00:00:00 2022

@author: stuart
"""

import sys
import subprocess

# implement pip as a subprocess:
subprocess.check_output(['pip', 'install', '--upgrade', 'pip'])
subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

# process output with an API in the subprocess module:
reqs = subprocess.check_output([sys.executable, '-m', 'pip',
'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

print(installed_packages)