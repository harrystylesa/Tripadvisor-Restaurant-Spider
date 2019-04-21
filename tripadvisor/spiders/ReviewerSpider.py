from scrapy.spiders import Spider, Request
import urllib.parse
import re
from ..items import ReviewerItem

class ReviewerSpider(Spider):
    name = 'reviewer'
    allowed_domains = ['tripadvisor.cn']
    start_urls = ["https://www.tripadvisor.cn/members/Nomad25888605249"]
    base = "https://www.tripadvisor.cn"
    member = "https://www.tripadvisor.cn/members/"
    badge = "https://www.tripadvisor.cn/members-badgecollection/"

    def parse(self, response):
        item = ReviewerItem()
        item['coll'] = 'reviewer'
        item['reviewerID'] = \
        response.xpath('//*[@id="MODULES_MEMBER_CENTER"]/div[1]/div[1]/div[1]/div/div/span/text()').extract()[0]
        item['reviewer'] = item['reviewerID']
        rank = response.xpath('//div[@class="level tripcollectiveinfo"]/span/text()').extract()
        if len(rank) > 0:
            item['revrank'] = int(rank[0])
        else:
            item['rank'] = 0
        item['joindate'] = \
        response.xpath('//*[@id="MODULES_MEMBER_CENTER"]/div[1]/div[1]/div[2]/div[1]/p/text()').extract()[0].strip()
        item['revs'] = int(
            response.xpath('//*[@id="MODULES_MEMBER_CENTER"]/div[1]/div[2]/div/ul/li[1]/a/text()').extract()[0].split()[
                0])
        item['photos'] = int(
            response.xpath('//*[@id="MODULES_MEMBER_CENTER"]/div[1]/div[2]/div/ul/li[2]/a/text()').extract()[0][0:-4])

        badge_url = self.badge + item['reviewerID']
        yield Request(badge_url, callback=self.get_membership, meta={'item': item})
        # print(item)

    def get_membership(self, response):
        item = response.meta['item']
        # print(item)
        item['membership'] = response.xpath('//*[@id="BODYCON"]/div/div/ul/li/div/div/text()').extract()
        city_url = self.base + response.xpath('//*[@id="TravelMap"]/a/@href').extract()[0]
        yield Request(city_url, callback=self.get_tocitys, meta={'item': item})

    def get_tocitys(self, response):
        item = response.meta['item']
        item['tocity'] = int(
            response.xpath('//*[@id="MC_MODULES"]/div[2]/div[1]/div[1]/span/span/text()').extract()[0][1:-1])
        # print(item)
        yield item
