import scrapy


class Com1SpiderItem(scrapy.Item):
    Name = scrapy.Field()
    SKU = scrapy.Field()
    Price = scrapy.Field()
    Description = scrapy.Field()
    Available_qty = scrapy.Field()
    Brand = scrapy.Field()
    Manufacturer_Part_Number = scrapy.Field()
    Product_page_link = scrapy.Field()
    Weight = scrapy.Field()
    specification = scrapy.Field()
    image = scrapy.Field()
    Width = scrapy.Field()
    Height = scrapy.Field()
    Length = scrapy.Field()
    scrapedDate = scrapy.Field()
