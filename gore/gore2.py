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

def make_equatorial(im, num_gores, projection = "sinusoidal", phi_min = -mt.pi / 2, 
         phi_max = mt.pi / 2, lam_min = -mt.pi, lam_max = mt.pi, phi_no_cut = 0, phi_cap = mt.pi / 2,
         alpha_limit = mt.pi, show_progress = True):
    """
    make_equatorial    returns an image that can be used as a gore net
    
    im:             input image opened by PIL
    num_gores:      number of gores
    projection:     "sinusoidal", "cassini", "american polyconic", 
                    "rectanguar polyconic", "transverse mercator"
    phi_min:        minimum latitude (radians)    
    phi_max:        maximum latitude (radians)
    lam_min:        minimum longitude (radians)    
    lam_max:        maximum longitude (radians)
    phi_no_cut:     angular size of no-cut zone (radians)
    phi_cap:        angular size of pole cap (radians)
    alpha_limit:    no goring beyond this angle
    show_progress:  show progress bar (boolean)
    """
    
    im2arr = np.array(im) # im2arr.shape: height x width x channel
    ht, wd, cols = im2arr.shape
    
    # The projection is done by iterating over source image pixels and 
    # using their values to set the pixel at its projected location: 
    # hence we use subsampling to ensure there are no "holes".
    if (projection == "sinusoidal"):
        sample_factor = 1.0
    else:
        sample_factor = 1.25
    
    ht2, wd2 = int(ht / sample_factor), int(wd / sample_factor)
    projected = np.zeros((ht2, wd2, cols + 1), dtype = "uint8")
    
    phi0 = 0
    
    ang_wd = lam_max - lam_min    
    rads_per_meridian = ang_wd / num_gores
    
    if (show_progress):
        tr = trange(0, ht, desc='goring image rows', leave=True)
    else:
        tr = range(0, ht)
    for i in tr:
        for j in range(0,wd):
            
            phi = phi_min + (phi_max - phi_min) * i / ht
            lam = lam_min + ang_wd * j / wd
            # calculate which meridian we are nearest
            n_meridian = (lam + 0.5 * ang_wd) // rads_per_meridian
            lam0 = lam_min + 0.5 * ang_wd / (num_gores) + (n_meridian) * ang_wd / (num_gores)

            if projection == "sinusoidal":
                x, y = lam0 + (lam - lam0) * mt.cos(phi), phi
            elif projection == "cassini":
                x, y = lam0 + mt.asin(mt.cos(phi) * mt.sin((lam - lam0))), mt.atan(mt.tan(phi) / mt.cos((lam - lam0)))
            elif projection == "american polyconic":
                if phi != 0:
                    x, y = lam0 + cot(phi) * mt.sin((lam - lam0) * mt.sin(phi)), phi - phi0 + cot(phi) * (1 - mt.cos((lam - lam0) * mt.sin(phi)))
                else: # handle phi = 0
                    x, y = lam - lam0, - phi0
            elif projection == "rectangular polyconic":
                if (phi != 0):
                    phi1 = mt.pi/2
                    A = mt.tan(0.5 * (lam - lam0) * mt.sin(phi1))*cosec(phi1)
                    E = 2 * mt.atan(A * mt.sin(phi))
                    x, y = lam0 + cot(phi) * mt.sin(E), phi - phi0 + (1 - mt.cos(E)) * cot(phi)
                else: # handle phi = 0
                    x, y = lam - lam0, -phi0
            elif projection == "transverse mercator":
                B = mt.cos(phi) * mt.sin(lam - lam0)
                scale = .5 / mt.atanh(mt.sin(rads_per_meridian / 2)) * rads_per_meridian
                scale = 1
                x = scale * mt.atanh(B) + lam0
                y = mt.atan2(mt.tan(phi), mt.cos(lam - lam0)) - phi0
            elif projection == "azimuthal equidistant":
                rho = mt.acos(mt.cos(phi) * mt.cos(lam))
                theta = mt.atan2(mt.cos(phi) * mt.sin(lam) , mt.sin(phi))
                scale = 2 / mt.pi
                scale = 1
                if (rho > phi_cap):
                    continue
                x = scale * rho * mt.sin(theta)
                y = scale * rho * mt.cos(theta)
            elif projection == "orthographic":
                if (abs(lam > mt.pi/2)):
                    continue
                scale = mt.pi / 2
                lam00 = 0
                x, y = scale * mt.cos(phi) * mt.sin(lam - lam00), scale * (mt.cos(phi0) * mt.sin(phi) - mt.sin(phi0) * mt.cos(phi) * mt.cos(lam - lam00))
            else:
                x, y =  lam, phi #equirectangular

            inew, jnew = (y - phi_min) / (phi_max - phi_min) * ht2,  (x - lam_min) / ang_wd * wd2 
            inew, jnew = round(inew), round(jnew)

            # do nothing if we have gone off the edge
            if jnew < 0 or jnew >= wd2 or inew < 0 or inew >= ht2:
                continue
                
            # do nothing if we have exceeded alpha_limit
            if phi > (alpha_limit - np.pi / 2):
                continue

            projected[inew][jnew][0:3], projected[inew][jnew][3] = im2arr[i][j][0:3], 255
            
    # now project the the no-cut zone
    for i in range(0,ht):
        for j in range(0,wd):

            phi = phi_min + (phi_max - phi_min) * i / ht
            lam = lam_min + ang_wd * j / wd

            if abs(phi) <= phi_no_cut:
                x, y = lam, mt.sin(phi) # Lambert cylindrical equal-area projection in the no-cut strip

                inew, jnew = (y - phi_min) / (phi_max - phi_min) * ht2,  (x - lam_min) / ang_wd * wd2
                inew, jnew = round(inew), round(jnew)

                # do nothing if we have gone off the edge
                if jnew < 0 or jnew >= wd2 or inew < 0 or inew >= ht2:
                    continue

                projected[inew][jnew][0:3], projected[inew][jnew][3] = im2arr[i][j][0:3], 255

    equator_stitched = Image.fromarray(projected, mode="RGBA")
    
    # since we subsampled, resize to match the input image size
    equator_stitched = equator_stitched.resize(im.size, Image.CUBIC)
    
    return equator_stitched

def make_polar(im, num_gores, projection = "sinusoidal", phi_min = -mt.pi / 2, 
         phi_max = mt.pi / 2, lam_min = -mt.pi, lam_max = mt.pi, alpha_limit = mt.pi,
         show_progress = True):
    
    # demand that the pole is included if the gores are to be stitched at the pole
    phi_min = -mt.pi / 2
    
    im2arr = np.array(im) # im2arr.shape: height x width x channel
    ht, wd = im2arr.shape[0:2]
    
    ang_wd = lam_max - lam_min    
    rads_per_meridian = ang_wd / num_gores
    degs_per_meridian = rads_per_meridian / mt.pi * 180
    
    gore_wd = wd // num_gores
    pole_stitched = Image.new(mode = "RGBA", size = (2 * ht, 2 * ht))
    
    equator_stitched = make_equatorial(im = im, num_gores = num_gores, projection = projection,
                                       phi_min = phi_min, phi_max = phi_max, lam_min = lam_min,
                                       lam_max = lam_max, phi_no_cut = 0, alpha_limit = alpha_limit,
                                       show_progress = show_progress)
    
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
    
def swap(im, phi_extent = mt.pi / 2, lam_extent = mt.pi, show_progress = True):
    """
    swap    takes an equirectangular projection of a certain angular
            extent and rotates it about the y-axis, so the poles lie 
            at the equator and the equator becomes a meridian.
    """
    im2arr = np.array(im) # im2arr.shape: height x width x channel
    ht, wd, cols = im2arr.shape
    wdo = ht * 2
    
    phii_max, phii_min = phi_extent, -phi_extent
    phio_max, phio_min  = mt.pi / 2, -mt.pi / 2
    lami_min, lami_max = -lam_extent , lam_extent
    lamo_min, lamo_max = -mt.pi, mt.pi
    sinus = np.zeros((ht, wdo, cols), dtype = "uint8")
    

    if (show_progress):
        tr = trange(0, ht, desc='rotating image rows to pole', leave=True)
    else:
        tr = range(0, ht)
    for i in tr:
        for j in range(0,wdo):
    
            phi, lam, = phio_min + (phio_max - phio_min) * i / ht, lamo_min + (lamo_max - lamo_min) * j / wdo
            x, y = mt.atan2(mt.sin(lam) * mt.cos(phi), mt.sin(phi)), mt.asin(-mt.cos(lam) * mt.cos(phi))
    
            isamp, jsamp = (y - phii_min) / (phii_max - phii_min) * ht,  (x - lami_min) / (lami_max - lami_min) * wd 
            isamp, jsamp = round(isamp), round(jsamp)
    
            if jsamp < 0 or jsamp >= wd or isamp < 0 or isamp >= ht:
                continue
    
            sinus[ht - i - 1][j][:] = im2arr[isamp][jsamp][:]
    
    output = Image.fromarray(sinus)
    return output

def equi(im, alpha_max, focal_length = 24, numpoints = 1000, show_progress = True):
    """
    equi         takes a fundus image and computes its equirectangular projection
                 assuming a simple spherical eye model

    im           input image (image)
            
    alpha_max    angular size of the image from the centre (radians)
            
    focal length default assumes a focal length of one eye diameter (mm)
    
    numpoints    number of angles to sample (number)
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
    
def equi_zeiss(im, alpha_max, focal_length = 24, numpoints = 1000):
    """
    equi_zeiss   takes a zeiss composite of two fundus images and computes its 
                 equirectangular projection assuming a simple spherical eye model

    im:          input image (image)
            
    alpha_max    angular size, in the vertical plane, of the image from the centre
                 (radians)
            
    focal length default assumes a focal length of one eye diameter (mm)
    
    numpoints    number of angles to sample (number)
    """

    wd, ht = im.size
    im_l = im.crop((0,0,ht, ht))
    equi_l, _lm, _pm = equi(im_l, alpha_max, focal_length, numpoints)
    im_r = im.crop((wd - ht + 1, 0, wd, ht))
    equi_r, _lm, _pm = equi(im_r, alpha_max, focal_length, numpoints)
    
    d = focal_length
    r = 12
    
    # convert the pole to image centre distance to an angle
    Lp_max = d * r * np.sin(alpha_max) / (d + r * (np.cos(alpha_max) - 1))
    Lp = (wd / 2 - ht / 2) / (ht / 2) * Lp_max
    beta = np.arctan2(Lp , d)
    alpha_centre = beta + np.arcsin((d/r - 1) * np.sin(beta))
    
    px_per_rad = numpoints / 2 / alpha_max
    half_angle = alpha_max + alpha_centre
    new_wd = int(half_angle * px_per_rad)
    
    equi_l = equi_l.crop((0, 0, new_wd, numpoints))
    equi_r = equi_r.crop((numpoints - new_wd, 0, numpoints, numpoints))
    
    equi_lr = Image.new("RGB", (new_wd * 2, numpoints))
    equi_lr.paste(equi_l,(0,0))
    equi_lr.paste(equi_r,(new_wd,0))
    
    return (equi_lr, float(half_angle), float(alpha_max))

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
                          focal_length = focal_length, alpha_max = alpha_max, numpoints = num_points, show_progress = show_progress)
    fundus_swapped = swap(fundus_equi, phi_extent = phimax, lam_extent = lammax, show_progress = show_progress)
    fundus_rotary = make_polar(fundus_swapped, num_gores = num_gores, 
                          projection = projection, alpha_limit = alpha_limit, show_progress = show_progress)
    fundus_cap = polecap(fundus_swapped, num_gores = num_gores, phi_cap = phi_no_cut, show_progress = show_progress)
    fundus_rotary.paste(fundus_cap, (0, round(num_points / 2)), fundus_cap)
    return fundus_rotary