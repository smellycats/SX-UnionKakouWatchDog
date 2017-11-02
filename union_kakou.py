# -*- coding: utf-8 -*-
import json

import requests


class UnionKakou(object):
    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.headers = {'content-type': 'application/json'}

        self.status = False

    def get_maxid(self):
        """获取最大ID值"""
        url = 'http://{0}:{1}/alarm_maxid'.format(self.host, self.port)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def get_vehicle_by_id(self, _id):
        """根据ID范围获取车辆信息"""
        url = 'http://{0}:{1}/alarm/{2}'.format(
            self.host, self.port, _id)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def get_kkdd_by_id(self, kkdd_id):
        """根据车牌号码获取布控信息"""
        url = 'http://{0}:{1}/kkdd/{2}'.format(
            self.host, self.port, kkdd_id)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def get_stat(self, st, et, kkdd_id):
        """根据车牌号码获取布控信息"""
        url = 'http://{0}:{1}/stat/{2}/{3}/{4}'.format(
            self.host, self.port, st, et, kkdd_id)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def get_stat2(self, st, et, kkdd_id):
        """根据车牌号码获取布控信息"""
        url = 'http://{0}:{1}/stat2/{2}/{3}/{4}'.format(
            self.host, self.port, st, et, kkdd_id)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def get_stat3(self, st, et, kkdd=None, fxbh=None, timeout=15):
        """根据车牌号码获取布控信息"""
	# 键值字典
        params_dict = {'st': st, 'et': et}
        if kkdd is not None:
            params_dict['kkdd'] = kkdd
        if fxbh is not None:
            params_dict['fxbh'] = fxbh
        url = 'http://{0}:{1}/stat3'.format(self.host, self.port)
        try:
            r = requests.get(url, params=params_dict, timeout=timeout)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def get_traffic_crossing_info(self, unit_id=None):
        """获取卡点信息"""
        if unit_id is None:
            url = 'http://{0}:{1}/traffic_crossing_info'.format(
                self.host, self.port)
        else:
            url = 'http://{0}:{1}/traffic_crossing_info/{2}'.format(
                self.host, self.port, unit_id)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def get_control_unit(self):
        """获取县区信息"""
        url = 'http://{0}:{1}/control_unit'.format(self.host, self.port)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def get_direction_info(self, direction_id):
        """获取方向信息"""
        url = 'http://{0}:{1}/traffic_direction_info/{2}'.format(
            self.host, self.port, direction_id)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise


