# -*- coding: utf-8 -*-
import os
import time
import datetime
import json
import random
import base64
import socket

import arrow
import requests

from union_kakou import UnionKakou
from helper_sms import SMS
from helper_consul import ConsulAPI
from my_yaml import MyYAML
from my_logger import *


debug_logging(u'/home/logs/error.log')
logger = logging.getLogger('root')


class WatchDog(object):
    def __init__(self):
        self.ini = MyYAML('/home/my.yaml')
        self.my_ini = self.ini.get_ini()

        self.sms = None
        self.union = None
        self.con = ConsulAPI()
	
        self.kkdd_send_dict = {}

        self.send_time_step = 12           # 故障发送时间间隔 12小时
        self.mobiles = []                  # 发送手机号码
        self.useless_kkdd = set()          # 无效的卡口地点
        self.uuid = None                   # session id
        self.session_time = time.time()    # session生成时间戳
        self.ttl = self.my_ini['consul']['ttl']
        self.lock_name = self.my_ini['consul']['lock_name']

        self.check_interval = self.my_ini['check_interval']         # 查询时间间隔
        self.check_time = time.time() - self.check_interval         # 查询时间戳
        self.user_name = self.my_ini['sms']['user_name']            # 短信发送用户名

        self.local_ip = socket.gethostbyname(socket.gethostname())  # 本地IP

    def __del__(self):
        del self.my_ini

    def send_sms(self, content, mobiles):
        """发送短信"""
        try:
            if self.sms is None:
                return
            self.sms.sms_send(content, mobiles)
        except Exception as e:
            self.sms = None
            logger.error(e)

    def get_kkdd_list(self):
        """获取卡口地点列表"""
        now = arrow.now('PRC')
        kkdd_info_list = []
        c = self.union.get_control_unit()
        for i in c['items']:
            if i['unit_level'] == 1:
                kkdd_info_list.append(
                    {'control_unit_id': i['id'], 'name': i['name'], 'kkdd_list': []})

        for i in kkdd_info_list:
            t = self.union.get_traffic_crossing_info(i['control_unit_id'])
            for j in t['items']:
                item = {}
                item['crossing_id'] = j['id']
                item['crossing_index'] = j['kkdd_id']
                item['name'] = j['kkdd_name']
                item['direction_list'] = []
                i['kkdd_list'].append(item)
	
        for i in kkdd_info_list:
            for j in i['kkdd_list']:
                d = self.union.get_direction_info(j['crossing_id'])
                for k in d['items']:
                    item = {}
                    item['id'] = k['fxbh_id']
                    item['fxbh_code'] = k['fxbh_code']
                    item['direction_index'] = k['fxbh_id']
                    item['name'] = k['fxbh_name']
                    j['direction_list'].append(item)

        return kkdd_info_list

    def get_count(self, st ,et, unit_info):
        """根据时间范围统计数据量"""
        content = '联网平台-{0}\n'.format(unit_info['name'])
        
        for i in unit_info['kkdd_list']:
            # 跳过无效的卡口地点
            if str(i['crossing_index']) in self.useless_kkdd:
                continue
            for j in i['direction_list']:
                r = self.union.get_stat3(st, et, i['crossing_index'], j['direction_index'])
                logger.info('{0},{1},{2},{3}={4}'.format(st, et, i['crossing_index'], j['direction_index'], r['count']))
                if r['count'] == 0:
                    content += '[{0},{1}]\n'.format(i['name'], j['name'])

        if len(content) <= 14:
            return
        content += '超过1小时没数据'
        if self.kkdd_send_dict.get(unit_info['control_unit_id'], None) is None:
            self.kkdd_send_dict[unit_info['control_unit_id']] = {'send_content': '', 'send_time': arrow.now()}
        if len(content) == len(self.kkdd_send_dict[unit_info['control_unit_id']]['send_content']) and self.kkdd_send_dict[unit_info['control_unit_id']]['send_time'].replace(hours=self.send_time_step) > arrow.now():
            return
	
        self.send_sms(content, self.mobiles)
        self.kkdd_send_dict[unit_info['control_unit_id']]['send_content'] = content
        self.kkdd_send_dict[unit_info['control_unit_id']]['send_time'] = arrow.now()

    def stat_check(self):
        t = arrow.now('PRC')
        st = t.replace(hours=-1).format('YYYY-MM-DD HH:mm:ss')
        et = t.format('YYYY-MM-DD HH:mm:ss')
        for i in self.get_kkdd_list():
            self.get_count(st, et, i)

    def get_lock(self):
        """获取锁"""
        if self.uuid is None:
            self.uuid = self.con.put_session(self.ttl, self.lock_name)['ID']
            self.session_time = time.time()
            print(self.uuid)
        # 大于一定时间间隔则更新session
        t = time.time() - self.session_time
        if t > (self.ttl - 15):
            self.con.renew_session(self.uuid)
            self.session_time = time.time()
            print(self.uuid)
        l = self.con.get_lock(self.uuid, self.local_ip)
        print('l=%s'%l)
        # 返回 None 表示session过期
        if l == None:
            self.uuid = None
            return False
        return l

    def get_config(self):
        """获取配置信息"""
        mobiles = self.con.get_mobiles()[0]['Value']
        self.mobiles = json.loads(base64.b64decode(mobiles).decode())
        value = self.con.get_useless_kkdd()[0]['Value']
        self.useless_kkdd = set(json.loads(base64.b64decode(value).decode()))

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

    def run(self):
        while 1:
            if not self.get_lock():
                time.sleep(2)
                continue
            if self.sms is not None and self.union is not None and self.union.status:
                try:
                    if (time.time() - self.check_interval) > self.check_time:
                        self.get_config()
                        self.stat_check()
                        self.check_time = time.time()
                    time.sleep(5)
                except Exception as e:
                    logger.exception(e)
                    time.sleep(15)
            else:
                try:
                    if self.sms is None:
                        s = self.get_service('sms')
                        if s is None:
                            time.sleep(5)
                            continue
                        sms_ini = {
                            'host': s['host'],
                            'port': s['port'],
                            'user_name': self.user_name
                        }
                        self.sms = SMS(**sms_ini)
                    if self.union is None:
                        s = self.get_service('unionDataServer')
                        if s is None:
                            time.sleep(5)
                            continue
                        union_ini = {
                            'host': s['host'],
                            'port': s['port']
                        }
                        self.union = UnionKakou(**union_ini)
                        self.union.status = True
                    time.sleep(2)
                except Exception as e:
                    logger.exception(e)
                    time.sleep(15)


