# -*- coding: utf-8 -*-
"""
goreui

Created on Thu Apr  1 17:50:00 2021

@author: swm
"""

import gore
import ipywidgets as widgets
out = widgets.Output(layout={'border': '1px solid black'})

style = {'description_width': 'initial'}
w_focal_length = widgets.FloatSlider(
    value=24,
    min=5,
    max=50.0,
    step=0.5,
    description='Focal length:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='.1f',
)
display(w_focal_length)

w_alpha_max = widgets.IntSlider(
    min=5,
    max=100,
    value = 32,
    step=1,
    description='Fundus angle:',
    style = style)
display(w_alpha_max)

w_num_gores = widgets.IntSlider(
    min = 1,
    max = 24,
    value = 6,
    step = 1,
    description = 'Number of gores:',
    style=style)
display(w_num_gores)

w_alpha_limit = widgets.IntSlider(
    min = 10,
    max = 150,
    value = 100,
    step = 5,
    description = 'Retina angle')
display(w_alpha_limit)

w_phi_no_cut = widgets.IntSlider(
    min = 0,
    max = 90,
    value = 10,
    step = 5,
    description = "Angle of no-cut area",
    style=style)
display(w_phi_no_cut)

w_num_points = widgets.IntSlider(
    min = 100,
    max = 2000,
    value = 1000,
    step = 100,
    description = 'Resolution',
    style = style)
display(w_num_points)

w_projection = widgets.Dropdown(
    options=["sinusoidal", "cassini", "american polyconic", 
             "rectanguar polyconic", "transverse mercator"],
    value='cassini',
    description='Projection:',
    disabled=False,
)
display(w_projection)

btn_calculate = widgets.Button(
    description='Click to gore',
    disabled=False,
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Click me',
    icon='eye' # (FontAwesome names without the `fa-` prefix)
)
def on_calculate(b):
    out.clear_output()
    rotary = gore.make_rotary(im_path = './img/fundus_white.jpg', 
                 focal_length = w_focal_length.value, 
                 alpha_max = gore.deg2rad(w_alpha_max.value), 
                 num_gores = w_num_gores.value, 
                 projection = w_projection.value, 
                 alpha_limit = gore.deg2rad(w_alpha_limit.value), 
                 num_points = w_num_points.value,
                 phi_no_cut = gore.deg2rad(w_phi_no_cut.value))
    
    with out:
        gore.fig(rotary)
    rotary.save("rotary.png")
    
btn_calculate.on_click(on_calculate)
display(btn_calculate)
display(out)


