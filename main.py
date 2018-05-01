# -*- coding: utf-8 -*-
import os
import time
import datetime
import json
import io
import sys

import arrow
import requests

from helper_union_kakou import UnionKakou
from helper_sms import SMS
from helper_consul import ConsulAPI
from my_yaml import MyYAML
from my_logger import *

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


debug_logging('/var/logs/error.log')
logger = logging.getLogger('root')


class WatchDog(object):
    def __init__(self):
        self.ini = MyYAML('/home/my.yaml')
        self.my_ini = self.ini.get_ini()

        self.con = ConsulAPI(path=self.my_ini['consul']['path'])
        self.sms = None
        self.kakou = None

        self.send_state = {}

        self.parent_id = self.my_ini['parent_id']

        logger.info('start')
        
    def __del__(self):
        pass

    def get_service(self, service):
        """获取服务信息"""
        s = self.con.get_service(service)
        if len(s) == 0:
            return None
        h = self.con.get_health(service)
        if len(h) == 0:
            return None
        service_status = {}
        for i in h:
            service_status[i['ServiceID']] = i['Status']
        for i in s:
            if service_status[i['ServiceID']] == 'passing':
                return {'host': i['ServiceAddress'], 'port': i['ServicePort']}
        return None

    def send_sms(self, content, mobiles):
        """发送短信"""
        try:
            self.sms.sms_send(content, mobiles, self.con.get_kv('sms_user'))
            info = 'mobiles={0}, content={1}'.format(mobiles, content)
            print(info)
            logger.info(info)
        except Exception as e:
            logger.error(e)

    def get_control_unit(self):
        control_unit_info = self.kakou.get_control_unit({'parent_id':self.parent_id})
        for i in control_unit_info['items']:
            send_time = self.send_state.get(i['id'], {'send_time': None})['send_time']
            if send_time is None:
                self.send_state[i['id']] = {
                    'send_time': arrow.now('PRC').replace(hours=-24),
                    'send_content': []
                }
            else:
                if arrow.now('PRC') > send_time.replace(hours=1):
                    self.get_stat(i)
                    logger.info(i)

    def get_stat(self, i):
        """流量统计"""
        t = arrow.now('PRC')
        et = t.strftime('%Y-%m-%d %H:%M:%S')
        st = t.replace(hours=-1).strftime('%Y-%m-%d %H:%M:%S')
        traffic_crossing_info = self.kakou.get_traffic_crossing_info({'control_unit_id':i['id']})
        miss_list = []
        for j in traffic_crossing_info['items']:
            # 过滤无效卡口
            if j['crossing_index'] in set(json.loads(self.con.get_kv('useless_kkdd'))):
                continue
            param = {
                'st': '"%s"' % st,
                'et': '"%s"' % et,
                'crossing_id': j['crossing_index']
            }
            count = self.kakou.get_stat(param)['count']
            if count == 0:
                miss_list.append(j['crossing_name'])
        # 故障卡口集合
        miss_set = set(miss_list) - set(self.send_state[i['id']]['send_content'])
        if len(miss_set) == 0:
            if arrow.now('PRC') < self.send_state[i['id']]['send_time'].replace(hours=12):
                self.send_state[i['id']]['send_content'] = miss_list
                return
        if len(miss_list) > 0:
            control_unit_info = self.kakou.get_control_unit_by_id(self.parent_id)
            content = '联网平台-{0}{1}\n'.format(i['name'], control_unit_info['name'])
            for k in miss_list:
                content += '[{0}]\n'.format(k)
            content += '超过1小时无数据'
        self.send_sms(content, json.loads(self.con.get_kv('mobiles')))
        self.send_state[i['id']]['send_time'] = t
        self.send_state[i['id']]['send_content'] = miss_list

    def run(self):
        while 1:
            if self.kakou is not None and self.kakou.status:
                try:
                    time.sleep(5)
                    self.get_control_unit()
                except Exception as e:
                    logger.exception(e)
                    time.sleep(15)
            else:
                try:
                    if self.kakou is None or not self.kakou.status:
                        s = self.get_service('kong')
                        if s is None:
                            time.sleep(5)
                            continue
                        param = {
                            'host': s['host'],
                            'port': s['port'],
                            'apikey': self.con.get_kv('apikey')
                        }
                        self.sms = SMS(**param)
                        self.sms.status = True
                        self.kakou = UnionKakou(**param)
                        self.kakou.status = True
                except Exception as e:
                    logger.exception(e)
                    time.sleep(1)
