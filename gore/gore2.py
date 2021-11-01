# -*- coding: utf-8 -*-
"""
gore

Created on Thu Dec  6 12:31:21 2018

@author: swm
"""
from PIL import Image
import numpy as np
import math as mt
from tqdm.notebook import trange
import matplotlib.pyplot as plt
import cv2

cot = lambda z : 1 / mt.tan(z)
cosec = lambda z : 1 / mt.sin(z)
sec = lambda z : 1 / mt.cos(z)

def fig(img):
    """
    fig:    display a figure given an image
    
    img:    image object
    """
    plt.figure(figsize = (10,10))
    plt.imshow(img)
    plt.show()

def openimage(f):
    """
    openimage    returns an image given a file path
    """
    return Image.open(f).convert('RGB')

def deg2rad(x):
    """
    deg2rad:    return an angle give in degrees in radians

    x:          angle in degrees
    """
    return x / 180 * np.pi

def rad2deg(x):
    """
    rad2deg:    return an angle give in radians in degrees

    x:          angle in radians
    """
    return x / np.pi * 180

def make_equatorial(im, num_gores, phi_min = -mt.pi / 2, 
         phi_max = mt.pi / 2, lam_min = -mt.pi, lam_max = mt.pi):
    """
    make_equatorial    returns an image that can be used as a gore net
    
    im:             input image opened by PIL
    num_gores:      number of gores
    phi_min:        minimum latitude (radians)    
    phi_max:        maximum latitude (radians)
    lam_min:        minimum longitude (radians)    
    lam_max:        maximum longitude (radians)
    phi_no_cut:     angular size of no-cut zone (radians)
    phi_cap:        angular size of pole cap (radians)
    alpha_limit:    no goring beyond this angle
    show_progress:  show progress bar (boolean)
    """
    
    h, w = im.shape[:2]
    phi_vector, lam_vector = np.linspace(phi_min, phi_max, h, dtype = np.float32), np.linspace(lam_min, lam_max, w, dtype = np.float32)
    lam_dst, phi_dst = np.meshgrid(lam_vector, phi_vector)
    indx = np.arange(w, dtype = np.float32)
    gore_width = (lam_max - lam_min) / num_gores
    lam00 = (indx // (w / num_gores)) * gore_width + gore_width / 2 + lam_min
    lam0 = np.tile(lam00, (h,1))
    lam_src = ((lam_dst - lam0) / np.cos(phi_dst)) + lam0
    lam_src = lam_src + np.array(np.greater(lam_src, lam0 + gore_width / 2) * 1000, dtype = np.float32)
    lam_src = lam_src + np.array(np.less(lam_src, lam0 - gore_width / 2) * -1000, dtype = np.float32)
    phi_src = phi_dst
    y_src = (phi_src - phi_min) * h / (phi_max - phi_min)
    x_src = (lam_src - lam_min) * w / (lam_max - lam_min)
    dst = cv2.remap(im, x_src, y_src, cv2.INTER_LINEAR)
    return(dst)
    

def make_polar(im, num_gores, phi_min = -mt.pi / 2, 
         phi_max = mt.pi / 2, lam_min = -mt.pi, lam_max = mt.pi):
    
    # demand that the pole is included if the gores are to be stitched at the pole
    phi_min = -mt.pi / 2
    
    ht, wd = im.shape[0:2]
    
    ang_wd = lam_max - lam_min    
    rads_per_meridian = ang_wd / num_gores
    degs_per_meridian = rad2deg(rads_per_meridian)
    
    gore_wd = wd // num_gores
    pole_stitched = Image.new(mode = "RGBA", size = (2 * ht, 2 * ht))
    
    equator_stitched = make_equatorial(im = im, num_gores = num_gores,
                                       phi_min = phi_min, phi_max = phi_max, lam_min = lam_min,
                                       lam_max = lam_max)
    
    for i in range(num_gores):
        strip = equator_stitched.crop((i * gore_wd, 0, (i+1) * gore_wd, ht))
        ht3 = int(ht * 1.5)
        gore = Image.new(mode = "RGBA", size = (ht3, ht3))
        left = (ht3 - gore_wd) // 2
        gore.paste(strip, box=(left, 0))
        gore = gore.rotate((i) * degs_per_meridian)
        ht2 = ht3 // 2
        omega = (i) * rads_per_meridian
        pos_x, pos_y = ht2 * (1 + mt.sin(omega)) - (ht3 - ht), ht2 * (1 + mt.cos(omega)) - (ht3 - ht)
        pos_x, pos_y = int(pos_x), int(pos_y)
        
        # using the gore as a mask means that the pasted bakground is transparent
        pole_stitched.paste(gore, (pos_x, pos_y), mask=gore)
        
    return pole_stitched
    
def swap(im, phi_extent = mt.pi / 2, lam_extent = mt.pi):
    """
    swap    takes an equirectangular projection of a certain angular
            extent and rotates it about the y-axis, so the poles lie 
            at the equator and the equator becomes a meridian.
    """
    h, w = im.shape[:2]
    phi_dst_min, phi_dst_max, lam_dst_min, lam_dst_max = -np.pi / 2, np.pi / 2, -np.pi, np.pi
    phi_src_min, phi_src_max, lam_src_min, lam_src_max = -phi_extent, phi_extent, -lam_extent, lam_extent
    phi_vector, lam_vector = np.linspace(phi_dst_min, phi_dst_max, h, dtype = np.float32), np.linspace(lam_dst_min, lam_dst_max, w, dtype = np.float32)
    lam_dst, phi_dst = np.meshgrid(lam_vector, phi_vector)
    lam_src = np.arcsin(np.cos(lam_dst) * np.cos(phi_dst))
    phi_src = np.arctan2(np.sin(lam_dst) * np.cos(phi_dst),-np.sin(phi_dst))
    y_src = (phi_src - phi_src_min) * h / (phi_src_max - phi_src_min)
    x_src = (lam_src - lam_src_min) * w / (lam_src_max - lam_src_min)
    dst = cv2.remap(im, x_src, y_src, cv2.INTER_LINEAR)
    return dst

def equi(im, alpha_max, focal_length = 24):
    """
    equi         takes a fundus image and computes its equirectangular projection
                 assuming a simple spherical eye model

    im           input image (image)
            
    alpha_max    angular size of the image from the centre (radians)
            
    focal length default assumes a focal length of one eye diameter (mm)
    
    """
    
    ht,wd = im.shape[0:2]
    
    d = focal_length
    r = 12
    
    # subtract a small amount (1 degree) to avoid going off the edge
    alpha_max -= deg2rad(1.0)
    phi_max = lam_max = float(alpha_max)
    phi_min, lam_min = -phi_max, -lam_max
    Lp_max = d * r * np.sin(phi_max) / (d + r * (np.cos(phi_max) - 1))
    
    phis = np.linspace(phi_min, phi_max, ht, dtype = np.float32)
    lams = np.linspace(lam_min, lam_max, wd, dtype = np.float32)
    
    phi, lam = np.meshgrid(phis, lams)

    Lp_x = d * r * np.sin(phi) / (d + r * (np.cos(phi) - 1))
    Lp_y = d * r * np.sin(lam) / (d + r * (np.cos(lam) - 1))
    
    x = np.floor(Lp_x / Lp_max * ht / 2 + ht / 2)
    y = np.floor(Lp_y / Lp_max * wd / 2 + wd / 2)
            
    equi_image = cv2.remap(im, x, y, cv2.INTER_LINEAR) 
            
    return (equi_image, float(lam_max), float(phi_max))

def polecap(im, num_gores, lam_extent = mt.pi, phi_extent = mt.pi / 2, phi_cap = mt.pi / 2, show_progress = True):
    """
    polecap    produce a polar cap to paste onto a set of gores
               joined at the pole, to allow for a "no-cut" zone.
    """
    swapped = swap(im = im, lam_extent = lam_extent, phi_extent = phi_extent, show_progress = show_progress)
    output = make_equatorial(swapped, num_gores = 1, phi_cap = phi_cap, projection = "azimuthal equidistant", show_progress = show_progress)
    output = output.transpose(Image.FLIP_TOP_BOTTOM)
    output = output.rotate(180 - 180 / num_gores)
    return output

def make_rotary(im_path, focal_length, alpha_max, num_gores, projection, alpha_limit, num_points, phi_no_cut, show_progress):
    """
    make_rotary master function to produce a gore net stitched at the pole
    """
    im = openimage(im_path)
    fundus_equi, lammax, phimax = equi(im = im, 
                          focal_length = focal_length, alpha_max = alpha_max)
    fundus_swapped = swap(fundus_equi, phi_extent = phimax, lam_extent = lammax)
    fundus_rotary = make_polar(fundus_swapped, num_gores = num_gores, 
                          projection = projection, alpha_limit = alpha_limit, show_progress = show_progress)
    fundus_cap = polecap(fundus_swapped, num_gores = num_gores, phi_cap = phi_no_cut, show_progress = show_progress)
    fundus_rotary.paste(fundus_cap, (0, round(num_points / 2)), fundus_cap)
    return fundus_rotary