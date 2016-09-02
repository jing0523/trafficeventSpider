# -*- coding: utf-8 -*-
class ExportOptions(object):
    '''
        Attributes：-
        activeparser                 -<obj,bool>     default true, will return active flag by comparing occurTime and endTime
        eventType                    -str
        datetimeparser               -<obj,bool>     bool:use parser (start_date?end_date),list of object: DataParser
        hasImg                       -bool           contains supporting doc image or not
        Method: -
        Open_ImgDownload_Channel     -               open imagedownloader to download gif/png/jpeg

        '''
    def __init__(self):
        self.activeparser = None
        self.eventType = ''
        self.datetimeparser = None
        self.hasImg = False

    def Open_ImgDownload_Channel(self):
        self.hasImg = True
        # initialize image downloader

    def Write_Over_End_Date(self):
        # self.datetimeparser =
        pass
