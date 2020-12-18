# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
from scrapy.utils.project import get_project_settings


class WfpmsPipeline:
    def process_item(self, item, spider):
        return item


class MysqlPipeline:
    def __init__(self):
        settings = get_project_settings()
        self.host = settings['DB_HOST']
        self.port = settings['DB_PORT']
        self.user = settings['DB_USER']
        self.pwd = settings['DB_PASSWORD']
        self.name = settings['DB_NAME']
        self.charset = settings['DB_CHARSET']
        self.connect()

    def connect(self):
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.pwd, db=self.name,
                                    charset=self.charset)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        sql = f"insert into RoomRate values(0,{item['RoomTypeID']},\'{item['RoomTypeName']}\',\'{item['RoomTypeCode']}\',{item['NewCube'][0]},{item['SilverCube'][0]},{item['GoldCube'][0]},{item['PlatinumCube'][0]},{item['BlackCube'][0]},{item['AllNight'][0]},\'{item['Remarks']}\',\'{item['accbegin']}\',\'{item['accend']}\')"
        self.cursor.execute(sql)
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
