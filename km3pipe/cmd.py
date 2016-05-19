# coding=utf-8
# Filename: cmd.py
"""
KM3Pipe command line utility.

Usage:
    km3pipe test
    km3pipe tohdf5 [-n EVENTS] -i FILE -o FILE
    km3pipe hdf2root -i FILE [-o FILE]
    km3pipe runtable [-n RUNS] DET_ID
    km3pipe (-h | --help)
    km3pipe --version

Options:
    -h --help       Show this screen.
    -i FILE         Input file.
    -o FILE         Output file.
    -n EVENTS/RUNS  Number of events/runs.
    DET_ID          Detector ID (eg. D_ARCA001).

"""

from __future__ import division, absolute_import, print_function

import sys

from km3pipe import version
from km3pipe.db import DBManager
from km3modules import StatusBar


def tohdf5(input_file, output_file, n_events):
    """Convert ROOT file to HDF5 file"""
    from km3pipe import Pipeline  # noqa
    from km3pipe.pumps import AanetPump, HDF5Sink  # noqa

    pipe = Pipeline()
    pipe.attach(AanetPump, filename=input_file)
    pipe.attach(StatusBar, every=1000)
    pipe.attach(HDF5Sink, filename=output_file)
    pipe.drain(n_events)


def runtable(det_id, n=5, sep='\t'):
    """Print the run table of the last `n` runs for given detector"""
    db = DBManager()
    df = db.run_table(det_id)
    if n is None:
        selected_df = df
    else:
        selected_df = df.tail(n)
    selected_df.to_csv(sys.stdout, sep=sep)


def hdf2root(infile, outfile):
    from rootpy.io import root_open
    from rootpy import asrootpy
    from root_numpy import array2tree
    from tables import open_file

    h5 = open_file(infile, 'r')
    rf = root_open(outfile, 'recreate')

    # 'walk_nodes' does not allow to check if is a group or leaf
    #   exception handling is bugged
    #   introspection/typecheck is buged
    # => this moronic nested loop instead of simple `walk`
    for group in h5.walk_groups():
        for leafname, leaf in group._v_leaves.items():
            tree = asrootpy(array2tree(leaf[:], name=leaf._v_pathname))
            tree.write()
    rf.close()
    h5.close()


def main():
    from docopt import docopt
    arguments = docopt(__doc__, version=version)

    try:
        n = int(arguments['-n'])
    except TypeError:
        n = None

    if arguments['tohdf5']:
        tohdf5(arguments['-i'], arguments['-o'], n)

    if arguments['runtable']:
        runtable(arguments['DET_ID'], n)

    if arguments['hdf2root']:
        infile = arguments['-i']
        if not arguments['-o']:
            outfile = infile + '.root'
        hdf2root(infile, outfile)
