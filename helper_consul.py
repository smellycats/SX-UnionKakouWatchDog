# -*- coding: utf-8 -*-
import json
import urllib

import requests


class ConsulAPI(object):
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 8500
        self.headers = {'content-type': 'application/json'}

        self.status = False

    def put_session(self, ttl=900, name=''):
        """创建session"""
        url = 'http://{0}:{1}/v1/session/create'.format(self.host, self.port)
        data = {
            "LockDelay": "15s",
            "Name": name,
            "Behavior": "release",
            "TTL": "{0}s".format(ttl)
        }
        try:
            r = requests.put(url, data=json.dumps(data))
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def del_session(self, uuid):
        """删除session"""
        url = 'http://{0}:{1}/v1/session/destroy/{2}'.format(
            self.host, self.port, uuid)
        try:
            r = requests.put(url)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def renew_session(self, uuid):
        """刷新session"""
        url = 'http://{0}:{1}/v1/session/renew/{2}'.format(
            self.host, self.port, uuid)
        try:
            r = requests.put(url)
            if r.status_code == 200:
                return json.loads(r.text)
            elif r.status_code == 404:
                return None
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def get_service(self, service):
        """获取服务"""
        url = 'http://{0}:{1}/v1/catalog/service/{2}'.format(
            self.host, self.port, service)
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

    def get_health(self, service):
        """获取服务健康信息"""
        url = 'http://{0}:{1}/v1/health/checks/{2}'.format(
            self.host, self.port, service)
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

    def get_lock(self, uuid, data):
        """获取锁成功返回True,失败返回False,session过期返回500错误"""
        url = 'http://{0}:{1}/v1/kv/union/watchdog/lock?acquire={2}'.format(
            self.host, self.port, uuid)
        try:
            r = requests.put(url, data=data)
            if r.status_code == 200:
                return json.loads(r.text)
            elif r.status_code == 500:
                return None
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def get_mobiles(self):
        """获取电话号码"""
        url = 'http://{0}:{1}/v1/kv/union/watchdog/mobiles'.format(
            self.host, self.port)
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

    def get_useless_kkdd(self):
        """获取卡口地点"""
        url = 'http://{0}:{1}/v1/kv/union/watchdog/useless_kkdd'.format(
            self.host, self.port)
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
