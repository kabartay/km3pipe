# coding=utf-8
# Filename: pandas.py
# pylint: disable=C0103,R0903
# vim:set ts=4 sts=4 sw=4 et:
"""
Pandas Helpers.
"""
from __future__ import division, absolute_import, print_function

from collections import defaultdict
import os.path
from six import string_types

import numpy as np
import pandas as pd
import tables as tb

from km3pipe.logger import logging
from km3pipe.tools import insert_prefix_to_dtype

log = logging.getLogger(__name__)  # pylint: disable=C0103

__author__ = "Moritz Lotze"
__copyright__ = "Copyright 2016, Tamas Gal and the KM3NeT collaboration."
__credits__ = []
__license__ = "MIT"
__maintainer__ = "Moritz Lotze"
__email__ = "mlotze@km3net.de"
__status__ = "Development"


class H5Chain(object):
    """Read/write multiple HDF5 files as ``pandas.DataFrame``.

    It is impliend that all files share the same group/tables
    structure and naming.

    Parameters
    ----------
    filenames: list(str), or dict(fname -> h5file)

    Examples
    --------
    >>> filenames = ['numu_cc.h5', 'anue_nc.h5']
    >>> n_evts = {'numu_cc.h5': None, 'anue_nc.h5': 100, }
    # either tables keys below '/', or group names
    >>> keys = ['hits', 'reco']
    >>> step = {'mc_tracks': 2}

    >>> c = H5Chain(filenames)
    >>> coll = c(n_evts, keys, step)
    {'mc_tracks': pd.Dataframe, 'hits' pd.DataFrame, 'reco': dataframe}

    >>> # these are pandas Dataframes
    >>> X = coll['reco']
    >>> wgt = coll['event_info']['weights_w2']
    >>> Y_ene = coll['mc_tracks']['energy']
    """
    def __init__(self, filenames):
        self.h5files = {}
        if isinstance(filenames, dict):
            self.h5files.update(filenames)
            return
        for fn in filenames:
            h5 = tb.open_file(fn, 'r')
            self.h5files[fn] = h5

    def close(self):
        for h5 in self.h5files.values():
            h5.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __enter__(self):
        return self

    def __call__(self, n_evts=None, keys=None):
        """
        Parameters
        ----------
        n_evts: int or dict(str->int) (default=None)
            Number of events to read. If None, read every event from all.
            If int, read that many from all.  In case of dict: If a
            filename is in the dict, read that many events from the file.

        keys: list(str) (default=None)
            Names of the tables/groups to read. If None, read all.
            Refers only to nodes sitting below '/',
            e.g. '/mc_tracks' (Table) or '/reco' (Group).
        """
        store = defaultdict(list)
        for fname, h5 in self.h5files.items():
            n = n_evts
            if isinstance(n_evts, dict):
                n = n_evts[fname]
            max_id = np.unique(h5.root.event_info.read(field='event_id', stop=n))[-1]
            print(max_id)
            # tables under '/', e.g. mc_tracks
            for tab in h5.iter_nodes('/', classname='Table'):
                tabname = tab.name
                if keys is not None and tabname not in keys:
                    continue
                arr = _read_table(tab, max_id)
                arr = pd.DataFrame.from_records(arr)
                store[tabname].append(arr)

            # groups under '/', e.g. '/reco'
            # tables sitting below will be merged
            for gr in h5.iter_nodes('/', classname='Group'):
                groupname = gr._v_name
                if keys is not None and groupname not in keys:
                    continue
                arr = read_group(gr, max_id)
                store[groupname].append(arr)

        for key, dfs in sorted(store.items()):
            store[key] = pd.concat(dfs, axis=0)
        return store


def map2df(map):
    return pd.DataFrame.from_records(map, index=np.ones(1, dtype=int))


def _read_table(tab, max_id=None):
    # takewhile(lambda x: x['event_id'] != max_id, tab.iterrows())
    return tab.read_where('event_id <= %d' % max_id)


def read_group(group, max_id=None, **kwargs):
    # Store through groupname, insert tablename into dtype
    df = []
    for tab in group._f_iter_nodes(classname='Table'):
        tabname = tab.name
        if max_id is None:
            arr = tab.read(**kwargs)
        else:
            arr = _read_table(tab, max_id)
        arr = insert_prefix_to_dtype(arr, tabname)
        arr = pd.DataFrame.from_records(arr)
        df.append(arr)
    df = pd.concat(df, axis=1)
    return df


def df_to_h5(df, filename, where):
    """Write pandas dataframes with proper columns.
    """
    write_table(df.to_records(index=False), filename, where)


def write_table(array, h5file, where):
    """Write a structured numpy array into a H5 table.
    """
    if isinstance(h5file, string_types):
        own_h5 = True
        h5file = tb.open_file(h5file, 'a')
    filt = tb.Filters(complevel=5, shuffle=True, fletcher32=True)
    loc, tabname = os.path.split(where)
    if loc == '':
        loc = '/'
    h5file.create_table(loc, tabname, obj=array, createparents=True,
                        filters=filt)
    if own_h5:
        h5file.close()