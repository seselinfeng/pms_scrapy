import hashlib
import json
import time
from urllib import parse

import jsonpath
import scrapy

from wfpms.items import TokenItem


class WfpmsGetmainstatuswithrevenueSpider(scrapy.Spider):
    name = 'wfpms_getmainstatuswithrevenue'
    allowed_domains = ['http://test.wfpms.com:9000']

    def start_requests(self):
        url = 'http://test.wfpms.com:9000/api/login?login_chainid=0&login_shift=&_=1607914726653&token=145_4239_f53e3fa079546f212ee8cc5f53da561&sign=7dea5054ad0c3e268195e84ebe1866b61c17c051'
        data = {
            'usercode': 'm3_admin',
            'password': '123123',
            'username': '',
            'fingerprint': '9844f81e1408f6ecb932137d33bed7cfdcf518a3',
        }
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN, zh;',
            'q': '0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'test.wfpms.com:9000',
            'Origin': 'http://test.wfpms.com:9000',
            'Referer': 'http://test.wfpms.com:9000/login.html'
        }

        yield scrapy.FormRequest(url=url, formdata=data, headers=headers,
                                 callback=self.parse_get_one_members)

    def parse_get_fangtai(self, response):
        """获取房态"""
        content = json.loads(response.text)
        item = TokenItem()
        item['token'] = jsonpath.jsonpath(content, '$..Token')
        item['login_token'] = jsonpath.jsonpath(content, '$..LoginToken')
        url = "http://test.wfpms.com:9000/api/GetMainStatusWithRevenue?login_chainid=440135&login_shift=A"
        # 解析url
        params = parse.parse_qs(parse.urlparse(url.lower()).query)
        # 排序
        str_list = Sign.para_filter(params)
        dtime = int(time.time())
        # 拼接请求
        params_str = Sign.create_link_string(str_list) + f'&_={dtime}&token={item["token"][0]}'
        # 生成签名
        sign = Sign.encryption(params_str)
        url = "http://test.wfpms.com:9000/api/GetMainStatusWithRevenue?" + f'login_chainid=440135&login_shift=A&_={dtime}&token={item["login_token"][0]}' + f'&sign={sign}'
        yield scrapy.Request(url=url, meta={'item': item}, callback=self.parse_get_coupon, dont_filter=True)


class Sign:
    @staticmethod
    def para_filter(kwargs):
        sign_dict = {}
        for key, value in kwargs.items():
            if str(kwargs[key]) != '' and str(key) != 'sign' and str(key) != 'sign_type' and str(
                    key) != 'token' and str(key) != '_':
                sign_dict[key] = kwargs[key]
        return sorted(sign_dict.items(), key=lambda x: x[0])

    @staticmethod
    def create_link_string(sign_dict):
        pre_str = ''
        for key in sign_dict:
            pre_str = pre_str + str(key[0]) + '=' + str(key[1][0] + '&')
        else:
            pre_str = pre_str.rstrip('&')
        return pre_str

    @staticmethod
    def encryption(s):
        m = hashlib.sha1()
        b = s.encode(encoding='utf-8')
        m.update(b)
        str_sha1 = m.hexdigest()
        return str_sha1.lower()

    @staticmethod
    def create_link(sign_dict):
        pre_str = ''
        for key in sign_dict:
            pre_str = pre_str + str(key) + '=' + str(sign_dict[key][0] + "&")
        else:
            pre_str = pre_str.rstrip('&')
        return pre_str
