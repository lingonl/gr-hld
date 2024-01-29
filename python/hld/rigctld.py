#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 lingo@de-mes.nl.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from gnuradio import gr
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import pmt
import socket

class rigctld(gr.sync_block):
    """
    Rigctld
    """
    def __init__(self, parent=None, addr='localhost', port=7356, baseband_width=1000000):
        gr.sync_block.__init__(self, name="rigctld", in_sig=[], out_sig=[])

        self.server = rigctld_server(parent, addr, port, baseband_width)
        
        self.freq = 0
        self.message_port_register_out(pmt.intern('freq'))
        self.server.freq_signal.connect(self.set_freq)

        self.baseband = 0
        self.message_port_register_out(pmt.intern('baseband'))
        self.server.baseband_signal.connect(self.set_baseband)

        self.offset = 0
        self.message_port_register_out(pmt.intern('offset'))
        self.server.offset_signal.connect(self.set_offset)

        self.acquired = False
        self.message_port_register_out(pmt.intern('acquired'))
        self.server.acquired_signal.connect(self.set_acquired)

    def work(self, input_items, output_items):
        return 0

    def set_freq(self, freq):
        self.freq = freq
        self.message_port_pub(pmt.intern('freq'), pmt.from_uint64(self.freq))

    def set_baseband(self, baseband):
        self.baseband = baseband
        self.message_port_pub(pmt.intern('baseband'), pmt.from_uint64(self.baseband))

    def set_offset(self, offset):
        self.offset = offset
        self.message_port_pub(pmt.intern('offset'), pmt.from_long(self.offset))

    def set_acquired(self, acquired):
        self.acquired = acquired
        self.message_port_pub(pmt.intern('acquired'), pmt.from_bool(self.acquired))

class rigctld_server(QThread):
    freq_signal = pyqtSignal(int)
    baseband_signal = pyqtSignal(int)
    offset_signal = pyqtSignal(int)
    acquired_signal = pyqtSignal(bool)

    def __init__(self, parent, addr, port, baseband_width):
        QThread.__init__(self, parent)

        self.addr = addr
        self.port = port
        self.baseband_width = baseband_width

        self.freq = 0
        self.baseband = 0
        self.offset = 0
        self.acquired = False

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.addr, self.port))
        server.listen(0)
        
        while True:
            client_socket, client_addr = server.accept()
            self.handle_client(client_socket, client_addr)

    def handle_client(self, client_socket, client_addr):
        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            commands = data.decode().split('\n')

            for command in commands:
                if not command:
                    continue

                # print(f"rigctld command: {command}")

                if command == 'q':
                    client_socket.close()
                    return

                response = self.handle_command(command.strip())

                if response:
                    # print(f"rigctld response: {response}")

                    client_socket.send(bytes(f'{response}\n', 'utf-8'))

    def handle_command(self, command):
        cmd = command.split()

        if not len(cmd):
            return None

        if cmd[0] == 'f':
            return self.get_freq()

        if cmd[0] == 'F':
            return self.set_freq(int(cmd[1]))

        if cmd[0] == 'AOS':
            return self.set_acquired(True)

        if cmd[0] == 'LOS':
            return self.set_acquired(False)

        return 'RPRT 1'

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        if self.freq != freq:
            self.freq = freq
            self.freq_signal.emit(self.freq)
        
        bandwidth = int(self.baseband_width / 16)

        (mult, offset) = divmod(self.freq, bandwidth)

        baseband = int((mult * bandwidth) + (bandwidth / 2))
        offset = int(offset - (bandwidth / 2))

        if self.offset != offset:
            self.offset = offset
            self.offset_signal.emit(self.offset)

        if self.baseband != baseband:
            self.baseband = baseband
            self.baseband_signal.emit(self.baseband)

        return 'RPRT 0'

    def set_acquired(self, acquired):
        self.acquired = acquired
        self.acquired_signal.emit(self.acquired)

        return 'RPRT 0'
