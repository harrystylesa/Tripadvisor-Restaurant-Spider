from scrapy.spiders import Spider, Request
import re
from ..items import NearbyItem, UpItem


class NearbySpider(Spider):
    name = 'nearby'
    allowed_domains = ['tripadvisor.cn']
    start_urls = ["https://www.tripadvisor.cn/Restaurants-g308272-Shanghai.html"]
    base = "https://www.tripadvisor.cn"
    member = "https://www.tripadvisor.cn/members/"

    def __init__(self, filename=None):
        if filename:
            for line in open(filename, 'r').readlines():
                self.start_urls.append(format(line.rstrip()))

    def parse(self, response):
        # 取出每个餐厅的链接
        ress = response.xpath('//a[@class="property_title"]/@href').extract()
        for res in ress:
            url = self.base + res
            url.replace(' ', '')
            # print(url)
            yield Request(url, callback=self.parse_res)
        # 分页找出所有餐厅列表
        hrefs = response.xpath('//a[@class="nav next rndBtn ui_button primary taLnk"]/@href').extract()
        if len(hrefs) > 0:
            href = hrefs[0]
        next_url = self.base + href
        next_url.replace(' ', '')
        # print(next_url)
        yield Request(next_url, callback=self.parse)

    def parse_res(self, response):
        resID = int(re.search(r'd\d+', response.url).group(0)[1:])
        # 附近酒店
        url = response.url
        # print(response.url)
        hotelurl = response.url
        hotelurl = hotelurl.replace('Restaurant_Review', 'HotelsNear')
        hotelurl = hotelurl.replace('-Reviews-', '-')

        # print(url)
        yield Request(hotelurl, callback=self.parse_nearbyHotel, meta={'resID': resID})

        # 附近餐厅
        resurl = url
        resurl = resurl.replace('Restaurant_Review', 'RestaurantsNear')
        resurl = resurl.replace('-Reviews-', '-')
        for i in range(0, 7):
            if i == 0:
                yield Request(resurl, callback=self.parse_nearbyRes, meta={'resID': resID})
            else:
                index = re.search(r'd\d+', resurl).span()[-1]
                next_url = resurl[0:index] + "-oa%s" % (i * 30) + resurl[index:]
                print(next_url)
                yield Request(next_url, callback=self.parse_nearbyRes, meta={'resID': resID})

        # 附近景点
        spoturl = url
        spoturl = spoturl.replace('Restaurant_Review', 'AttractionsNear')
        spoturl = spoturl.replace('-Reviews-', '-')
        for i in range(0, 7):
            if i == 0:
                yield Request(spoturl, callback=self.parse_nearbySpot, meta={'resID': resID})
            else:
                index = re.search(r'd\d+', spoturl).span()[-1]
                next_url = spoturl[0:index] + "-oa%s" % (i * 30) + spoturl[index:]
                print(next_url)
                yield Request(next_url, callback=self.parse_nearbySpot, meta={'resID': resID})

        # hrefs = response.xpath('//a[@class="taLnk seeAll"]/@href').extract()
        # urls = []
        # for href in hrefs:
        #     url = self.base + href
        #     urls.append(url)
        #     # print(url)
        # yield Request(urls[0], callback=self.parse_nearbyHotel)
        # for i in range(0, 7):
        #     if i == 0:
        #         yield Request(urls[1], callback=self.parse_nearbyRes)
        #     else:
        #         index = re.search(r'd\d+', urls[1]).span()[-1]
        #         next_url = urls[1][0:index] + "-oa%s" % (i * 30) + urls[1][index:]
        #         print(next_url)
        #         yield Request(next_url, callback=self.parse_nearbyRes)
        # for i in range(0, 7):
        #     if i == 0:
        #         yield Request(urls[2], callback=self.parse_nearbySpot)
        #     else:
        #         index = re.search(r'd\d+', urls[2]).span()[-1]
        #         next_url = urls[2][0:index] + "-oa%s" % (i * 30) + urls[2][index:]
        #         print(next_url)
        #         yield Request(next_url, callback=self.parse_nearbySpot)

    def parse_nearbyHotel(self, response):
        item = UpItem()
        item['coll'] = 'nearbyhotels'
        item['resID'] = int(re.search(r'd\d+', response.url).group(0)[1:])
        hotels = response.xpath('//a[@class="property_title prominent "]/text()').extract()
        hrefs = response.xpath('//a[@class="property_title prominent "]/@href').extract()
        ids = []
        for href in hrefs:
            ids.append(int(re.search(r'd\d+', href).group(0)[1:]))
        diss = response.xpath('//b/text()').extract()
        list = []
        length = len(ids)
        for i in range(0, length):
            hotelitem = NearbyItem()
            hotelitem['ID'] = ids[i]
            hotelitem['name'] = hotels[i]
            hotelitem['dis'] = float(diss[i][0:-2])
            list.append(hotelitem)
        item['list'] = list
        print(item)
        yield item
        url = response.xpath('//a[@class="nav next taLnk ui_button primary"]/@href').extract()[0]
        next_url = self.base + url
        yield Request(next_url, self.parse_nearbyHotel)

    def parse_nearbyRes(self, response):
        item = UpItem()
        item['coll'] = 'nearbyress'
        item['resID'] = int(re.search(r'd\d+', response.url).group(0)[1:])
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
        print(item)
        yield item

    def parse_nearbySpot(self, response):
        item = UpItem()
        item['coll'] = 'nearbyspots'
        item['resID'] = int(re.search(r'd\d+', response.url).group(0)[1:])
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
        yield item
