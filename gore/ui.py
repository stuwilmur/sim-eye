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
    inputs = dict(
    im = gore2.image_from_path(im_path), 
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

@debounce(2)
def on_edit_parameters(change):
    inputs = get_inputs()
    calculate(inputs)

btn_calculate.on_click(on_calculate)
w_num_gores.observe(on_edit_parameters)

display(btn_calculate)
display(out)


