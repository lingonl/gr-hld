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

class rotctld(gr.sync_block):
    """
    Rotctld
    """
    def __init__(self, parent=None, addr='localhost', port=4533):
        gr.sync_block.__init__(self, name="rigctld", in_sig=[], out_sig=[])

        self.server = rotctld_server(parent, addr, port)
        
        self.azimuth = 0.0
        self.message_port_register_out(pmt.intern('azimuth'))
        self.server.azimuth_signal.connect(self.set_azimuth)

        self.elevation = 0.0
        self.message_port_register_out(pmt.intern('elevation'))
        self.server.elevation_signal.connect(self.set_elevation)

    def work(self, input_items, output_items):
        return 0

    def set_azimuth(self, azimuth):
        self.azimuth = azimuth
        self.message_port_pub(pmt.intern('azimuth'), pmt.from_float(self.azimuth))

    def set_elevation(self, elevation):
        self.elevation = elevation
        self.message_port_pub(pmt.intern('elevation'), pmt.from_float(self.elevation))

class rotctld_server(QThread):
    azimuth_signal = pyqtSignal(float)
    elevation_signal = pyqtSignal(float)

    def __init__(self, parent, addr, port):
        QThread.__init__(self, parent)

        self.addr = addr
        self.port = port

        self.azimuth = 0.00
        self.elevation = 0.00

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

                # print(f"rotctld command: {command}")

                if command == 'q':
                    client_socket.close()
                    return

                response = self.handle_command(command.strip())

                if response:
                    # print(f"rotctld response: {response}")

                    client_socket.send(bytes(f'{response}\n', 'utf-8'))

    def handle_command(self, command):
        cmd = command.split()

        if not len(cmd):
            return None

        if cmd[0] == 'p':
            return self.get_position()

        if cmd[0] == 'P':
            azimuth = float(cmd[1].replace(',', '.'))
            elevation = float(cmd[2].replace(',', '.'))

            return self.set_position(azimuth, elevation)

        return 'RPRT 1'

    def get_position(self):
        return f"{self.azimuth:.2f}\n{self.elevation:.2f}"

    def set_position(self, azimuth, elevation):
        if self.azimuth != azimuth:
            self.azimuth = azimuth
            self.azimuth_signal.emit(self.azimuth)
        
        if self.elevation != elevation:
            self.elevation = elevation
            self.elevation_signal.emit(self.elevation)

        return 'RPRT 0'