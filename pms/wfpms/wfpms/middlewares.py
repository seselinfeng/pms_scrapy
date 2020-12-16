# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import hashlib
from urllib import parse

from scrapy import signals, Request

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.http import HtmlResponse


class WfpmsCouponSpiderMiddleware:
    def process_request(self, request, spider):
        if spider.name == 'wfpms_coupon':
            # 获取爬取网站地址
            spider.driver.get(request.url)
            iframe = spider.driver.find_elemnt_by_xpath('')
            spider.driver.switch_to.frame(iframe)
            body = spider.driver.page_source
            return HtmlResponse(url=spider.driver.current_url, body=body, encoding='utf-8', request=request)
        else:
            return None

#
# class SignSpiderMiddleware:
#     def process_start_requests(self, start_requests, spider):
#         # Called with the start requests of the spider, and works
#         # similarly to the process_spider_output() method, except
#         # that it doesn’t have a response associated.
#
#         # Must return only requests (not items).
#         for r in start_requests:
#             yield r
#
#     def process_request(self, request, spider):
#         if spider.name == 'wfpms_test':
#             if "http://test.wfpms.com:9000/api/GetDiscoups" in request.url:
#                 # 解析url
#                 params = parse.parse_qs(parse.urlparse(request.url.lower()).query)
#                 print(params)
#                 # 排序
#                 str_list = Sign.para_filter(params)
#                 # 拼接请求
#                 params_str = Sign.create_link_string(str_list) + '&token=d5b9fedec0b3ad976842e83313cb2c75d616cafa'
#                 # 生成签名
#                 sign = Sign.encryption(
#                     "login_chainid=440135&login_shift=a&_=1607680643688&token=d5b9fedec0b3ad976842e83313cb2c75d616cafa")
#                 url = "http://test.wfpms.com:9000/api/GetMebType?" + 'login_chainid=440135&login_shift=A&_=1607680643688&token=145_4239_d197b0ac6cbafe4b680aa3227ddab0411111' + f'&sign={sign}'
#                 request.replace(url=url)
#                 print(f"request.url{request.url}")
#             return None
#         else:
#             return None



class WfpmsSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WfpmsDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
