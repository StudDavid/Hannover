#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path


class Constants:
    # FILE PATHS
    ROOT_DIRECTORY = Path(os.getcwd())
    OUTPUT_PATH = ROOT_DIRECTORY / 'output'
    SOURCE_PATH = ROOT_DIRECTORY / 'src'

    # SIMULATION PARAMETERS
    TIME_STEP = 10  # in seconds
    NUMBER_ITERATIONS = int(1E3)
    # constants B. subtilius

    BSUB_WIDTH = 1    # MICROMETERS https://en.wikipedia.org/wiki/Bacillus_subtilis
    BSUB_LENGTH = 4  # MICROMETERS https://en.wikipedia.org/wiki/Bacillus_subtilis
    BSUB_MASS = 10 ** (-15)  # kg
    BSUB_MORTALITY_RATE = 0.06
    BSUB_CRITICAL_LENGTH = 4.7  # MICROMETERS
    BSUB_MEAN_SPEED = 50  # 50 MICROMETERS / s mean speed

    BSUB_DOUBLING_TIME = 720    # SECONDS DOI: 10.1128/jb.167.1.219-230.1986
    BSUB_GROWTH_FACTOR = 2 * BSUB_LENGTH / BSUB_DOUBLING_TIME  # MICROMETERS / s

    gr_factor_inv = 0.05  # 0.2
    gr_pr_i = 10.1  # 1.1
    MOTION_ACTIVATION_PROBABILITY = 0.005
    MOTION_DEACTIVATION_PROBABILITY = 0.01

    # constants regarding biofilm
    START_NUMBER_BACTERIA = 1

    # constants regarding visualisation
    WINDOW_SIZE = (500, 750)
