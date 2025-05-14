import scrapy
import json
import re
from scrapy.http import Request, FormRequest
from cleantext import clean


class AscolorSpider(scrapy.Spider):
    name = 'ascolor'

    # Define custom settings, particularly the pipeline used to process items
    custom_settings = {
        'ITEM_PIPELINES': {
            'ascolorspider.pipelines.AscolorspiderPipeline': 300,
        }
    }

    def start_requests(self):
        # Send a POST request to log into the website
        url = "https://www.ascolour.co.nz/login.php?action=check_login"
        payload = {
            'login_email': 'xyz',
            'login_pass': 'pass123'
        }
        headers = {
            'authority': 'www.ascolour.co.nz',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://www.ascolour.co.nz',
            'referer': 'https://www.ascolour.co.nz/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        }
        yield FormRequest(url, method="POST", formdata=payload, headers=headers, callback=self.after_login)

    def after_login(self, response):
        # After successful login, request the product sitemap
        sitemap_url = 'https://www.ascolour.co.nz/xmlsitemap.php?type=products&page=1'
        yield Request(sitemap_url, callback=self.after_sitemap)

    def after_sitemap(self, response):
        # Extract all product URLs from the sitemap using regex
        pattern = r'<loc>(.*?)<\/loc>'
        urls = re.findall(pattern, response.text)
        urls = [url.strip() for url in urls]

        # For each product URL, call the detail page parser
        for url in urls:
            yield Request(url, callback=self.detail_page)

    def data_extractor(self, data, code):
        # Helper function to extract price or tier from a string
        spl_tier = data.split('_')
        if code == 'p':
            return [spl_tier[0]]
        else:
            return [spl_tier[1]]

    def detail_page(self, response):
        item = {}

        # Extract product SKU
        sku = response.xpath('.//*[@data-product-sku]/text()').extract_first()
        if sku:
            item['code'] = sku

        # Extract product name
        name = response.xpath('.//*[@itemprop="name"]/text()').extract_first()
        if name:
            item['Name'] = name

        item['country'] = 'nz'

        # Extract product description
        product_detail = response.xpath('//*[@class="description"]//*[@class="content"]/p//text()').extract()
        if product_detail:
            item['description'] = "".join(product_detail)

        # Initialize additional fields
        item['dimensions'] = ""
        item['packaging'] = []
        item['brand'] = ""
        item['brandlogo'] = ""
        item['supplier_link'] = response.url

        # Extract main image
        item['Images'] = []
        main_image_dic = {}
        main_image = response.xpath(""".//li/img[@lazyload='title="MAIN"']/@src""").extract_first()
        if main_image:
            main_image_spl = main_image.split('/')[-1]
            name = main_image_spl.replace('?c=1', '')
            main_image_dic['name'] = name
            main_image_dic['url'] = main_image
            main_image_dic['type'] = 'feature'
            item['Images'].append(main_image_dic)

        # Extract embedded JSON for colors and images
        colourjson = response.xpath(
            '//script[contains(text()," window.stencilBootstrap")]/text()'
        ).re_first(r'window\.stencilBootstrap\(\"product\", \"(.*)\"\).load')
        colourjson = colourjson.replace('\\"', '"').replace('\\\\"', "'")
        jsondata = json.loads(colourjson)

        # Parse available colors
        colours_list = []
        colour_names = jsondata['product']['options']
        for items in colour_names:
            if items['display_name'] == "Colour":
                colours = items['values']
                for i in colours:
                    colour = i['label']
                    colours_list.append(colour)

        # Parse gallery images mapped to colors
        image_list = []
        imagesdata = jsondata['product']['images']
        for img in imagesdata:
            alt_img = img['alt']
            image_url = img['data']
            for col in colours_list:
                if col in alt_img:
                    image_name_from_url = image_url.split('/')[-1].replace('?c=1', '')
                    image_list.append({
                        "name": image_name_from_url,
                        "url": image_url.replace("{:size}", "2000w"),
                        "colour": col
                    })
        item['images_gallary'] = image_list
        item['colours'] = colours_list

        # Extract main price
        main_price = response.xpath('.//*[@class="price price--withoutTax price-section--minor"]/text()').extract_first()
        if main_price:
            item['price'] = main_price

        # Extract tiered pricing
        price_tier_list = []
        price_under = response.xpath('//ul[contains(@class,"other-bulk-rates")]/li')
        for li in price_under:
            dic_tier = {}
            price = li.xpath('.//span[@class="price"]//text()').getall()
            if not price:
                price = li.xpath('.//text()').get()
                price = self.data_extractor(price, 'p')
            if price:
                price = [z.strip() for z in price if z.strip()]
            dic_tier['price'] = clean(''.join(price))
            dic_tier['price'] = ''.join(price)

            _tier = li.xpath('.//span[@class="range"]//text()').getall()
            if not _tier:
                tier = li.xpath('.//text()').get()
                tier = self.data_extractor(tier, 't')
            if _tier:
                tier = [x.strip() for x in _tier if x.strip()]
            dic_tier['tier'] = ''.join(tier)

            price_tier_list.append(dic_tier)

        # Deduplicate tier data
        sorted_list = [dict(t) for t in set(tuple(sorted(d.items())) for d in price_tier_list)]
        for data_dict in sorted_list:
            tier = data_dict['tier'].encode('utf8').decode('utf-8')
            data_dict['tier'] = tier
        item['prices'] = sorted_list

        # Extract product categories
        all_list = []
        uniq_list = []
        all_categories = response.xpath('.//*[@class="productView"]/@data-product-category').extract_first()
        if all_categories:
            all_categories = all_categories.split(',')
            categories = [i.strip() for i in all_categories]
            for cat in categories:
                if cat.startswith('all/') or cat == "all":
                    all_list.append(cat)
                else:
                    uniq_list.append(cat)

        # Flatten and deduplicate unique categories
        uni_list = []
        for i in uniq_list:
            spl_unq = i.split('/')
            uni_list.extend(spl_unq)
        set_of_uniq_list = list(set(uni_list))

        item['category'] = set_of_uniq_list
        item['property'] = all_list

        yield item
