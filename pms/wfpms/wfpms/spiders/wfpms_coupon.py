import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.linkextractors import LinkExtractor


class WfpmsCouponSpider(scrapy.Spider):
    name = 'wfpms_coupon'
    allowed_domains = ['http://test.wfpms.com:9000']
    start_urls = ['http://http://test.wfpms.com:9000/']

    def __init__(self):
        super().__init__()
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome('chromedriver', options=options)

    def parse(self, response):
        le = LinkExtractor()
        links = le.extract_links(response)
        for link in links:
            yield {
                'file_urls': [link.url]
            }

    def close(spider, reason):
        spider.driver.quit()  # 关闭浏览器
