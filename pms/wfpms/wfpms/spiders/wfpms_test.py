import hashlib
import json
import time

from urllib import parse
import jsonpath
import scrapy

from wfpms.items import TokenItem

from wfpms.items import MemberItem

from wfpms.items import CouponItem


class WfpmsTestSpider(scrapy.Spider):
    name = 'wfpms_test'
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

    def parse_get_one_members(self, response):
        """获取新立方用户列表"""
        content = json.loads(response.text)
        item = TokenItem()
        item['token'] = jsonpath.jsonpath(content, '$..Token')
        item['login_token'] = jsonpath.jsonpath(content, '$..LoginToken')
        url = 'http://test.wfpms.com:9000/api/GetMemberList?thischain=0&vague=1&mebtype=1333&pageno=1&pagesize=12&login_chainid=440135&login_shift=A'
        # 解析url
        params = parse.parse_qs(parse.urlparse(url.lower()).query)
        # 排序
        data = Sign.create_link(params)
        dtime = int(time.time())
        # 拼接请求
        params_str = data + f'&_={dtime}&token={item["token"][0]}'
        # 生成签名
        sign = Sign.encryption(params_str)
        url = "http://test.wfpms.com:9000/api/GetMemberList?" + f'thischain=0&vague=1&mebtype=1333&pageno=1&pagesize=12&login_chainid=440135&login_shift=A&_={dtime}&token={item["login_token"][0]}' + f'&sign={sign}'
        yield scrapy.Request(url=url, meta={'item': item}, callback=self.parse_get_one_member, dont_filter=True)

    def parse_get_one_member(self, response):
        content = json.loads(response.text)
        item = response.meta['item']
        item['token'] = item['token']
        item['login_token'] = item['login_token']
        member_list = []
        for i in range(len(jsonpath.jsonpath(content, '$..MebName'))):
            member_item = MemberItem()
            member_item['name'] = str(jsonpath.jsonpath(content, '$..MebName')[i])
            member_item['memid'] = jsonpath.jsonpath(content, '$..MebID')[i]
            member_item['cardno'] = str(jsonpath.jsonpath(content, '$..CardNo')[i])
            member_list.append(member_item)
        print(member_list)
        with open('members.json', 'a', encoding='utf-8') as fp:
            fp.write(str(member_list))
        for member in member_list:
            url = f"http://test.wfpms.com:9000/api/GetDiscoups?mebid={member['memid']}&folioid=0&pageno=1&pagesize=11&login_chainid=440135&login_shift=A"
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
            url = "http://test.wfpms.com:9000/api/GetDiscoups?" + f'mebid={member["memid"]}&folioid=0&pageno=1&pagesize=11&login_chainid=440135&login_shift=A&_={dtime}&token={item["login_token"][0]}' + f'&sign={sign}'

            yield scrapy.Request(url=url, meta={'member_item': member_item, 'item': item},
                                 callback=self.parse_get_coupon,
                                 dont_filter=True)

    def parse_get_coupon(self, response):
        content = json.loads(response.text)
        member_item = parse.parse_qs(parse.urlparse(response.url).query)
        coupon = {}
        coupon['memid'] = member_item.get('mebid')
        coupon['DisDescription'] = jsonpath.jsonpath(content, '$..DisDescription')
        coupon['EndDate'] = jsonpath.jsonpath(content, '$..EndDate')
        coupon['State'] = jsonpath.jsonpath(content, '$..DataSet..State')
        with open("coupons.json", 'a', encoding='utf-8') as fp:
            fp.write(json.dumps(coupon, ensure_ascii=False))
        coupon = CouponItem(memid=coupon['memid'], DisDescription=coupon['DisDescription'])
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
