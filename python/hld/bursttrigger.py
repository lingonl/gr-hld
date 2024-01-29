#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 lingo@de-mes.nl.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
from gnuradio import gr, analog
import numpy as np
import pmt

class bursttrigger(gr.sync_block):
    def __init__(self, azimuth_min=-180.0, azimuth_max=540.0, elevation_min=-20.0, elevation_max=210.0):
        gr.sync_block.__init__(self, 'Burst trigger', [], [np.short])

        self.azimuth_min = azimuth_min
        self.azimuth_max = azimuth_max
        self.elevation_min = elevation_min
        self.elevation_max = elevation_max
        
        self.acquired = False
        self.azimuth = 0.0
        self.elevation = 0.0

        self.burst = False
        self.burst_short = 0
        self.burst_key = pmt.intern('burst')
        self.burst_val = pmt.from_bool(self.burst)

        self.message_port_register_in(pmt.intern('acquired'))
        self.set_msg_handler(pmt.intern('acquired'), self.handle_acquired)

        self.message_port_register_in(pmt.intern('azimuth'))
        self.set_msg_handler(pmt.intern('azimuth'), self.handle_azimuth)

        self.message_port_register_in(pmt.intern('elevation'))
        self.set_msg_handler(pmt.intern('elevation'), self.handle_elevation)

        self.message_port_register_out(pmt.intern('state'))

    def handle_acquired(self, msg):
        self.acquired = pmt.to_bool(msg)
        self.update_burst()

    def handle_azimuth(self, msg):
        self.azimuth = pmt.to_float(msg)
        self.update_burst()

    def handle_elevation(self, msg):
        self.elevation = pmt.to_float(msg)
        self.update_burst()

    def update_burst(self):
        burst = (
            self.acquired and
            self.azimuth >= self.azimuth_min and
            self.azimuth <= self.azimuth_max and
            self.elevation >= self.elevation_min and
            self.elevation <= self.elevation_max
        )

        if self.burst != burst:
            self.burst = burst
            self.burst_val = pmt.from_bool(self.burst)
            self.burst_short = 0
            if self.burst:
                self.burst_short = 1

            self.message_port_pub(pmt.intern('state'), self.burst_val)

    def work(self, input_items, output_items):
        output_items[0][:] = self.burst_short

        return len(output_items[0])
