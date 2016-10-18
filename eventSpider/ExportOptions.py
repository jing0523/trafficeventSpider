# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-
from pandas import *
from scrapy.spiders import Spider

rl_workingdir = r"output/"
abs_workingdir = r''

def export_linkinfo_in_file(filename, **kwargs):
    """
    \+++++++++++++++Remove fields for link info calculating+++++++++++++++++
    :param filename:file that spider crawled and located in output dir
    :return: file in output/input_join for moving into conversion-tool on server
    """
    _spider = kwargs.items()[0][-1]
    _src_withno_coords = ['zjHWApp','hbHWApp']
    if _spider in _src_withno_coords:
        return
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
    do what pandas_parc.py do
    :param filename: exporting file name calling file.
    :param command:  Y: Execute N: Next
    :param kwargs:   inventory file name, spider ,
    :return: generate 2 files"
            1.          offdata_[spidername].csv  data should be offline when spider crawling
            2.          purge lines no longer valid at the moment,keep intact records in exportee file
    """
    _spider = kwargs.items()[0][-1] # spidername  text

    _filename_purge = filename.replace(".csv", "")
    delta_updating_source = ['bjevent','fjHWApp','zjHWApp','bjevent2','bjevent','shdHWApp','chqevent1']
    accumulating_updating_source = ['shHWApp']

    if command.strip().upper() == 'Y':
        if _spider in delta_updating_source:
            df0 = pandas.read_csv(filename,index_col='spider_oid')
            df1 = pandas.read_csv("data_inventory/inv_%s.csv" % _spider, index_col='spider_oid')

            temp = df1.join(df0, how='left', lsuffix='_left', rsuffix='_right')
            offdata = temp[isnull(temp.loc_name) & isnull(temp.deleted) & isnull(temp.ref_point)]

            manualrevert = pandas.DataFrame({'EVENT_TO_REMOVE': offdata['eventid']})
            manualrevert.to_csv('data_inventory/offdata_%s.csv' % _spider, sep=",", line_terminator='\n')

        elif _spider in accumulating_updating_source:
            return filename
        return filename
    return None


def combine_linkinfo(filename,commmand,**kwargs):
    """

    :param filename: at ? moment  pipeline's output
    :param commmand:
    :param kwargs:
    :return:
    """
    _src_with_coords = []
    _src_withno_coords = ['zjHWApp','hbHWApp']
    _spider = kwargs.items()[0][-1]

    if commmand.strip().upper() == 'Y':
        if _spider in _src_with_coords:
            print "process A"
        elif _spider in _src_withno_coords:
            df_spider = pandas.read_csv(filename, index_col='spider_oid')
            df_linkout = pandas.DataFrame({
                'id': df_spider['spider_oid'],
                'link_info': '',
            })
            temp = pandas.merge(left=df_spider, right=df_linkout, left_on=['spider_oid'], right_on=['id'], suffixes=['_L', '_R'])
            temp.to_csv('eventSpider/input_join/%s.csv' % (filename + "_merge"), sep=",",
                          line_terminator='\n')
            export_result = temp.copy()
            export_result = export_result.drop(export_result.columns[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                                                                      10, 11, 29,
                                                                      30,
                                                                      32
                                                                      ]], axis=1)

            rows_cnt = len(export_result.index)
            for i in range(0, rows_cnt + 1, 15):
                blockrows = export_result.iloc[i:i + 15, ]
                blockrows.to_csv(("eventSpider/input_join/%s_p" + str(i / 15) + ".csv")  % filename
                ,sep = ",",
                line_terminator = '\n')
        else:
            print 'process C'
        return file  # log filename
    return None



class AdvancedParser(object):
    '''
        Attributes：-
        based on which spider
        _history                     -file          recorded data @social-navi platform #properties relied on spidername
        _link_infos                  -strnig        result csv files' name converted from tools,
        current_path                 -str           processing path

        Method: - Properties
        export_overdue_rows          -file          return csv file
        setParser                    -obj           return attributes, define the parser
        export_manualinput_rows      -file          return rows that coordinates  == [-1,-1] that need to manually
        combine_linkinfo_file        -file          combine linkinfo with current spider result
    '''
    def __init__(self):
        self._history = 1
        self._have_coords = True
        pass

    def setParser(self,spider):
        return self._history
    def export_overdue_rows(self,file):
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
