#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 lingo@de-mes.nl.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from gnuradio import gr, gr_unittest
# from gnuradio import blocks
from rotctld import rotctld

class qa_rotctld(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):
        instance = rotctld()
        # FIXME: make some tests

    def test_001_descriptive_test_name(self):
        # set up fg
        self.tb.run()
        # check data


if __name__ == '__main__':
    gr_unittest.run(qa_rotctld)
