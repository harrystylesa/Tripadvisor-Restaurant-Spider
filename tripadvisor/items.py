# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TripadvisorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CityItem(scrapy.Item):
    coll = scrapy.Field()
    cityID = scrapy.Field()
    city = scrapy.Field()
    province = scrapy.Field()
    totalres = scrapy.Field()
    totalrev = scrapy.Field()
    url = scrapy.Field()


class ResItem(scrapy.Item):
    coll = scrapy.Field()
    resID = scrapy.Field()
    chi = scrapy.Field()
    eng = scrapy.Field()
    rank = scrapy.Field()
    revnum = scrapy.Field()
    star = scrapy.Field()
    food = scrapy.Field()
    service = scrapy.Field()
    price = scrapy.Field()
    addr = scrapy.Field()
    phone = scrapy.Field()
    photos = scrapy.Field()
    type = scrapy.Field()
    special = scrapy.Field()
    meal = scrapy.Field()
    time = scrapy.Field()
    low = scrapy.Field()
    high = scrapy.Field()
    great = scrapy.Field()
    good = scrapy.Field()
    normal = scrapy.Field()
    worse = scrapy.Field()
    horrible = scrapy.Field()


class RevItem(scrapy.Item):
    coll = scrapy.Field()
    revID = scrapy.Field()
    resID = scrapy.Field()
    date = scrapy.Field()
    revdate = scrapy.Field()
    reviewer = scrapy.Field()
    star = scrapy.Field()
    thanks = scrapy.Field()
    content = scrapy.Field()
    title = scrapy.Field()
    isReply = scrapy.Field()
    reply = scrapy.Field()


class ReviewerItem(scrapy.Item):
    coll = scrapy.Field()
    reviewerID = scrapy.Field()
    reviewer = scrapy.Field()
    revrank = scrapy.Field()
    joindate = scrapy.Field()
    membership = scrapy.Field()
    tocity = scrapy.Field()
    photos = scrapy.Field()
    revs = scrapy.Field()


class UpItem(scrapy.Item):
    coll = scrapy.Field()
    list = scrapy.Field()
    resID = scrapy.Field()


class NearbyItem(scrapy.Item):
    ID = scrapy.Field()
    name = scrapy.Field()
    dis = scrapy.Field()
