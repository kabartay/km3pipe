from __future__ import division, absolute_import, print_function

__author__ = 'tamasgal'

import matplotlib.pyplot as plt

from km3pipe import Pipeline, Module
from km3pipe.io import CLBPump
from km3modules import StatusBar

class TOTHisto(Module):
    def __init__(self, **context):
        super(self.__class__, self).__init__(**context)
        self.tots = []

    def process(self, blob):
        for pmt_data in blob['PMTData']:
            self.tots.append(pmt_data.tot)
        return blob

    def finish(self):
        plt.hist(self.tots, 80)
        plt.xlabel("ToT [ns]")
        plt.ylabel('count')
        plt.show()

class PrintCLBHeader(Module):
    def process(self, blob):
        print(blob['CLBHeader'])
        return blob

pipeline = Pipeline()
pipeline.attach(CLBPump,
                filename='/Users/tamasgal/Data/KM3NeT/du1-clb/DOM2_run23.dat')
pipeline.attach(StatusBar)
pipeline.attach(PrintCLBHeader)
pipeline.attach(TOTHisto)
pipeline.drain(30)
