# --------------------------------------------------
# Copyright (C) 2020 Antonio Viesti (a.viesti@eutropia.it).
# Creative Commons CC BY (https://creativecommons.org/licenses/by/4.0/)
# --------------------------------------------------

# Drawing toolbox for the LED panel device.

import argparse
import logging
import time

import numpy as np
from luma.core.interface.serial import noop, spi
from luma.core.legacy import show_message, text
from luma.core.legacy.font import (CP437_FONT, LCD_FONT, SINCLAIR_FONT, TINY_FONT, proportional)
from luma.core.render import canvas
from luma.led_matrix.device import max7219

# Gets the LED panel device, in its default configuration.
#
# Returns: the device - a MAX7219 LED panel - in its default configuration.
def get_device_in_default_configuration():

    logger = logging.getLogger(__name__)

    logger.debug('Getting LED panel device, in its default configuration...')
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded = 1, block_orientation = 0, rotate = 0, blocks_arranged_in_reverse_order = False)
 
    return device

# Gets the LED panel device, in the specified configuration.
#
# Arguments:
# cascaded: sets how many cascaded panels, defaulting to 1.
# block_orientation: redefines the panel orientation when it is wired vertically, defaulting to 0 (choices are [0, 90, -90]).
# rotate:  rotates the panel (0=0°, 1=90°, 2=180°, 3=270°), defaulting to 0 (choices=[0, 1, 2, 3]).
# inreverse: has to be true if panels are in reverse order, defaulting to false.
#
# Returns: the device - a MAX7219 LED panel - in the specified configuration.
def get_device(n, block_orientation, rotate, inreverse):

    logger = logging.getLogger(__name__)

    logger.debug('Getting LED panel device...')
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=n or 1, block_orientation=block_orientation, rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse)
 
    return device

# Scrolls a text message.
#
# Args:
# device: the device.
# text_message: the text message.
def write(device, text_message):

    logger = logging.getLogger(__name__)

    logger.debug('Writing \"' + text_message + '\"...')
    show_message(device, text_message, fill='white', font=proportional(CP437_FONT))

# Turn on a LED element.
#
# Args:
# device: the device.
# point: a point, like (4, 6).
# milliseconds: the time (in milliseconds) during wich LEDs are turned on.
def draw_point(device, point, milliseconds):

    with canvas(device) as draw:
        draw.point(point, fill='white')
    time.sleep(milliseconds/1000)

# Turn on an array of LED elements.
#
# Args:
# device: the device.
# points: an array of points, like  [(0, 0), (1, 0), (4, 6)].
# milliseconds: the time (in milliseconds) during wich LEDs are turned on.
def draw_points(device, points, milliseconds):
    with canvas(device) as draw:
        draw.point(points, fill='white')
    time.sleep(milliseconds/1000)

# Draws a boolean matrix, like this:
# [[0, 1, 1, 0, 0, 1, 0, 0],
#  [1, 1, 1, 0, 1, 0, 1, 1],
#  [0, 0, 1, 0, 0, 0, 0, 0],
#  [1, 1, 0, 1, 0, 1, 0, 1],
#  [0, 0, 1, 0, 0, 0, 0, 0],
#  [1, 1, 0, 0, 1, 1, 0, 1],
#  [0, 1, 0, 1, 0, 1, 0, 1],
#  [1, 1, 1, 1, 0, 0, 1, 1]].
# Turns on the LED elements with value 1.
#
# Args:
# device: the device.
# boolean_matrix: the boolean matrix.
# milliseconds: the time (in milliseconds) during wich LEDs are turned on. 
def draw_boolean_matrix(device, boolean_matrix, milliseconds):

    logger = logging.getLogger(__name__)

    # Get the xy_coordinates of the LED elements with value 1
    index_of_elements_with_value_1 = np.where(boolean_matrix == 1)
    xy_coordinates_of_elements_with_value_1 = list(zip(index_of_elements_with_value_1[1], index_of_elements_with_value_1[0]))

    # Turns on the LED elements with value 1.
    logger.debug('Turning on the LEDs:')
    logger.debug(xy_coordinates_of_elements_with_value_1)
    with canvas(device) as draw:
        draw.point(xy_coordinates_of_elements_with_value_1, fill='white')
    time.sleep(milliseconds/1000)

# Composes a boolean matrix representing dinamically a fluid level.
#
# Args:
# level: the level value.
def compose_level_matrix(level):

    logger = logging.getLogger(__name__)

    matrix_dimension = 8

    # Populate the submatrix above the level with 0 values.
    above_the_level = np.random.choice((0, 1), (matrix_dimension - level, matrix_dimension), p = [1, 0])
    logger.debug('Above the level:')
    logger.debug(above_the_level)

    # Populate the submatrix at the level - one row - with 0 (50%) and 1 (50%) values.
    at_the_level = np.random.choice((0, 1), (1, matrix_dimension), p = [.50, .50])
    logger.debug('At the level:')
    logger.debug(at_the_level)

    # Populate the submatrix below the level with 0 (1%) and 1 (99%) values.
    below_the_level = np.random.choice((0, 1), (level - 1, matrix_dimension), p = [.01, .99])
    logger.debug('Below the level:')
    logger.debug(below_the_level)

    # Concatenate the above_the_level, at_the_level, and below_the_level submatrices.
    level_matrix = np.concatenate ((above_the_level, at_the_level, below_the_level))
    logger.debug('Level matrix:')
    logger.debug(level_matrix)

    return level_matrix

# Draws a level matrix.
#
# Args:
# device: the device.
# level: the level value.
def draw_level(device, level):

    draw_boolean_matrix(device, compose_level_matrix(level), 500)

if __name__ == '__main__':

    # Get command-line arguments.
    parser = argparse.ArgumentParser(description='led_matrix arguments', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--cascaded', '-n', type=int, default=1, help='Number of cascaded MAX7219 LED matrices')
    parser.add_argument('--block-orientation', type=int, default=0, choices=[0, 90, -90], help='Corrects block orientation when wired vertically')
    parser.add_argument('--rotate', type=int, default=0, choices=[0, 1, 2, 3], help='Rotate display 0=0°, 1=90°, 2=180°, 3=270°')
    parser.add_argument('--reverse-order', type=bool, default=False, help='Set to true if blocks are in reverse order')
    args = parser.parse_args()

    # Get the device.
    device = get_device(args.cascaded, args.block_orientation, args.rotate, args.reverse_order)

    # Run some diagnostics: write a scrolling text message.
    write(device, 'Hello, world')

    # Run some diagnostics: turn on a LED element.
    draw_point(device, (4, 6), 1000)

    # Run some diagnostics: turn on an array of LED elements.
    draw_points(device, [(0, 0), (1, 0), (4, 6)], 1000)

    # Run some diagnostics: draws some boolean matrices.
    boolean_matrix = np.array([[1, 1, 1, 1, 1, 1, 1, 1],
                                 [1, 1, 1, 1, 1, 1, 1, 1],
                                 [1, 1, 1, 1, 1, 1, 1, 1],
                                 [1, 1, 1, 1, 1, 1, 1, 1],
                                 [1, 1, 1, 1, 1, 1, 1, 1],
                                 [1, 1, 1, 1, 1, 1, 1, 1],
                                 [1, 1, 1, 1, 1, 1, 1, 1],
                                 [1, 1, 1, 1, 1, 1, 1, 1]])
    draw_boolean_matrix(device, boolean_matrix, 250)
    boolean_matrix = np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                                 [1, 1, 1, 1, 1, 1, 1, 1],
                                 [0, 0, 0, 0, 0, 0, 0, 0],
                                 [1, 1, 1, 1, 1, 1, 1, 1],
                                 [0, 0, 0, 0, 0, 0, 0, 0],
                                 [1, 1, 1, 1, 1, 1, 1, 1],
                                 [0, 0, 0, 0, 0, 0, 0, 0],
                                 [1, 1, 1, 1, 1, 1, 1, 1]])
    draw_boolean_matrix(device, boolean_matrix, 250)
    boolean_matrix = np.array([[0, 1, 0, 1, 0, 1, 0, 1],
                                 [0, 1, 0, 1, 0, 1, 0, 1],
                                 [0, 1, 0, 1, 0, 1, 0, 1],
                                 [0, 1, 0, 1, 0, 1, 0, 1],
                                 [0, 1, 0, 1, 0, 1, 0, 1],
                                 [0, 1, 0, 1, 0, 1, 0, 1],
                                 [0, 1, 0, 1, 0, 1, 0, 1],
                                 [0, 1, 0, 1, 0, 1, 0, 1]])
    draw_boolean_matrix(device, boolean_matrix, 250)

# --------------------------------------------------