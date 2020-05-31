# --------------------------------------------------
# Copyright (C) 2020 Antonio Viesti (a.viesti@eutropia.it).
# Creative Commons CC BY (https://creativecommons.org/licenses/by/4.0/)
# --------------------------------------------------

# Mareografie (1) — When above — Alta e bassa marea.
#
# «Mareografie (1) — When above» gets the current sea level value nearby Italian sea towns, and draws it on a 8X8 LED panel, iteratively.
# A tide gauge — also known as mareograph, marigraph, sea-level recorder, or limnimeter — is a device for measuring the change in sea level (hydrometric_level).
# The Italian ISPRA National Tidegauge Network is composed of 36 monitoring stations — powered by solar panels — located in:
# Ancona
# Anzio
# Bari
# Cagliari
# Carloforte
# Catania
# Civitavecchia
# Crotone
# Gaeta
# Genova
# Ginostra
# Imperia
# La Spezia
# Lampedusa
# Livorno
# Marina di Campo
# Messina
# Napoli
# Ortona
# Otranto
# Palermo
# Palinuro
# Ponza
# Porto Empedocle
# Porto Torres
# Ravenna
# Reggio Calabria
# Salerno
# San Benedetto del Tronto
# Sciacca
# Strombolicchio
# Taranto
# Tremiti
# Trieste
# Valona
# Venezia
# Vieste

import logging
import time
from queue import Queue
from threading import Thread

from ispra_rmn.ispra_rmn_services import get_discretized_hydrometric_level_nearby
from led_panel.led_panel_drawings import draw_level, get_device_in_default_configuration

# Tide gauge geographical reference.
here = 'Bari'

# LED panel resolution.
dots = 8

# Hydrometric level queue.
level_queue = Queue()

# Gets and enqueues the hydrometric level value.
#
# Args:
# here: the tide gauge geographical reference.
# dots: the LED panel resolution.
# level_queue: the queue of hydrometric level values.
def get_hydrometric_level_nearby(here, dots, level_queue):

    cuts = dots

    while True:
        level = get_discretized_hydrometric_level_nearby(here, cuts)
        level_queue.put(level)
        time.sleep(60*10) # TODO 60*5

# Dequeues and draws the hydrometric level value.
#
# Args:
# level_queue: the queue of hydrometric level values.
def draw_hydrometric_level(level_queue):

    device = get_device_in_default_configuration()

    level = 0
    while True:
        if not level_queue.empty():
            level= level_queue.get()
        if level > 0:
            draw_level(device, level)

# Configure logging.
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Thread the ingesting and enqueuing of the hydrometric level.
thread_get_hydrometric_level_nearby = Thread(target = get_hydrometric_level_nearby, args = (here, dots, level_queue, ))
thread_get_hydrometric_level_nearby.setDaemon(True)
thread_get_hydrometric_level_nearby.start()

# Thread the dequeuing and drawing of the hydrometric level.
thread_draw_hydrometric_level = Thread(target = draw_hydrometric_level, args = (level_queue, ))
thread_draw_hydrometric_level.setDaemon(True)
thread_draw_hydrometric_level.start()

while True:
    pass

# --------------------------------------------------