# -*- coding: utf-8 -*-
import os
import time
import datetime
import json
#import io
#import sys

import arrow
import requests

from helper_union_kakou import UnionKakou
from helper_sms import SMS
from my_yaml import MyYAML
from my_logger import *

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


debug_logging('/logs/error.log')
logger = logging.getLogger('root')


class WatchDog(object):
    def __init__(self):
        self.ini = MyYAML('my.yaml')
        self.my_ini = self.ini.get_ini()

        self.sms = SMS(**dict(self.my_ini['sms']))
        self.kakou = UnionKakou(**dict(self.my_ini['union']))

        self.send_state = {}
        #print(dict(self.my_ini['tel'])['group1'])

        logger.info('start')
        
    def __del__(self):
        del self.my_ini

    def send_sms(self, content, mobiles):
        """发送短信"""
        try:
            self.sms.sms_send(content, mobiles)
            logger.info('mobiles={0}, content={1}'.format(mobiles, content))
        except Exception as e:
            logger.error(e)

    def get_data(self):
        control_unit_info = self.kakou.get_control_unit({'parent_id':1})
        for i in control_unit_info['items']:
            send_time = self.send_state.get(i['id'], {'send_time': None})['send_time']
            if send_time is None:
                self.get_stat(i)
            else:
                if arrow.now('PRC') > send_time.replace(hours=1):
                    self.get_stat(i)

    def get_stat(self, i):
        """流量统计"""
        t = arrow.now('PRC')
        et = t.strftime('%Y-%m-%d %H:%M:%S')
        st = t.replace(hours=-1).strftime('%Y-%m-%d %H:%M:%S')
        traffic_crossing_info = self.kakou.get_traffic_crossing_info({'control_unit_id':i['id']})
        crossing_info_list = []
        for j in traffic_crossing_info['items']:
            param = {
                'st': '"%s"' % st,
                'et': '"%s"' % et,
                'crossing_id': j['crossing_id']
            }
            count = self.kakou.get_stat(param)['count']
            if count == 0:
                crossing_info_list.append(j['crossing_name'])
        if len(crossing_info_list) != 0:
            content = '联网平台-{0}\n'.format(i['name'])
            for k in crossing_info_list:
                content += '[{0}]\n'.format(k)
            content += '超过1小时无数据'
            self.send_sms(content, dict(self.my_ini['tel'])['group1'])
        self.send_state[i['id']] = {
            'send_time': arrow.now('PRC')
        }

    def run(self):
        while 1:
            try:
                time.sleep(5)
                self.get_data()
            except Exception as e:
                logger.exception(e)
                time.sleep(15)

