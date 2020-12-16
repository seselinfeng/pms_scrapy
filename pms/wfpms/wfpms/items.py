# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RateItem(scrapy.Item):
    # define the fields for your item here like:
    RoomTypeID = scrapy.Field()
    RoomTypeName = scrapy.Field()
    RoomTypeCode = scrapy.Field()
    NewCube = scrapy.Field()
    SilverCube = scrapy.Field()
    GoldCube = scrapy.Field()
    PlatinumCube = scrapy.Field()
    BlackCube = scrapy.Field()
    AllNight = scrapy.Field()
    Remarks = scrapy.Field()


class TokenItem(scrapy.Item):
    token = scrapy.Field()
    login_token = scrapy.Field()


class MemberItem(scrapy.Item):
    name = scrapy.Field()
    memid = scrapy.Field()
    cardno = scrapy.Field()


class CouponItem(scrapy.Item):
    memid = scrapy.Field()
    DisDescription = scrapy.Field()
