from scrapy.spiders import Spider, Request
import re
from ..items import RevItem, ReviewerItem
from ..utils import Util


class RevSpider(Spider):
    name = 'review'
    allowed_domains = ['tripadvisor.cn']
    start_urls = []
    base = "https://www.tripadvisor.cn"
    member = "https://www.tripadvisor.cn/members/"
    badge = "https://www.tripadvisor.cn/members-badgecollection/"

    def __init__(self, filename=None):
        if filename:
            for line in open(filename, 'r').readlines():
                self.start_urls.append(format(line.rstrip()))

    def parse(self, response):
        ress = response.xpath('//a[@class="property_title"]/@href').extract()
        for res in ress:
            url = self.base + res
            # print(url)
            yield Request(url, callback=self.parse_rev)
        # 分页找出所有餐厅列表
        href = response.xpath('//a[@class="nav next rndBtn ui_button primary taLnk"]/@href').extract()[0]
        next_url = self.base + href
        next_url.replace(' ', '')
        yield Request(next_url, callback=self.parse)

    def parse_rev(self, response):
        revs = response.xpath('//div[@class="review-container"]')
        # urls = response.xpath('(//div[@class="quote isNew"]|//div[@class="quote"])/a/@href').extract()
        length = len(revs)
        for i in range(0, length):
            revitem = RevItem()
            rev = revs[i]
            revitem['coll'] = 'review'
            revitem['revID'] = int(rev.xpath('div/div/@data-reviewid').extract()[0])
            revitem['revdate'] = rev.xpath('div//span[@class="ratingDate"]/@title').extract()[0]
            dates = rev.xpath('div//div[@class="prw_rup prw_reviews_stay_date_hsx"]/text()').extract()
            if len(dates) > 0:
                revitem['date'] = dates[0]
            revitem['star'] = int(rev.xpath('div//div[@class="ui_column is-9"]/span/@class').extract()[0][-2:]) * 0.1
            revitem['content'] = re.sub(r'\s+', '',
                                        rev.xpath('div//div[@class="ui_column is-9"]//p/text()').extract()[0])
            revitem['reviewer'] = \
                rev.xpath('div//div[@class="ui_column is-2"]//div[@class="info_text"]/div/text()').extract()[0]

            reviewer_url = self.member + revitem['reviewer']
            yield Request(reviewer_url, callback=self.parse_reviewer)

            list = rev.xpath('div//div[@class="ui_column is-2"]//span[@class="badgetext"]/text()').extract()
            if len(list) > 1:
                revitem['thanks'] = int(list[1])
            else:
                revitem['thanks'] = 0
            revitem['title'] = rev.xpath('div//div[@class="ui_column is-9"]//span[@class="noQuotes"]/text()').extract()[
                0]
            if len(rev.xpath('div//div[@class="mgrRspnInline"]').extract()) > 0:
                revitem['isReply'] = True
                revitem['reply'] = re.sub(r'\s+', '', rev.xpath(
                    'div//div[@class="mgrRspnInline"]//p[@class="partial_entry"]/text()').extract()[0])
            else:
                revitem['isReply'] = False
            print(revitem)
            yield revitem

    def parse_reviewer(self, response):
        revieweritem = ReviewerItem()
        revieweritem['coll'] = 'reviewer'
        revieweritem['reviewerID'] = response.xpath('//div[@class="name"]/span/text()').extract_first()
        revieweritem['reviewer'] = revieweritem['reviewerID']
        rank = response.xpath('//div[@class="level tripcollectiveinfo"]/span/text()').extract()
        if len(rank) > 0:
            revieweritem['revrank'] = int(rank[0])
        else:
            revieweritem['revrank'] = 0
        revieweritem['joindate'] = response.xpath('//p[@class="since"]/text()').extract_first().strip()
        revs = response.xpath('//a[@name="reviews"]/text()').extract()
        if len(revs) > 0:
            revieweritem['revs'] = int(revs[0].split()[0])
        photos = response.xpath('//a[@name="photos"]/text()').extract()
        if len(photos) > 0:
            revieweritem['photos'] = int(Util.del_com(self, photos[0].strip()[0:-3]))
        badge_url = self.badge + revieweritem['reviewerID']
        yield Request(badge_url, callback=self.get_membership, meta={'item': revieweritem})
        print(revieweritem)

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
        print(item)
        yield item
