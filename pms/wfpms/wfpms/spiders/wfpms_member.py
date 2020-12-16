import hashlib
import json
from urllib import parse

import jsonpath as jsonpath
import scrapy

from wfpms.items import TokenItem


class WfpmsMemberPySpider(scrapy.Spider):
    name = 'wfpms_member'
    allowed_domains = ['http://test.wfpms.com:9000']

    def start_requests(self):
        url = 'http://test.wfpms.com:9000/api/login?login_chainid=0&login_shift=A&_=1607415178032&token=145_4239_f0153a8545217eae0b022befc1244f0&sign=c8fc9618a32e301199c3a0f7ce966cc8671d62f4'
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
                                 callback=self.parse_login)

    def parse_login(self, response):
        url = 'http://test.wfpms.com:9000/index.html?chainid=440135'
        yield scrapy.Request(url=url, callback=self.parse_login_token, dont_filter=True)

    def parse_login_token(self, response):
        url = 'http://test.wfpms.com:9000/api/login?login_chainid=0&login_shift=&_=1607682456849&token=145_4239_d197b0ac6cbafe4b680aa3227ddab04&sign=b269ceda8d1564e1a7d170661ae08e00996f25eb'
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

        yield scrapy.FormRequest(url=url, formdata=data, headers=headers, callback=self.parse_get_login_token,
                                 dont_filter=True)

    # def parse_get_login_token(self, response):
    #     content = json.loads(response.text)
    #     item = TokenItem()
    #     item['token'] = jsonpath.jsonpath(content, '$..Token')
    #     item['login_token'] = jsonpath.jsonpath(content, '$..LoginToken')
    #     print(item)
    #     url = "http://test.wfpms.com:9000/api/GetMebType?login_chainid=440135&login_shift=A&_=1607680643688"
    #     # 解析url
    #     params = parse.parse_qs(parse.urlparse(url.lower()).query)
    #     print(params)
    #     # 排序
    #     str_list = Sign.para_filter(params)
    #     # 拼接请求
    #     params_str = Sign.create_link_string(str_list) + f'&_=1607680643681&token={item["token"][0]}'
    #     print(params_str)
    #     # 生成签名
    #     sign = Sign.encryption(params_str)
    #     url = "http://test.wfpms.com:9000/api/GetMebType?" + f'login_chainid=440135&login_shift=A&_=1607680643681&token={item["login_token"][0]}' + f'&sign={sign}'
    #     yield scrapy.Request(url=url, meta={'item': item}, callback=self.parse_get_member, dont_filter=True)

    def parse_get_login_token(self, response):
        content = json.loads(response.text)
        item = TokenItem()
        item['token'] = jsonpath.jsonpath(content, '$..Token')
        item['login_token'] = jsonpath.jsonpath(content, '$..LoginToken')
        url = "http://test.wfpms.com:9000/api/GetMemberList?thischain=0&vague=1&qdata=&mebtype=1332%252C1333%252C1334%252C1341%252C1342&pageno=1&pagesize=12&login_chainid=440135&login_shift=A"
        # 解析url
        params = parse.parse_qs(parse.urlparse(url.lower()).query)
        print(params)
        # 排序
        str_list = Sign.para_filter(params)
        print(str_list)
        # 拼接请求
        params_str = Sign.create_link_string(str_list) + f'&_=1607680643688&token={item["token"][0]}'
        print(params_str)
        # 生成签名
        sign = Sign.encryption(params_str)
        url = "http://test.wfpms.com:9000/api/GetMemberList?" + f'thischain=0&vague=1&qdata=&mebtype=1332%252C1333%252C1334%252C1341%252C1342&pageno=1&pagesize=12&login_chainid=440135&login_shift=A&_=1607680643688&token={item["login_token"][0]}' + f'&sign={sign}'
        yield scrapy.Request(url=url, meta={'item': item}, callback=self.parse_get_member, dont_filter=True)

    def parse_get_member(self, response):
        content = response.text
        content = json.loads(content)
        with open('member.json', 'w', encoding='utf-8') as fp:
            fp.write(str(content))
        yield content


class Sign:
    @staticmethod
    def para_filter(kwargs):
        sign_dict = {}
        for key, value in kwargs.items():
            if str(kwargs[key]) != '' and str(key) != 'sign' and str(key) != 'sign_type' and str(
                    key) != 'token' and str(key) != '_':
                sign_dict[key] = kwargs[key]
        print(sign_dict)
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
        return str_sha1
