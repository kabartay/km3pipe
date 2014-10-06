from __future__ import division, absolute_import, print_function

__author__ = 'tamasgal'

from km3pipe.tools import unpack_nfirst, split
from km3pipe.logger import get_logger

log = get_logger(__name__)

class Detector(object):
    def __init__(self, filename=None):
        self.det_file = None
        self.det_id = None
        self.n_doms = None
        self.doms = {}
        self.pmts = {}

        if filename:
            self.open_file(filename)

    def open_file(self, filename):
        pass

    def parse_header(self):
        """Extract information from the header of the detector file"""
        self.det_file.seek(0, 0)
        first_line = self.det_file.readline()
        self.det_id, self.n_doms = split(first_line, int)

    def parse_doms(self):
        """Extract dom information from detector file"""
        self.det_file.seek(0, 0)
        self.det_file.readline()
        lines = self.det_file.readlines()
        try:
            while True:
                line = lines.pop(0)
                if not line:
                    continue
                dom_id, line_id, floor_id, n_pmts = split(line, int)
                self.doms[dom_id] = (line_id, floor_id, n_pmts)
                for i in range(n_pmts):
                    raw_pmt_info = lines.pop(0)
                    pmt_info = raw_pmt_info.split()
                    pmt_id, x, y, z, dx, dy, dz, t0, rest = unpack_nfirst(pmt_info, 8)
                    if rest:
                        log.warn("Unexpected PMT values: '{0}'".format(rest))
                    pmt_id = int(pmt_id)
                    pmt_pos = (float(x), float(y), float(z))
                    pmt_dir = (float(dx), float(dy), float(dz))
                    t0 = float(t0)
                    pmt_entry = (pmt_id,) + pmt_pos + pmt_dir + (t0,)
                    self.pmts[(line_id, floor_id, i)] = pmt_entry
        except IndexError:
            pass


