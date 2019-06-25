#
# purpose:
# Connect to SD remote server and control LibreOffice instance
# 

import time

from request import Request
import infoscreen, config, web
import unoremote 

# temp
SLIDE_TIME = 2

class LibreOfficeController():
    def __init__ (self, signd):
        self.signd          = signd
        self.libo_running   = False
        self.info_showing   = True

        self.start_libo()

        self.client = unoremote.UNOClient(self)
        self.client.start()

        self.last_transition    = 0
        self.slideshow_running  = False

    def start_libo (self):
        pass

    def run (self):
        # TODO check the playlist, if we have >= 1 presentations
        #      play the first one, otherwise stop presenting / libreoffice

        secs = time.time()

        if self.client.connected and not self.slideshow_running:
            self.client.play_file()
            self.slideshow_running = True

        if (self.slideshow_running and 
                secs > self.last_transition + SLIDE_TIME):
            self.client.transition_next()
            self.last_transition = secs

    def start_info_screen (self):
        if config.SHOW_INFO_SCREEN:
            self.info_showing = True
            addr = web.get_address()
            infoscreen.start_info(addr)

    def stop_info_screen (self):
        if config.SHOW_INFO_SCREEN:
            self.info_showing = False
            infoscreen.stop_info()

    def handle_irp_message (self, msg):
        print("IRP", msg)
        if 'slideshow_started' == msg:
            self.last_transition    = time.time()
            self.slideshow_running  = True

        elif 'slideshow_finished' == msg:
            self.slideshow_running = False

    def handle_web_request(self, msg):
        mtype = msg.get('type')

        if Request.PLAY_FILE == mtype:
            # TODO need to either restart libreoffice, supplying the correct file
            #      or add a way of changing the current file while libreoffice is 
            #      running
            pass

        if Request.PLAY == mtype:
            pass

        if Request.PAUSE == mtype:
            pass

