# Web Scraping Projects

This repository contains three web scraping scripts targeting different e-commerce websites. The tools used include Scrapy and Selenium (with undetected-chromedriver).

---

## 📁 Project Structure

```
.
├── ascolour_spider/
│   └── ascolor_spider.py
├── com1_spider/
│   └── com1_spider.py
├── euspares_scraper/
│   └── eusp_selenium_scraper.py
└── scrapy.cfg
```

---

## 🕷️ 1. ASColour Spider

**Script Path:** `ascolour_spider/ascolor_spider.py`  
**Framework:** Scrapy  
**Target:** [ascolour.co.nz](https://www.ascolour.co.nz)

### Features
- Logs in via POST request
- Parses sitemap for product URLs
- Extracts:
  - SKU, name, price, tiered pricing
  - Gallery and feature images mapped to colors
  - Description, categories, properties

### Run Command
```bash
cd ascolour_spider
scrapy crawl ascolor
```

---

## 🕷️ 2. Com1 Spider

**Script Path:** `com1_spider/com1_spider.py`  
**Framework:** Scrapy  
**Target:** [com1.com.au](https://www.com1.com.au)

### Features
- Logs in using credentials from `scrapy.cfg`
- Navigates categories and extracts:
  - Name, SKU, price, availability
  - Manufacturer number, weight, dimensions
  - Specifications and images

### Run Command
```bash
cd com1_spider
scrapy crawl com_1
```

> ⚠️ Make sure your credentials are set correctly in `scrapy.cfg`.

---

## 🖱️ 3. EUspares Selenium Scraper

**Script Path:** `euspares_scraper/eusp_selenium_scraper.py`  
**Framework:** Selenium (`undetected-chromedriver`) + Requests + Scrapy selectors  
**Target:** [euspares.co.uk](https://www.euspares.co.uk)

### Features
- Uses undetected ChromeDriver for login bypass
- Scrapes data using Requests + Scrapy Selectors
- Extracts:
  - Title, subtitle, description
  - Price, brand, OE number, compatibility
  - Category, image URLs

### Run Command
```bash
cd euspares_scraper
python eusp_selenium_scraper.py
```

> Output is saved to `all_brands/vika.csv`.

---

## 📦 Installation

Install all dependencies:

```bash
pip install scrapy selenium undetected-chromedriver pandas clean-text
```

---

## ✅ Notes

- Ensure proper credentials are configured for login-required spiders.
- Folder structure and paths must be followed as shown above.
- Outputs are saved in CSV or as JSON, depending on the script.

---
