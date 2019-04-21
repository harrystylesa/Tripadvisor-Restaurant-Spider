from scrapy.spiders import Spider, Request
import urllib.parse
import re
from ..items import CityItem, ReviewerItem, RevItem, ResItem, NearbyItem, UpItem
from ..utils import Util

class CitySpider(Spider):
    name = "city"
    allowed_domains = ["tripadvisor.cn"]
    start_urls = ["https://www.tripadvisor.cn/Restaurants-g294211-China.html"]
    i = 0
    base = "https://www.tripadvisor.cn"

    def parse(self, response):
        if self.i == 0:
            citys = response.xpath('//div[@class="geo_name"]/a/@href').extract()
        else:
            citys = response.xpath('//ul[@class="geoList"]/li/a/@href').extract()
        for city in citys:
            url = urllib.parse.urljoin(self.base, city)
            yield Request(url, callback=self.parse_city)
        self.i += 20
        if self.i <= 720:
            next_url = self.base + ("/Restaurants-g294211-oa%s-China.html" % self.i)
            yield Request(next_url, callback=self.parse)

    def parse_city(self, response):
        item = CityItem()
        item['coll'] = 'city'
        list = response.xpath('//span[@itemprop="title"]/text()').extract()
        id = re.search(r'g\d+', response.url).group(0)[1:]
        item['cityID'] = int(id)
        item['city'] = list[3]
        item['province'] = list[2]
        review = response.xpath('//div[@class="popIndex rebrand popIndexDefault"]/text()').extract_first().strip()
        review = Util.del_com(self, review)
        item['totalres'] = int(re.findall(r'\d+', review)[1])
        item['url'] = response.url
        print(item)
        yield item
