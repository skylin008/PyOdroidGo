"""
    Render mandelbrot on Odroid Go
    It's for loboris MicroPython port!
    
    Based on code from https://github.com/pypyjs/pypyjs-examples/
"""
import sys
import time

import display
import machine
import micropython
from machine import SPI
from micropython import const
from odroidgo.screen import screen

micropython.opt_level(99)


def gen_pow(limit, reverse=True):

    interlace_steps = []
    step = 0
    while True:
        value = 2 ** step
        if value >= limit:
            break
        interlace_steps.append(value)
        step += 1

    if reverse:
        interlace_steps.reverse()
    return tuple(interlace_steps)


def interlace_generator(limit):

    interlace_steps = gen_pow(limit, reverse=True)

    pos = 0
    step = 1
    iteration = 0
    size = interlace_steps[iteration]

    while True:
        yield pos, size
        pos += size * step

        if pos > limit:
            step = 2
            iteration += 1
            try:
                size = interlace_steps[iteration]
            except IndexError:
                return

            pos = size


def render_mandelbrot_line(tft, width, height, y, size, left, right, top, bottom, iterations):
    color_factor = int(0xffffff / iterations)

    for x in range(width):
        z = complex(0, 0)
        c = complex(left + x * (right - left) / width, top + y * (bottom - top) / height)
        norm = abs(z) ** 2
        for count in range(iterations):
            if norm <= 4:
                z = z * z + c
                norm = abs(z * z)
            else:
                break

        color = int(count * color_factor)

        if size > 1:
            # https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/wiki/display#tftlinex-y-x1-y1-color
            tft.line(x, y, x, y + size, color)
        else:
            # https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/wiki/display#tftpixelx-y-color
            tft.pixel(x, y, color)


def mandelbrot(tft, width, height, left, right, top, bottom, iterations):
    for y, size in interlace_generator(height):
        render_mandelbrot_line(tft, width, height, y, size, left, right, top, bottom, iterations)


def main():
    screen.reset()

    # https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/wiki/machine#machinewdtenable
    machine.WDT(False)

    start_time = time.time()
    mandelbrot(
        screen,
        width=screen.width,
        height=screen.height,
        left=const(-2),
        right=0.5,
        top=const(1.25),
        bottom=const(-1.25),
        iterations=const(40),
    )
    duration = time.time() - start_time
    print("rendered in %.1f sec." % duration)


if __name__ == "builtins":  # start with F5 from thonny editor ;)
    main()
