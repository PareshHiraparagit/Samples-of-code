import undetected_chromedriver as uc
import time
import csv
import requests
import codecs
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector

# Output CSV setup
f = open('all_brands/vika.csv', 'w', encoding='utf-8')
coloum_fields = [
    'Category (Parent)',
    'Category URL (Parent)',
    'Category - Leaf (Child 1)',
    'Category URL - Leaf (Child 1)',
    'Product URL',
    'PartNumber',
    'Product Title',
    'Product Subtitle',
    'Product Description',
    'Image URLs',
    'Price',
    'List of Vehicle Compatibility',
    'Brand',
    'OE part number'
]
csv_writer = csv.DictWriter(f, fieldnames=coloum_fields)
csv_writer.writeheader()

# Get session cookies using undetected_chromedriver to bypass bot protection
def get_cookie():
    driver = uc.Chrome(use_subprocess=True)
    with driver:
        driver.get('https://www.euspares.co.uk/')
        time.sleep(10)
        cookies = driver.get_cookies()

    cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    driver.quit()
    return cookie_dict

# Get product detail data from product page
def get_detail(product_url, cat_url, cat):
    # Use global cookie_dict for authentication
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'cookie': '; '.join([f"{k}={v}" for k, v in cookie_dict.items()]),
    }

    res3 = requests.get(product_url, headers=headers)
    html = res3.text
    response3 = Selector(text=html)

    item = {
        "Category (Parent)": cat,
        "Category URL (Parent)": cat_url,
        "Category - Leaf (Child 1)": None,
        "Category URL - Leaf (Child 1)": None,
        "Product URL": product_url,
    }

    # Product identifiers and details
    item["PartNumber"] = response3.xpath('.//span[@itemprop="sku"]/@content').get()
    title_main = response3.xpath('.//h2[@itemprop="name"]/span/span/text()').get(default='').strip()
    title_sub = response3.xpath('.//h2[@itemprop="name"]/span/text()').get(default='').strip()
    item['Product Title'] = f"{title_main} {title_sub}"
    item['Product Subtitle'] = None

    # Description
    desc_list = []
    desc_head = response3.xpath('.//div[@class="col"][1]//tr/th/text()').get()
    if desc_head:
        desc_list.append(desc_head.strip())

    desc_keys = response3.xpath('.//*[@itemprop="description"]//li/span[1]/text()').getall()
    desc_vals = response3.xpath('.//*[@itemprop="description"]//li/span[2]/text()').getall()
    for k, v in zip(desc_keys, desc_vals):
        desc_list.append(f"{k.strip()} {v.strip()}")

    extra_keys = ['Designation', 'Manufacturer', 'EAN', 'Item number:', 'Our price:']
    extra_selectors = [
        './/*[contains(text(),"Designation")]/following-sibling::span/text()',
        './/*[contains(text(),"Manufacturer")]/following-sibling::span/text()',
        './/*[contains(text(),"EAN")]/following-sibling::span/text()',
        './/td[contains(text(),"Item number:")]/span/text()',
        ['.//td[contains(text(),"Our price:")]/span[1]/text()', './/td[contains(text(),"Our price:")]/span[2]/text()']
    ]

    for key, selector in zip(extra_keys[:-1], extra_selectors[:-1]):
        val = response3.xpath(selector).get()
        if val:
            desc_list.append(f"{key}: {val.strip()}")

    price1 = response3.xpath(extra_selectors[-1][0]).get(default='').strip()
    price2 = response3.xpath(extra_selectors[-1][1]).get(default='').strip()
    if price1 or price2:
        desc_list.append(f"Our price: {price1} {price2}")

    item["Product Description"] = desc_list if desc_list else None

    # Images
    image_urls = response3.xpath('.//li[@data-fancybox="productImageGroup"]/@href | .//a[@data-slide-index]/img/@src').getall()
    item['Image URLs'] = list(set(image_urls)) or None

    # Price
    item['Price'] = response3.xpath('.//*[@itemprop="price"]/@content').get()

    # Brand
    item['Brand'] = response3.xpath('.//div[@class="art"]//a/span/text()').get()

    # OE Part Numbers
    item['OE part number'] = response3.xpath('.//div[@class="oeNum_data"]//ul//li/*/text()').getall() or None

    # Compatibility AJAX request
    comp_id = response3.xpath('.//div[@class="product_page eu"]/@data-ref').get()
    if comp_id:
        payload = f"id={comp_id}&eq=0"
        headers_ajax = {
            'x-requested-with': 'XMLHttpRequest',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': headers['cookie']
        }
        responseC = requests.post(
            "https://www.euspares.co.uk/ajax/product/models_by_product",
            headers=headers_ajax,
            data=payload
        )
        decoded = codecs.decode(responseC.text, "unicode_escape").replace('\\/', '/')
        comp_resp = Selector(text=decoded)

        Compatibility_list = []
        for box in comp_resp.xpath('//*[contains(@class,"list_auto_tab")]'):
            make = box.xpath('.//a//text()').get(default='').strip()
            for row in box.xpath('.//tr'):
                model = row.xpath('.//span[@class="name"]/text()').get(default='').strip()
                year = row.xpath('.//span[@class="date"]/text()').get(default='').strip()
                Compatibility_list.append({"Make": make, "Model": model, "Year": year})

        item['List of Vehicle Compatibility'] = Compatibility_list if Compatibility_list else None

    return item

print("<<<-------start------->>>")

count = 0
all_brand_urls = []
df = pd.read_csv('/media/paresh/Work Space/MY_WORK/EUSPares/product_urls.csv')
latter_urls = df['brand_urls']

# Iterate each brand URL and extract product data
for latter_url in latter_urls:
    cookie_dict = get_cookie()
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'cookie': '; '.join([f"{k}={v}" for k, v in cookie_dict.items()]),
    }

    res = requests.get(latter_url, headers=headers)
    response = Selector(text=res.text)

    category_urls = response.xpath("//*[@class='supplier_cat']//a/@href | .//*[@class='supplier_cat']/span/@url").getall()
    category_names = response.xpath(".//*[@class='supplier_cat']//a/text() | .//*[@class='supplier_cat']/span//text()").getall()

    for cat_url, cat in zip(category_urls, category_names):
        res1 = requests.get(cat_url, headers=headers)
        response1 = Selector(text=res1.text)
        product_urls = response1.xpath(".//*[@class='imgdesc_wrapper']//a/@href").getall()

        count += len(product_urls)
        all_brand_urls += [product_urls, cat, cat_url]

        for product_url in product_urls:
            item = get_detail(product_url, cat_url, cat)
            csv_writer.writerow(item)

print("Total count", count)