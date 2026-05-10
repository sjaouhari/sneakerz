import scrapy
import json
import re
from datetime import datetime

class SnipesSpider(scrapy.Spider):
    name = "snipes"
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'FEEDS': {
            'data/bronze/snipes_raw.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
            }
        }
    }

    # Plusieurs catégories pour avoir ~500 produits
    start_urls = [
        "https://www.snipes.com/fr-fr/c/chaussures?srule=best-sellers&start=0&sz=100",
        "https://www.snipes.com/fr-fr/c/chaussures?srule=best-sellers&start=100&sz=100",
        "https://www.snipes.com/fr-fr/c/chaussures?srule=best-sellers&start=200&sz=100",
        "https://www.snipes.com/fr-fr/c/chaussures?srule=best-sellers&start=300&sz=100",
        "https://www.snipes.com/fr-fr/c/chaussures?srule=best-sellers&start=400&sz=100",
    ]

    def parse(self, response):
        # Les données sont dans un script JSON
        scripts = response.css('script::text').getall()
        
        for script in scripts:
            if 'gtm4wp.blockedProductData' in script or '"products"' in script:
                try:
                    # Cherche les données produit dans le JS
                    matches = re.findall(
                        r'"name"\s*:\s*"([^"]+)"[^}]*"price"\s*:\s*(\d+\.?\d*)',
                        script
                    )
                    for name, price in matches:
                        yield {
                            'source': 'snipes',
                            'name': name.strip(),
                            'brand': self.detect_brand(name),
                            'price': float(price),
                            'currency': 'EUR',
                            'url': response.url,
                            'image': '',
                            'ingested_at': datetime.now().isoformat(),
                            'source_layer': 'bronze',
                        }
                except:
                    continue

        # CSS selectors classiques
        products = response.css(
            'div.product-tile, div[class*="product"], '
            'article[class*="product"]'
        )
        
        for p in products:
            name = p.css(
                'div.product-name::text, '
                '[class*="product-name"]::text, '
                'h3::text, h2::text'
            ).get('').strip()
            
            brand = p.css(
                '[class*="brand"]::text, '
                '[class*="vendor"]::text'
            ).get('').strip()
            
            price = p.css(
                '[class*="sales"] span::text, '
                '[class*="price"]::text, '
                'span.value::text'
            ).get('').strip()
            
            price_nums = re.findall(r'\d+[.,]?\d*', price.replace(',', '.'))
            price_val = float(price_nums[0]) if price_nums else 0
            
            url = p.css('a::attr(href)').get('')
            img = p.css('img::attr(src), img::attr(data-src)').get('')
            
            if name and price_val > 0:
                yield {
                    'source': 'snipes',
                    'name': name,
                    'brand': brand if brand else self.detect_brand(name),
                    'price': price_val,
                    'currency': 'EUR',
                    'url': f"https://www.snipes.com{url}" if url.startswith('/') else url,
                    'image': img,
                    'ingested_at': datetime.now().isoformat(),
                    'source_layer': 'bronze',
                }

    def detect_brand(self, name):
        brands = {
            'nike': 'Nike', 'jordan': 'Jordan', 'air jordan': 'Jordan',
            'adidas': 'Adidas', 'yeezy': 'Adidas',
            'new balance': 'New Balance', 'puma': 'Puma',
            'reebok': 'Reebok', 'asics': 'Asics',
            'converse': 'Converse', 'vans': 'Vans',
            'salomon': 'Salomon', 'saucony': 'Saucony',
        }
        name_lower = name.lower()
        for key, brand in brands.items():
            if key in name_lower:
                return brand
        return 'Unknown'