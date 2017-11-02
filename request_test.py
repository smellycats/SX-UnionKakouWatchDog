# -*- coding: utf-8 -*-
import json
import time
import base64

from helper_consul import ConsulAPI


class ConsulTest(object):
    def __init__(self):
        self.con = ConsulAPI()

    def put_session(self):
        session = self.con.put_session()
        print(session)
        print(self.con.get_lock(uuid=session['ID']))
        print(self.con.get_lock('e7f8675a-e374-c041-6816-8a424fa77191'))

    def get_mobiles(self):
        print(type(self.con.get_mobiles()[0]))
        value = self.con.get_mobiles()[0]['Value']
        print(base64.b64decode(value))

    def get_useless_kkdd(self):
        value = self.con.get_useless_kkdd()[0]['Value']
        print(base64.b64decode(value))

    def renew_session(self):
        session = self.con.put_session()
        #print(session)
        #print(self.con.get_lock(uuid=session['ID']))
        for i in range(5):
            #time.sleep(20)
            print(self.con.renew_session('556f2c50-0fbd-aa87-8169-28abe25cc2c7'))


if __name__ == '__main__':
    ct = ConsulTest()
    #ct.put_session()
    #ct.get_mobiles()
    #ct.get_useless_kkdd()
    ct.renew_session()
