__author__ = 'tamasgal'

import urwid

from pipeinspector.widgets import BlobWidget, BlobBrowser
from pipeinspector.settings import UI
from km3pipe.pumps import EvtPump





class MainFrame(urwid.Frame):
    """
    Represents the main GUI

    """
    def __init__(self):
        self.header = urwid.AttrWrap(urwid.Text("The header!", align='center'),
                                     'header')

        self.blob_browser = BlobBrowser()

        self.info_area = urwid.Text('')
        self.blobs = BlobWidget()
        self.footer = urwid.Columns([self.info_area, self.blobs])

        self.frame = urwid.AttrWrap(urwid.Frame(self.blob_browser,
                                                header=self.header,
                                                footer=self.footer), 'default')
        urwid.Frame.__init__(self, self.frame)
        self.overlay = None

        self.pump = EvtPump(filename='/Users/tamasgal/Data/KM3NeT/v4/modk40_v4_numuCC_23.evt')

        urwid.connect_signal(self.blobs, 'blob_selected', self.blob_selected)
        self.blobs.goto_blob(0)

    def blob_selected(self, index):
        self.info_area.set_text("Blob: {0}".format(index))

        blob = self.pump.process(None)
        self.blob_browser.load(blob)

    def keypress(self, size, key):
        input = urwid.Frame.keypress(self, size, key)
        if input is None:
            return
        if input in UI.keys['left']:
            self.blobs.previous_blob()
        elif input in UI.keys['right']:
            self.blobs.next_blob()
        elif input in [key.upper() for key in UI.keys['left']]:
            self.blobs.previous_blob(step=10)
        elif input in [key.upper() for key in UI.keys['right']]:
            self.blobs.next_blob(step=10)
        elif input in UI.keys['home']:
            self.blobs.goto_blob(0)
        else:
            return self.body.keypress(size, input)