# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-
from pandas import *
from scrapy.spiders import Spider

rl_workingdir = r"output/"
abs_workingdir = r''

def export_linkinfo_in_file(filename):
    allrcrs_df = pandas.read_csv(filename, index_col='spider_oid')
    link_calc_rcrs = pandas.DataFrame({
        'loc_name': allrcrs_df['loc_name'],
        'ref_point': allrcrs_df['ref_point'],
        'ref_point_type': allrcrs_df['ref_point_type'],
        'spider_dist': allrcrs_df['spider_dist'].map(lambda x: '%2.1f' % x),
        'zdirection': allrcrs_df['spider_direction'],
    })
    _filename_purge = filename.replace(".csv", "")
    link_calc_rcrs.to_csv('input_join/%s.csv' % (_filename_purge + "_linkcalc"), sep=",",
                          line_terminator='\n')



def export_manualinput_rows(filename,command):
    if command.strip().upper()=='Y':
        _filename_purge = filename.replace(".csv", "")
        _pre_filename = 'input_join/%s.csv' % (_filename_purge + "_linkcalc")
        dataframe =  pandas.read_csv(_pre_filename,index_col='spider_oid')
        manually = dataframe[dataframe.ref_point == u"-1,-1"]  # need to manualinput -1,-1
        from scrapy.log import logger
        logger.info(manually)
        logger.info('manually input rows')

        #writeo ver link_clacrcrse

        others = dataframe[dataframe.ref_point <> u"-1,-1"]
        others.to_csv(_pre_filename, sep=",",
                          line_terminator='\n')
        return _pre_filename
    print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

def delta_input(filename, command, **kwargs):
    """

    :param filename: exporting file name calling file.
    :param command:  Y: Execute N: Next
    :param kwargs:   inventory file name, spider ,
    :return: generate 2 files"
            1.          offdata_[spidername].csv  data should be offline when spider crawling
            2.          purge lines that not valid at the moment,keep intact records in exportee file
    """
    _spider = kwargs.items()[0][-1] # spidername  text
    delta_updating_source = ['bjevent','fjHWApp','zjHWApp']
    accumulating_updating_source = ['shHWApp','shdHWApp']
    if command == 'Y':
        return file # log filename
    return None


class AdvancedParser(object):
    '''
        Attributes：-
        based on which spider
        _history                     -file          recorded data @social-navi platform #properties relied on spidername
        _link_infos                  -file          result csv converted from tools,
        current_path                 -str           processing path

        Method: - Properties
        export_overdue_rows          -file          return csv file
        setParser                    -obj           return attributes, define the parser
        export_manualinput_rows      -file          return rows that coordinates  == [-1,-1] that need to manually
        combine_linkinfo_file        -file          combine linkinfo with current spider result
    '''
    def __init__(self):
        self._history = 1
        pass

    def setParser(self,spider):
        return self._history
    def export_overdue_rows(self,file):
        pass

    def combine_linkinfo(self,file):
        pass
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
