#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 21:33:00 2022

@author: stuart
"""

import matplotlib.pyplot as plt

def fig(img):
    """
    fig:        display a figure given an image
    
    img:        image object
    
    returns:    NULL
    """
    plt.figure(figsize = (10,10))
    plt.imshow(img)
    plt.show()

