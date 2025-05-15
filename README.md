# Web Scraping Projects

This repository contains three different web scraping projects built using Scrapy and Selenium. Each project targets a different e-commerce website and extracts product data such as SKU, name, price, images, specifications, and more.

---

## 1. `ascolor_spider.py`

**Target Website:** [ascolour.co.nz](https://www.ascolour.co.nz)  
**Framework:** Scrapy

### Features:
- Logs in using a POST request and handles authentication.
- Parses product sitemap to gather product URLs.
- Extracts comprehensive product details:
  - SKU, name, description, price, tiered pricing
  - Feature and gallery images mapped to color variations
  - Category tags and product properties
- Parses embedded JavaScript JSON for color and image mapping.

---

## 2. `com1_spider.py`

**Target Website:** [com1.com.au](https://www.com1.com.au)  
**Framework:** Scrapy

### Features:
- Logs in using credentials stored in `scrapy.cfg`.
- Navigates through product categories and subcategories.
- Extracts detailed product data:
  - Name, SKU, price, availability
  - Manufacturer part number, specifications
  - Weight and dimensions (with unit normalization)
  - Product and thumbnail image URLs

---

## 3. `eusp_selenium_scraper.py`

**Target Website:** [euspares.co.uk](https://www.euspares.co.uk)  
**Framework:** Selenium + `undetected-chromedriver` + Requests + Scrapy Selectors

### Features:
- Uses undetected ChromeDriver to bypass bot protection.
- Authenticates via browser session and captures cookies.
- Scrapes data using `requests` and Scrapy selectors on rendered HTML.
- Extracts and saves:
  - Category name and URL
  - Product title, subtitle, description
  - Image URLs, price, vehicle compatibility, brand, OE part number
- Outputs data to CSV (`vika.csv`) under the `all_brands/` folder.

---

## Setup & Usage

### Install Dependencies
```bash
pip install scrapy selenium undetected-chromedriver pandas clean-text

Run Spiders:

Scrapy Spiders:
scrapy crawl ascolor
scrapy crawl com_1

Selenium Script:
python eusp.py
