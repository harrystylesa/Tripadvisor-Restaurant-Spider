from scrapy.spiders import Spider, Request
import re
from ..items import NearbyItem, UpItem


class NearbySpider(Spider):
    name = 'nearby'
    allowed_domains = ['tripadvisor.cn']
    start_urls = [
        "https://www.tripadvisor.cn/Restaurant_Review-g308272-d7227449-Reviews-Aura_Lounge_Jazz_Bar_The_Ritz_Carlton_Shanghai_Pudong-Shanghai.html"]
    base = "https://www.tripadvisor.cn"

    def __init__(self, filename=None):
        if filename:
            with open(filename, 'r') as f:
                self.start_urls = f.readlines()

    def parse(self, response):
        hrefs = response.xpath('//a[@class="taLnk seeAll"]/@href').extract()
        urls = []
        for href in hrefs:
            url = self.base + href
            urls.append(url)
            # print(url)
        yield Request(urls[0], callback=self.parse_nearbyHotel)
        for i in range(0, 7):
            if i == 0:
                yield Request(urls[1], callback=self.parse_nearbyRes)
            else:
                index = re.search(r'd\d+', urls[1]).span()[-1]
                next_url = urls[1][0:index] + "-oa%s" % (i * 30) + urls[1][index:]
                print(next_url)
                yield Request(next_url, callback=self.parse_nearbyRes)
        for i in range(0, 7):
            if i == 0:
                yield Request(urls[2], callback=self.parse_nearbySpot)
            else:
                index = re.search(r'd\d+', urls[2]).span()[-1]
                next_url = urls[2][0:index] + "-oa%s" % (i * 30) + urls[2][index:]
                print(next_url)
                yield Request(next_url, callback=self.parse_nearbySpot)

    def parse_nearbyHotel(self, response):
        item = UpItem()
        item['coll'] = 'nearbyhotel'
        # item['res'] = response.meta['res']
        hotels = response.xpath('//a[@class="property_title prominent "]/text()').extract()
        hrefs = response.xpath('//a[@class="property_title prominent "]/@href').extract()
        ids = []
        for href in hrefs:
            ids.append(int(re.search(r'd\d+', href).group(0)[1:]))
        diss = response.xpath('//b/text()').extract()
        list = []
        length = len(ids)
        for i in range(0, ids):
            hotelitem = NearbyItem()
            hotelitem['ID'] = ids[i]
            hotelitem['name'] = hotels[i]
            hotelitem['dis'] = float(diss[i][0:-2])
            list.append(hotelitem)
        item['list'] = list
        print(item)
        # yield item
        url = response.xpath('//a[@class="nav next taLnk ui_button primary"]/@href').extract()[0]
        next_url = self.base + url
        yield Request(next_url, self.parse_nearbyHotel)

    def parse_nearbyRes(self, response):
        item = UpItem()
        item['coll'] = 'nearbyres'
        # item['res'] = ''
        ress = response.xpath('//div[@class="location_name"]/a/text()').extract()
        hrefs = response.xpath('//div[@class="location_name"]/a/@href').extract()
        ids = []
        for href in hrefs:
            ids.append(int(re.search(r'd\d+', href).group(0)[1:]))
        diss = response.xpath('//b/text()').extract()
        list = []
        length = len(ids)
        for j in range(0, length):
            resitem = NearbyItem()
            resitem['ID'] = ids[j]
            resitem['name'] = ress[j]
            resitem['dis'] = float(diss[j][0:-2])
            list.append(resitem)
        item['list'] = list
        # print(item)
        yield item

    def parse_nearbySpot(self, response):
        item = UpItem()
        item['coll'] = 'nearbyspot'
        # item['res'] = ''
        spots = response.xpath('//div[@class="location_name"]/a/text()').extract()
        hrefs = response.xpath('//div[@class="location_name"]/a/@href').extract()
        ids = []
        for href in hrefs:
            ids.append(int(re.search(r'd\d+', href).group(0)[1:]))
        diss = response.xpath('//b/text()').extract()
        list = []
        length = len(ids)
        for j in range(0, length):
            spotitem = NearbyItem()
            spotitem['ID'] = ids[j]
            spotitem['name'] = spots[j]
            spotitem['dis'] = float(diss[j][0:-2])
            list.append(spotitem)
        item['list'] = list
        print(item)
        # yield item
