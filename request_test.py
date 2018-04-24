# -*- coding: utf-8 -*-
import json

from helper_kakou import Kakou
from helper_sms import SMS
from ini_conf import MyIni


class KakouTest(object):
    def __init__(self):
        self.my_ini = MyIni()
        self.kakou = Kakou(**self.my_ini.get_kakou())

    def get_maxid(self):
        print self.kakou.get_maxid()

    def get_vehicle_by_id(self):
        print self.kakou.get_vehicle_by_id(140)

    def get_kkdd_by_id(self):
        print self.kakou.get_kkdd_by_id(441302001)

    def get_stat(self):
	print self.kakou.get_stat('2016-11-17 00:00:00', '2016-11-17 01:00:00', '441302000')


class SMSTest(object):
    def __init__(self):
        #self.my_ini = MyIni()
        self.sms = SMS(**{'host': '10.47.223.147', 'port': 8090, 'user': 'union_kakou', 'pwd': 'unionkakousms'})

    def get_sms(self):
        content = u'死消磨'
        mobiles = ['13556222300']
        print self.sms.sms_send(content, mobiles)


if __name__ == '__main__':
    #st = SMSTest()
    #st.get_sms()
    kt = KakouTest()
    kt.get_stat()
