#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Scoreboard Hacker
# GNU Radio version: 3.8.1.0

from packet import *

from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import math
import osmosdr
import time

import os
import signal
import faulthandler
faulthandler.enable()


class tx_modem(gr.top_block):

    def __init__(self, center_freq_MHz, FSK_offset_kHz, bits_per_second, sample_rate_coefficient=0, repeat_enabled=False, TX_through_air=False):
        gr.top_block.__init__(self, "2FSK GNU Radio Modem")

        # if this is not defined, set to the minimum possible for HackRF One
        if sample_rate_coefficient <= 0:
            sample_rate_coefficient = 2e3 * 1.25 / FSK_offset_kHz #

        ##################################################
        # Scoreboard signal settings
        ##################################################
        self.center_freq_MHz = center_freq_MHz
        self.FSK_offset_kHz = FSK_offset_kHz
        self.bits_per_second = bits_per_second

        ##################################################
        # Transmission variables
        ##################################################
        TX_through_air = True
        self.sample_rate_coefficient = sample_rate_coefficient
        self.digital_sequence = digital_sequence = (1, 0)
            #(1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1)
        if TX_through_air:
            self.gain_out = gain_out = 1
        else:
            self.gain_out = gain_out = 0.25

        ##################################################
        # Dependent variables
        ##################################################
        self.FSK_offset_hz_converted = FSK_offset_hz_converted = FSK_offset_kHz * 1e3
        self.sample_rate = sample_rate = FSK_offset_hz_converted * sample_rate_coefficient
        self.offset_freq = offset_freq = -FSK_offset_hz_converted / 2

        ##################################################
        # Block initialization
        ##################################################
        self.blocks_vector_source_x_0 = blocks.vector_source_f(digital_sequence, repeat_enabled, 1, [])
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_float*1, int(sample_rate / bits_per_second))
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_float*1, sample_rate, True)
        self.blocks_vco_c_0 = blocks.vco_c(sample_rate, (2 * math.pi * FSK_offset_hz_converted), 1)
        self.blocks_rotator_cc_0 = blocks.rotator_cc((math.pi * 2 * offset_freq) / sample_rate)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                gain_out,
                sample_rate,
                FSK_offset_hz_converted * 1.1,
                10000,
                firdes.WIN_HAMMING,
                6.76))

        ##################################################
        # HackRF One block configuration
        ##################################################
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(sample_rate)
        self.osmosdr_sink_0.set_center_freq(center_freq_MHz * 1e6, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        #def sig_handler1(sig=None, frame=None):
        #    print("Error setting gain. Is the HackRF One connected?")
        #    shutdown()
        #    sys.exit(0)

        #print("a")
        #signal.signal(signal.SIGSEGV, sig_handler1)
        #print("b")

        if TX_through_air:
            self.osmosdr_sink_0.set_gain(14, 0)
            self.osmosdr_sink_0.set_if_gain(47, 0)
            self.osmosdr_sink_0.set_bb_gain(0, 0)
        else:
            self.osmosdr_sink_0.set_gain(0, 0)
            self.osmosdr_sink_0.set_if_gain(0, 0)
            self.osmosdr_sink_0.set_bb_gain(0, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_repeat_0, 0),          (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0),        (self.blocks_vco_c_0, 0))
        self.connect((self.blocks_vco_c_0, 0),           (self.blocks_rotator_cc_0, 0))
        self.connect((self.blocks_rotator_cc_0, 0),      (self.low_pass_filter_0, 0))
        self.connect((self.low_pass_filter_0, 0),        (self.osmosdr_sink_0, 0))



    ##################################################
    # GETs and SETs
    ##################################################

    def get_FSK_offset_kHz(self):
        return self.FSK_offset_kHz

    def set_FSK_offset_kHz(self, FSK_offset_kHz):
        self.FSK_offset_kHz = FSK_offset_kHz
        self.set_FSK_offset_hz_converted(self.FSK_offset_kHz * 1e3)

    def get_sample_rate_coefficient(self):
        return self.sample_rate_coefficient

    def set_sample_rate_coefficient(self, sample_rate_coefficient):
        self.sample_rate_coefficient = sample_rate_coefficient
        self.set_sample_rate(self.FSK_offset_hz_converted * self.sample_rate_coefficient)

    def get_FSK_offset_hz_converted(self):
        return self.FSK_offset_hz_converted

    def set_FSK_offset_hz_converted(self, FSK_offset_hz_converted):
        self.FSK_offset_hz_converted = FSK_offset_hz_converted
        self.set_offset_freq(-self.FSK_offset_hz_converted / 2 )
        self.set_sample_rate(self.FSK_offset_hz_converted * self.sample_rate_coefficient)
        self.low_pass_filter_0.set_taps(firdes.low_pass(self.gain_out, self.sample_rate, self.FSK_offset_hz_converted * 1.1, 10000, firdes.WIN_HAMMING, 6.76))

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.blocks_repeat_0.set_interpolation(int(self.sample_rate / self.bits_per_second))
        self.blocks_rotator_cc_0.set_phase_inc((math.pi * 2 * self.offset_freq) / self.sample_rate)
        self.blocks_throttle_0.set_sample_rate(self.sample_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(self.gain_out, self.sample_rate, self.FSK_offset_hz_converted * 1.1, 10000, firdes.WIN_HAMMING, 6.76))
        self.osmosdr_sink_0.set_sample_rate(self.sample_rate)

    def get_offset_freq(self):
        return self.offset_freq

    def set_offset_freq(self, offset_freq):
        self.offset_freq = offset_freq
        self.blocks_rotator_cc_0.set_phase_inc((math.pi * 2 * self.offset_freq) / self.sample_rate)

    def get_gain_out(self):
        return self.gain_out

    def set_gain_out(self, gain_out):
        self.gain_out = gain_out
        self.low_pass_filter_0.set_taps(firdes.low_pass(self.gain_out, self.sample_rate, self.FSK_offset_hz_converted * 1.1, 10000, firdes.WIN_HAMMING, 6.76))

    def get_digital_sequence(self):
        return self.digital_sequence

    def set_digital_sequence(self, digital_sequence):
        self.digital_sequence = digital_sequence
        self.blocks_vector_source_x_0.set_data(self.digital_sequence, [])

    def get_center_freq_MHz(self):
        return self.center_freq_MHz

    def set_center_freq_MHz(self, center_freq_MHz):
        self.center_freq_MHz = center_freq_MHz
        self.osmosdr_sink_0.set_center_freq(self.center_freq_MHz * 1e6, 0)

    def get_bits_per_second(self):
        return self.bits_per_second

    def set_bits_per_second(self, bits_per_second):
        self.bits_per_second = bits_per_second
        self.blocks_repeat_0.set_interpolation(int(self.sample_rate / self.bits_per_second))

    ##################################################
    # Custom functions
    ##################################################

    def updateDigitalSequence(self, raw_packet):
        self.set_digital_sequence(raw_packet)

    def printInfo(self):
        print("Sending 2FSK at", self.bits_per_second, "baud using sample rate", self.sample_rate / 1e6,
            "M/s. Signal has", self.FSK_offset_kHz, "KHz spacing centered at", self.center_freq_MHz,"MHz.")

    def shutdown(self):
        self.stop() # stop sending data into flowgraph
        self.wait() # wait for flowgraph to finish
