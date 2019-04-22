from scrapy.spiders import Spider, Request
import re
from ..items import ResItem, UpItem, NearbyItem
from ..utils import Util


class ResSpider(Spider):
    name = 'restaurants'
    allowed_domains = ['tripadvisor.cn']
    start_urls = ["https://www.tripadvisor.cn/Restaurants-g308272-Shanghai.html#EATERY_OVERVIEW_BOX"]
    base = "https://www.tripadvisor.cn"
    member = "https://www.tripadvisor.cn/members/"

    # driver = webdriver.Chrome()

    # script1 = """
    # function main(splash, args)
    #     assert(splash:go(splash.args.url))
    #     local get_dimensions = splash:jsfunc([[
    #         function () {
    #             var rect = document.getElementsByClassName('public-location-hours-LocationHours__bold--2oLr-')[0].getClientRects(0)[0];
    #             return {"x": rect.left, "y": rect.top}
    #         }
    #     ]])
    #     splash:set_viewport_full()
    #     splash:wait(10)
    #     local dimensions = get_dimensions()
    #     splash:mouse_click(dimensions.x, dimensions.y)
    #     splash:wait(10)
    #     return splash:html()
    # end
    # """
    #
    # script = """
    # function main(splash, args)
    #   splash.images_enabled = false
    #   assert(splash:go(args.url))
    #   assert(splash:wait(10))
    #   js = string.format("document.getElementsByClassName('public-location-hours-LocationHours__bold--2oLr-')[0].click()",args.page)
    #   splash:runjs(js)
    #   assert(splash:wait(10))
    #   return splash:html()
    # end
    # """
    #
    # script2 = """
    # function main(splash)
    #     splash:go(splash.args.url)
    #     splash:wait_for_resume("document.getElementsByClassName([[
    #               function main(splash) {
    #                    document.getElementsByClassName('public-location-hours-LocationHours__bold--2oLr-')[0].click()
    #                    splash.resume();
    #               }
    #     ]])
    # return splash:html()
    # """

    def __init__(self, filename=None):
        if filename:
            for line in open(filename, 'r').readlines():
                self.start_urls.append(format(line.rstrip()))

    def parse(self, response):
        if response.status == 403 or response.status == 500 or response.status == 10060 or response.status == 503:
            yield Request(response.url, callback=self.parse, dont_filter=True)
            return
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
        # 取出餐厅的具体内容
        if response.status == 403 or response.status == 500 or response.status == 10060 or response.status == 503:
            yield Request(response.url, callback=self.parse_res, dont_filter=True)
            return
        item = ResItem()
        item['coll'] = 'restaurants'
        ranks = response.xpath('//div[@class="popIndexContainer"]/div/span/b/span/text()').extract()
        if len(ranks) > 0:
            item['rank'] = int(Util.del_com(self, ranks[0]))
        item['resID'] = int(re.search(r'\d+', response.url).group(0))
        resID = item['resID']
        chis = response.xpath('//h1[@class="ui_header h1"]/text()').extract()
        if len(chis) > 0:
            item['chi'] = chis[0]
        start = re.search(r'Reviews-', response.url).span()[-1]
        stop = re.search(r'-\w+.html', response.url).span()[0]
        item['eng'] = response.url[start:stop].replace('_', ' ')
        revnum = ''
        revnums = response.xpath(
            '//a[@class="restaurants-detail-overview-cards-RatingsOverviewCard__ratingCount--DFxkG"]/text()').extract()
        if len(revnums) > 1:
            revnum = Util.del_com(self, revnums[0])
            item['revnum'] = int(re.search(r'\d+', revnum).group(0))
        stars = response.xpath(
            '//span[@class="restaurants-detail-overview-cards-RatingsOverviewCard__overallRating--nohTl"]/text()').extract()
        if len(stars) > 0:
            item['star'] = float(stars[0])
        stars = response.xpath(
            '//span[@class="restaurants-detail-overview-cards-RatingsOverviewCard__ratingBubbles--1kQYC"]/span/@class').extract()
        length = len(stars)
        for i in range(0, length):
            stars[i] = int(re.search(r'\d+', stars[i]).group(0)) * 0.1
            # print(stars[i])
        if length > 2:
            item['food'] = stars[0]
            item['service'] = stars[1]
            item['price'] = stars[2]
        misc = response.xpath(
            '//span[@class="restaurants-detail-overview-cards-LocationOverviewCard__detailLinkText--co3ei"]/text()').extract()
        item['addr'] = misc[0]
        item['phone'] = misc[-1]
        photos = response.xpath('//span[@class="details"]/text()').extract()
        if len(photos) > 1:
            item['photos'] = int(re.search(r'\d+', photos[0]).group(0))
        det = response.xpath(
            '//div[@class="restaurants-detail-overview-cards-DetailsSectionOverviewCard__tagText--1OH6h"]/text()').extract()
        if len(det) > 2:
            item['type'] = det[1]
            item['special'] = det[2]
        list = response.xpath(
            '//span[@class="public-location-hours-LocationHours__hoursOpenerText--42y6t"]/span/text()').extract()
        if len(list) > 0:
            item['time'] = list[-1]
        marks = response.xpath('//span[@class="row_num  is-shown-at-tablet"]/text()').extract()
        if len(marks) > 4:
            item['great'] = int(Util.del_com(self, marks[0]))
            item['good'] = int(Util.del_com(self, marks[1]))
            item['normal'] = int(Util.del_com(self, marks[2]))
            item['worse'] = int(Util.del_com(self, marks[3]))
            item['horrible'] = int(Util.del_com(self, marks[4]))

        print(item)
        yield item

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

    def parse_nearbyHotel(self, response):
        if response.status == 403 or response.status == 500 or response.status == 10060 or response.status == 503:
            yield Request(response.url, callback=self.parse_nearbyHotel, dont_filter=True)
            return
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
        if response.status == 403 or response.status == 500 or response.status == 10060 or response.status == 503:
            yield Request(response.url, callback=self.parse_nearbyRes, dont_filter=True)
            return
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
        if response.status == 403 or response.status == 500 or response.status == 10060 or response.status == 503:
            yield Request(response.url, callback=self.parse_nearbySpot, dont_filter=True)
            return
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
