# -*- coding: utf-8 -*-
"""
goreui

Created on Thu Apr  1 17:50:00 2021

@author: swm
"""

import gore2
import ipywidgets as widgets
from os import listdir
from os.path import isfile, join
from IPython.display import display, FileLink
import asyncio

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback

    async def _job(self):
        await asyncio.sleep(self._timeout)
        self._callback()

    def start(self):
        self._task = asyncio.ensure_future(self._job())

    def cancel(self):
        self._task.cancel()

def debounce(wait):
    """ Decorator that will postpone a function's
        execution until after `wait` seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        timer = None
        def debounced(*args, **kwargs):
            nonlocal timer
            def call_it():
                fn(*args, **kwargs)
            if timer is not None:
                timer.cancel()
            timer = Timer(wait, call_it)
            timer.start()
        return debounced
    return decorator

out = widgets.Output(layout={'border': '1px solid black'})

mypath = "./img"
imgfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

style = {'description_width': 'initial'}
layout = widgets.Layout(width='500px', height='40px') #set width and height

w_source_img = widgets.Dropdown(
    options=imgfiles,
    description='Source image:',
    disabled=False,
)
display(w_source_img)

w_focal_length = widgets.FloatSlider(
    value=24,
    min=5,
    max=50.0,
    step=0.5,
    description='Focal length:',
    disabled=False,
    continuous_update=True,
    orientation='horizontal',
    readout=True,
    readout_format='.1f',
    style = style,
    layout = layout,
)
display(w_focal_length)

w_alpha_max = widgets.IntSlider(
    min=5,
    max=100,
    value = 32,
    step=1,
    description='Fundus image size (degrees):',
    style = style,
    layout = layout)
display(w_alpha_max)

w_num_gores = widgets.IntSlider(
    min = 1,
    max = 24,
    value = 6,
    step = 1,
    description = 'Number of gores',
    style=style,
    layout = layout)
display(w_num_gores)

w_alpha_limit = widgets.IntSlider(
    min = 10,
    max = 150,
    value = 100,
    step = 5,
    description = 'Retinal size (degrees)',
    style = style,
    layout = layout)
display(w_alpha_limit)

w_phi_no_cut = widgets.IntSlider(
    min = 0,
    max = 90,
    value = 10,
    step = 1,
    description = "No-cut area (degrees)",
    style=style,
    layout = layout)
display(w_phi_no_cut)

w_angle = widgets.IntSlider(
    min = 0,
    max = 360,
    value = 0,
    step = 1,
    description = "Rotation (degrees)",
    style=style,
    layout = layout)
display(w_angle)

w_quality = widgets.IntSlider(
    min = 10,
    max = 100,
    value = 20,
    step = 5,
    description = "Quality (%)",
    style=style,
    layout = layout)
display(w_quality)

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

def get_inputs():
    im_path = join(mypath, w_source_img.value)
    im = gore2.image_from_path(im_path)
    im = gore2.deres_image(im, float(w_quality.value / 100))
    if (w_angle.value > 0):
        im = gore2.rotate_image(im, w_angle.value)
    inputs = dict(
    im = im, 
    focal_length = w_focal_length.value, 
    alpha_max = gore2.deg2rad(w_alpha_max.value), 
    num_gores = w_num_gores.value, 
    projection = w_projection.value,
    phi_no_cut = gore2.deg2rad(w_phi_no_cut.value),
    )

    return inputs;

@out.capture(clear_output = True)
def calculate(gore_args, allow_save=False):
    rotary = gore2.make_rotary(**gore_args)
    gore2.fig(rotary)

    if (allow_save):
        rotary.save("output.png")
        local_file = FileLink('./output.png', result_html_prefix="Click here to download: ")
        display(local_file)

def on_calculate(b):
    calculate(get_inputs(), allow_save = True)

@debounce(1)
def on_edit_parameters(change):
    inputs = get_inputs()
    calculate(inputs)

btn_calculate.on_click(on_calculate)
w_source_img.observe(on_edit_parameters)
w_focal_length.observe(on_edit_parameters)
w_alpha_max.observe(on_edit_parameters)
w_num_gores.observe(on_edit_parameters)
w_alpha_limit.observe(on_edit_parameters)
w_phi_no_cut.observe(on_edit_parameters)
w_angle.observe(on_edit_parameters)
w_quality.observe(on_edit_parameters)

display(btn_calculate)
display(out)


