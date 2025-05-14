# Import necessary modules from Scrapy and other Python libraries
from scrapy.http import Request, FormRequest
from scrapy.spiders import Spider
import configparser
import json
from ..items import Com1SpiderItem
import re
import datetime


# Define the spider class
class Com1Spider(Spider):
    name = 'com_1'
    start_urls = ['http://www.com1.com.au/']

    def start_requests(self):
        url = "https://www.com1.com.au/customer/account/login"
        yield Request(url, callback=self.parse)

    def parse(self, response):
        value = response.xpath('.//*[@name="form_key"]/@value').extract_first()
        url = "https://www.com1.com.au/customer/account/loginPost/referer/aHR0cHM6Ly93d3cuY29tMS5jb20uYXUv/"

        config = configparser.ConfigParser()
        config.read('scrapy.cfg')
        Email = config['User_Detail']['Email']
        Password = config['User_Detail']['Password']

        data = {
            'form_key': value,
            'login[username]': Email,
            'login[password]': Password,
            'persistent_remember_me': 'on',
            'send': '',
        }

        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'https://www.com1.com.au',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://www.com1.com.au/customer/account/login/referer/aHR0cHM6Ly93d3cuY29tMS5jb20uYXUv/',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        yield FormRequest(url, method="POST", headers=headers, formdata=data, callback=self.main_catagory)

    def main_catagory(self, response):
        Main_catagory_urls = response.xpath('//*[@class="level-top "]/@href').extract()
        for Main_catagory_url in Main_catagory_urls:
            if Main_catagory_url == 'https://www.com1.com.au/hdds-ssds-1.html':
                yield Request(Main_catagory_url, callback=self.product_url)
            else:
                yield Request(Main_catagory_url + "?product_list_limit=all", callback=self.product_url)

    def product_url(self, response):
        if response.url == "https://www.com1.com.au/hdds-ssds-1.html":
            for cat_url in response.xpath(
                './/div[@class="filter-options-content"]/ol/li/a[contains(@href, "cat=")]/@href'
            ).extract():
                yield Request(cat_url, callback=self.product_url)
        else:
            product_urls = response.xpath('//*[@class="product-item-link"]/@href').extract()
            for product_url in product_urls:
                yield Request(product_url, callback=self.detail_page)

    def detail_page(self, response):
        item = Com1SpiderItem()

        item['Name'] = response.xpath('//*[@itemprop="name"]/text()').extract_first()
        item['SKU'] = response.xpath('//*[@itemprop="sku"]/text()').extract_first()
        item['Price'] = response.xpath(
            '//*[@data-price-type="finalPrice"]/span/text()'
        ).extract_first().replace("$", "").replace(",", "")

        Descriptions = response.xpath('//*[@itemprop="description"]//text()').extract()
        for Description in Descriptions:
            item['Description'] = Description

        Available_qty = response.xpath('//div[@class="control stock-availability"]/text()').extract_first()
        qty = Available_qty.replace("+", "").strip() if Available_qty else None
        if qty and '-' in qty:
            qty = qty.split('-')[-1]
        item['Available_qty'] = qty

        item['Brand'] = response.xpath('.//tr[th[contains(text(),"Brand")]]/td/text()').extract_first()
        item['Manufacturer_Part_Number'] = response.xpath(
            './/tr[th[contains(text(),"Manufacturer Part Number")]]/td/text()'
        ).extract_first()
        item['Product_page_link'] = response.xpath('//*[@itemprop="url"]/@content').extract_first()
        item['scrapedDate'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00')

        _weight = None
        _dimension = None
        specifications = dict()

        for tr in response.xpath(
            './/table[not(contains(@class, "additional-attributes"))]//tr[not(contains(@style, "display:none"))]'
        )[1:]:
            default_header = tr.xpath('./td[@colspan=2]/text()').extract_first()
            if default_header:
                continue

            key = tr.xpath('./td[1]/text()').extract_first()
            key = key.strip() if key else default_header
            value = tr.xpath('./td[2]//text()').extract()
            value = "\n".join([x.strip() for x in value if x.strip()])

            if key not in specifications:
                specifications[key] = []
            specifications[key].append(value.replace("\n", "").replace("\r", "").strip())

            if key and "dimension" in key.lower():
                _dimension = value
            if key and "weight" in key.lower():
                _weight = value

        for k, v in specifications.items():
            specifications[k] = "\n".join(v)

        specifications.pop(None, None)

        item['specification'] = json.dumps(specifications) if specifications else response.xpath(
            './/div[@id="description"]'
        ).extract_first()

        for k, v in item.items():
            if v:
                item[k] = v.strip()

        item['image'] = self.Image_page(response=response)

        weight = None
        if _weight:
            weight_match = re.search(r"([\d.]+[ g|g| gm|gm| kg|kg|K| K|lb| lb|LB| LB|IB| IB|ib| ib]{1,3})", _weight)
            if weight_match:
                weight = weight_match.group(1)

        _kgs = self.normalize_weight(weight)
        item["Weight"] = f"{_kgs} " if _kgs else None

        if _dimension:
            dimension_match = re.search(
                r"(([\d.]+.*?)[xX×*\s]+([\d.]+.*?)[xX×*\s]+([\d.]+.*?)?)", _dimension
            )
            dimension_unit_bck = re.search(r"(mm|cm|inch|in.|\"|INCH|MM|CM|'')", _dimension)
            Dimension = dimension_match.group(1) if dimension_match else None
            _unit = dimension_unit_bck.group(1) if dimension_unit_bck else None

            _cms = self.normalize_dimension(Dimension, _unit)
            item['Length'] = _cms.get('length')
            item['Width'] = _cms.get('width')
            item['Height'] = _cms.get('height')

        yield item

    def extract_measurements(self, value):
        v_match = re.findall(r"([\d][\d.]+)", value)
        if v_match:
            v_match = [float(i) for i in v_match]
            v_match.sort(reverse=True)
            return {k: v for k, v in zip(["length", "width", "height"], v_match)}
        else:
            return {}

    def normalize_dimension(self, dimension_value, _unit):
        if not dimension_value:
            return {}
        value = dimension_value.lower()
        dimension = self.extract_measurements(dimension_value)
        if "mm" in value:
            return {k: round(v / 10.0, 2) for k, v in dimension.items()}
        elif "cm" in value:
            return {k: round(v, 2) for k, v in dimension.items()}
        elif '"' in value or "inch" in value or "in." in value:
            return {k: round(v * 2.54, 2) for k, v in dimension.items()}
        elif _unit:
            return self.normalize_dimension(value + " " + _unit, None)
        return {}

    def normalize_weight(self, weight_value):
        if not weight_value:
            return None
        value = weight_value.lower()
        if "k" in value:
            weight = value.split("k")[0].strip()
            return round(float(weight), 2)
        elif "g" in value:
            weight = value.split("g")[0].strip()
            return round(float(weight) / 1000.0, 2)
        elif "b" in value:
            weight = value.replace("i", "l").split("l")[0].strip()
            return round(float(weight) * 0.4536, 2)

    def Image_page(self, response):
        images_data = response.xpath(
            '//script[@type="text/x-magento-init" and contains(text(), \'"thumb"\')]/text()'
        ).extract_first()
        image_json = json.loads(images_data)
        images = image_json['[data-gallery-role=gallery-placeholder]']['mage/gallery/gallery']['data']
        image_list = [
            {
                "main": 1 if image_info['isMain'] else 0,
                "image": image_info['full'],
                "thumb": image_info['thumb']
            }
            for image_info in images
        ]
        return json.dumps(image_list)
