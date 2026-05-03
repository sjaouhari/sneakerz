import scrapy
import json
import re
from datetime import datetime

class KickCrewSpider(scrapy.Spider):
    name = "kickscrew"
    base_url = "https://www.kickscrew.com/collections/shoes?page={}"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    async def start(self):
        for page in range(1, 10):
            yield scrapy.Request(
                url=self.base_url.format(page),
                callback=self.parse
            )

    def parse(self, response):
        # Méthode 1 : JSON dans le script
        scripts = response.css('script[type="application/json"]::text').getall()
        for script in scripts:
            try:
                data = json.loads(script)
                products = data.get('products', [])
                for p in products:
                    yield {
                        'source': 'kickscrew',
                        'name': p.get('title', ''),
                        'brand': p.get('vendor', ''),
                        'price': str(p.get('price', p.get('price_min', ''))),
                        'currency': 'USD',
                        'url': f"https://www.kickscrew.com/products/{p.get('handle', '')}",
                        'image': p.get('featured_image', ''),
                        'ingested_at': datetime.now().isoformat(),
                        'source_layer': 'bronze',
                    }
            except:
                continue

        # Méthode 2 : CSS selectors classiques
        products = response.css('div.product-item, div.grid__item, li.grid__item')
        for p in products:
            name = (p.css('h3::text, .product-item__title::text, '
                         '.card__heading::text').get('') or '').strip()
            brand = (p.css('.product-item__vendor::text, '
                          '.card__vendor::text').get('') or '').strip()
            price = (p.css('.price__regular .price-item::text, '
                          'span.price::text, .price::text').get('') or '').strip()
            url = p.css('a::attr(href)').get('')

            if name:
                yield {
                    'source': 'kickscrew',
                    'name': name,
                    'brand': brand,
                    'price': price,
                    'currency': 'USD',
                    'url': f"https://www.kickscrew.com{url}" if url else '',
                    'image': p.css('img::attr(src)').get(''),
                    'ingested_at': datetime.now().isoformat(),
                    'source_layer': 'bronze',
                }

        self.logger.info(f"Page scrapée : {response.url}")