"""Hit processing classes.

This module defines 2 base classes: HitStatistics (e.g. to count n_doms)
and HitSelector (e.g. FirstHits).
"""

import km3pipe as kp
import numpy as np
import pandas as pd     # noqa
from scipy.stats import trimboth

from km3pipe.dataclasses import HitSeries


class HitStatistics(kp.Module):
    """Compute stuff on hits.

    Parameters
    ----------
    key_in: str, default='Hits'
        Key of the hits to use.
    key_out: str, default='None'
        Key to write into.
    """
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.key_in = self.get('key_in') or 'Hits'
        self.key_out = self.get('key_out') or 'SelectedHits'

    def process(self, blob):
        """Read Hits, convert to pandas, compute stuff.
        """
        hits = blob[self.key_in]
        hits = hits.serialise(to='pandas')
        blob[self.key_out] = self.compute(hits)
        return blob

    def compute(self, pd_hits):
        return


class NDoms(HitStatistics):
    """Count active Doms.

    Parameters
    ----------
    key_in: str, default='Hits'
        Key of the hits to use.
    key_out: str, default='n_doms'
        Key to write into.
    """
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.key_in = self.get('key_in') or 'Hits'
        self.key_out = self.get('key_out') or 'n_doms'

    def compute(self, pd_hits):
        dus = np.unique(pd_hits['dom_id'])
        return len(dus)


class HitSelector(kp.Module):
    """Select hits according to a criterion.

    Defaults to ``return hits``.

    Parameters
    ----------
    key_in: str, default='Hits'
        Key of the hits to select.
    key_out: str, default='SelectedHits'
        Key to write into.
    """
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.key_in = self.get('key_in') or 'Hits'
        self.key_out = self.get('key_out') or 'SelectedHits'

    def process(self, blob):
        """Read Hits, call ``process_hits``, store result.
        """
        hits = blob[self.key_in]
        hits = self.process_hits(hits)
        blob[self.key_out] = hits
        return blob

    def process_hits(self, hits):
        """Convert to pandas, call ``select_hits``, convert to HitSeries.
        """
        hits = hits.serialise(to='pandas')
        hits = self.select_hits(hits)
        return HitSeries.from_table(hits)

    def select_hits(self, pd_hits):
        """Defaults to nothing: ``return hits``."""
        return pd_hits


class FirstHits(HitSelector):
    """Select first hits on each dom.

    Parameters
    ----------
    key_in: str, default='Hits'
        Key of the hits to select.
    key_out: str, default='FirstHits'
        Key to write into.

    """
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.key_in = self.get('key_in') or 'Hits'
        self.key_out = self.get('key_out') or 'FirstHits'

    def process_hits(self, hits):
        # do not convert to pandas, the HitSeries method does the job.
        return hits.first_hits


class TrimmedHits(HitSelector):
    """Select hits in a percentile range.

    E.g. pos_z, time, pos_3d.

    Parameters
    ----------
    which: str, default=None
        The quantity to run the selection on. If None, just trim the hits in
        the order in which they appear. Otherwise sort by 'which'.
        Possible values are [None, 'time', 'pos_z'].
    trim: float, default=0.1
        The amount to trim. Remove from trim to 1-trim.
    key_in: str, default='Hits'
        Key of the hits to trim.
    key_out: str, default='TrimmedHits'
        Key to write into.
    """
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.which = self.get('which') or 'time'
        self.trim = self.get('trim') or 0.1
        self.key_in = self.get('key_in') or 'Hits'
        self.key_out = self.get('key_out') or 'TrimmedHits'

    def select_hits(self, pd_hits):
        if self.which is None:
            n = len(pd_hits)
            idx = trimboth(range(n), self.trim)
            return pd_hits.iloc[idx]
        if self.which in {'time', 'pos_z'}:     # noqa
            lo = df.quantile(self.trim)[self.which]
            hi = df.quantile(1 - self.trim)[self.which]
            return pd_hits.query(
                '{l} < {w} and {w} <= {h}'.format(l=lo, h=hi, w=self.which))
        # if not matching anything above
        raise KeyError("which: '{}' not understood.".format(self.which))
