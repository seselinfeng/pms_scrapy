import hashlib
import json
import time
from urllib import parse

import jsonpath
import scrapy

from wfpms.items import TokenItem, MemberItem, CouponItem


class WfpmsProTestSpider(scrapy.Spider):
    name = 'wfpms_pro_test'
    allowed_domains = ['http://pms.wfpms.com/']

    def start_requests(self):
        url = 'http://pms.wfpms.com/api/login?login_chainid=0&login_shift=&_=1608010113790&token=145_8962_e0e5517cad7c022bb538e9c49185827&sign=d714868ac0068dfd218d833733edc0680d1a2877'
        data = {
            'usercode': 'm3_test1',
            'password': 'tigertest123456',
            'username': '',
            'fingerprint': '9844f81e1408f6ecb932137d33bed7cfdcf518a3',
        }
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN, zh;',
            'q': '0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'pms.wfpms.com',
            'Origin': 'http://pms.wfpms.com',
            'Referer': 'http://pms.wfpms.com/login.html'
        }

        yield scrapy.FormRequest(url=url, formdata=data, headers=headers,
                                 callback=self.parse_get_one_members)

    def parse_get_one_members(self, response):
        """获取新立方用户列表"""
        content = json.loads(response.text)
        item = TokenItem()
        item['token'] = jsonpath.jsonpath(content, '$..Token')
        item['login_token'] = jsonpath.jsonpath(content, '$..LoginToken')
        for i in range(1, 52):
            url = f'http://pms.wfpms.com/api/GetMemberList?thischain=0&vague=1&mebtype=1361&pageno={i}&pagesize=100&login_chainid=440135&login_shift=A'
            # 解析url
            params = parse.parse_qs(parse.urlparse(url.lower()).query)
            # 排序
            data = Sign.create_link(params)
            dtime = int(time.time())
            # 拼接请求
            params_str = data + f'&_={dtime}&token={item["token"][0]}'
            # 生成签名
            sign = Sign.encryption(params_str)
            url = "http://pms.wfpms.com/api/GetMemberList?" + f'thischain=0&vague=1&mebtype=1361&pageno={i}&pagesize=100&login_chainid=440135&login_shift=A&_={dtime}&token={item["login_token"][0]}' + f'&sign={sign}'
            yield scrapy.Request(url=url, meta={'item': item}, callback=self.parse_get_one_member, dont_filter=True)

    def parse_get_one_member(self, response):
        content = json.loads(response.text)
        item = response.meta['item']
        item['token'] = item['token']
        item['login_token'] = item['login_token']
        member_list = []
        if jsonpath.jsonpath(content, '$..MebName'):
            for i in range(len(jsonpath.jsonpath(content, '$..MebName'))):
                member_item = MemberItem()
                member_item['name'] = str(jsonpath.jsonpath(content, '$..MebName')[i])
                member_item['memid'] = jsonpath.jsonpath(content, '$..MebID')[i]
                member_item['cardno'] = str(jsonpath.jsonpath(content, '$..CardNo')[i])
                member_list.append(member_item)
            with open('members.json', 'a', encoding='utf-8') as fp:
                fp.write(str(member_list)+",\n")
        for member in member_list:
            url = f"http://pms.wfpms.com/api/GetDiscoups?mebid={member['memid']}&folioid=0&pageno=1&pagesize=11&login_chainid=440135&login_shift=A"
            # 解析url
            params = parse.parse_qs(parse.urlparse(url.lower()).query)
            # 排序
            # str_list = Sign.para_filter(params)
            data = Sign.create_link(params)
            dtime = int(time.time())
            # 拼接请求
            params_str = data + f'&_={dtime}&token={item["token"][0]}'
            # 生成签名
            sign = Sign.encryption(params_str)
            url = "http://pms.wfpms.com/api/GetDiscoups?" + f'mebid={member["memid"]}&folioid=0&pageno=1&pagesize=11&login_chainid=440135&login_shift=A&_={dtime}&token={item["login_token"][0]}' + f'&sign={sign}'

            yield scrapy.Request(url=url, meta={'member_item': member_item, 'item': item},
                                 callback=self.parse_get_coupon,
                                 dont_filter=True)

    def parse_get_coupon(self, response):
        content = json.loads(response.text)
        item = response.meta['item']
        item['token'] = item['token']
        item['login_token'] = item['login_token']
        member_item = parse.parse_qs(parse.urlparse(response.url).query)
        coupon = {}
        coupon['memid'] = member_item.get('mebid')
        if jsonpath.jsonpath(content, '$..DisDescription'):
            coupon['DisDescription'] = jsonpath.jsonpath(content, '$..DisDescription')
            coupon['EndDate'] = jsonpath.jsonpath(content, '$..EndDate')
            coupon['State'] = jsonpath.jsonpath(content, '$..DataSet..State')
            with open("coupons.json", 'a', encoding='utf-8') as fp:
                fp.write(json.dumps(coupon, ensure_ascii=False)+",\n")
            coupon = CouponItem(memid=coupon['memid'], DisDescription=coupon['DisDescription'])
            yield coupon
        else:
            coupon = CouponItem(memid=coupon['memid'], DisDescription='此用户暂无体验券')
            yield coupon


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
