import hashlib
import json
import datetime
import time
from urllib import parse
import jsonpath
import scrapy

from wfpms.items import RateItem
from wfpms.items import TokenItem


class WfpmsPriceSpider(scrapy.Spider):
    name = 'wfpms_price'
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

        yield scrapy.FormRequest(url=url, formdata=data, headers=headers, callback=self.parse_price,
                                 dont_filter=True)

    def parse_price(self, response):
        content = json.loads(response.text)
        item = TokenItem()
        item['token'] = jsonpath.jsonpath(content, '$..Token')
        item['login_token'] = jsonpath.jsonpath(content, '$..LoginToken')
        today = datetime.date.today()
        tomorrow = (datetime.date.today() + datetime.timedelta(days=+1)).strftime('%Y-%m-%d')
        url = f'http://test.wfpms.com:9000/api/GetRoomRate?accbegin={today}&accend={tomorrow}&roomtypeid=0&roomratetype=0&login_chainid=440135&login_shift=A'
        # 解析url
        params = parse.parse_qs(parse.urlparse(url.lower()).query)
        # 排序
        # str_list = Sign.para_filter(params)
        data = Sign.create_link(params)
        data = Sign.create_link(params)
        dtime = int(time.time())
        # 拼接请求
        params_str = data + f'&_={dtime}&token={item["token"][0]}'
        # 生成签名
        sign = Sign.encryption(params_str)
        url = "http://test.wfpms.com:9000/api/GetRoomRate?" + f'accbegin={today}&accend={tomorrow}&roomtypeid=0&roomratetype=0&login_chainid=440135&login_shift=a&_={dtime}&token={item["login_token"][0]}' + f'&sign={sign}'
        yield scrapy.Request(url=url, callback=self.parse_get_price, dont_filter=True)

    def parse_get_price(self, response):
        content = json.loads(response.text)
        with open('price.json', 'w', encoding='utf-8') as fp:
            fp.write(json.dumps(content, ensure_ascii=False))
        price_dict = {}
        # 获取所有房型编号
        RoomTypeID_list = jsonpath.jsonpath(content, '$.Data..RoomTypeID')
        # 获取所有房型的名称
        RoomTypeName_list = jsonpath.jsonpath(content, '$.Data..RoomTypeName')
        # 获取所有房型的编码
        RoomTypeCode_list = jsonpath.jsonpath(content, '$.Data..RoomTypeCode')
        for i in range(len(RoomTypeID_list)):
            price_dict['RoomTypeID'] = RoomTypeID_list[i]
            price_dict['RoomTypeName'] = RoomTypeName_list[i]
            price_dict['RoomTypeCode'] = RoomTypeCode_list[i]
            today = datetime.date.today()
            tomorrow = (datetime.date.today() + datetime.timedelta(days=+1)).strftime('%Y-%m-%d')
            price_dict['Remarks'] = str(today) + 'to' + tomorrow
            # 获取对应房型的数据
            data = jsonpath.jsonpath(content, f'$.Data[?(@.RoomTypeID == {RoomTypeID_list[i]})]')
            # 获取房价
            price_dict['NewCube'] = jsonpath.jsonpath(data,
                                                      '$..RoomRateTypeItem[?(@.RoomRateTypeName == "新立方会员价")]..RoomRate')
            price_dict['SilverCube'] = jsonpath.jsonpath(data,
                                                         '$..RoomRateTypeItem[?(@.RoomRateTypeName == "银立方会员价")]..RoomRate')
            price_dict['GoldCube'] = jsonpath.jsonpath(data,
                                                       '$..RoomRateTypeItem[?(@.RoomRateTypeName == "金立方会员价")]..RoomRate')
            price_dict['PlatinumCube'] = jsonpath.jsonpath(data,
                                                           '$..RoomRateTypeItem[?(@.RoomRateTypeName == "铂金立方会员价")]..RoomRate')
            price_dict['BlackCube'] = jsonpath.jsonpath(data,
                                                        '$..RoomRateTypeItem[?(@.RoomRateTypeName == "黑立方会员价")]..RoomRate')
            price_dict['AllNight'] = jsonpath.jsonpath(data,
                                                       '$..RoomRateTypeItem[?(@.RoomRateTypeName == "整夜房")]..RoomRate')
            rate = RateItem(RoomTypeID=price_dict['RoomTypeID'], RoomTypeName=price_dict['RoomTypeName'],
                            RoomTypeCode=price_dict['RoomTypeCode'], NewCube=price_dict['NewCube'],
                            SilverCube=price_dict['SilverCube'], GoldCube=price_dict['GoldCube'],
                            PlatinumCube=price_dict['PlatinumCube'],
                            BlackCube=price_dict['BlackCube'], AllNight=price_dict['AllNight'],
                            Remarks=price_dict['Remarks'])
            yield rate


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
