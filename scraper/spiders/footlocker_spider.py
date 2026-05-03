import scrapy
import re
from datetime import datetime

class FootlockerSpider(scrapy.Spider):
    name = "footlocker"
    base_url = "https://www.footlocker.fr/fr/category/chaussures.html?start={}&size=48"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    async def start(self):
        for start in range(0, 200, 48):
            yield scrapy.Request(
                url=self.base_url.format(start),
                callback=self.parse
            )

    def extract_info_from_url(self, url):
        """Extrait nom et marque depuis l'URL du produit"""
        try:
            # URL: /fr/product/nike-air-max-tuned-1-homme-chaussures/314206535404.html
            slug = url.split('/product/')[-1].split('/')[0]
            parts = slug.split('-')
            
            brands = ['nike', 'adidas', 'jordan', 'new-balance', 'puma', 
                     'reebok', 'asics', 'converse', 'vans', 'salomon',
                     'new', 'balance']
            
            # Détecter la marque
            brand = parts[0].capitalize()
            if parts[0] == 'new' and len(parts) > 1 and parts[1] == 'balance':
                brand = 'New Balance'
            
            # Construire le nom propre
            name = ' '.join(parts).replace('-', ' ').title()
            # Supprimer "Homme" "Femme" "Chaussures" etc
            for word in ['Homme', 'Femme', 'Chaussures', 'Primaire', 'College', 
                        'Maternelle', 'Unisexe']:
                name = name.replace(f' {word}', '')
            
            return brand, name.strip()
        except:
            return 'Unknown', 'Unknown'

    def parse(self, response):
        products = response.css('div.ProductCard, li.product-grid__item, div.product-item')
        
        if not products:
            # Fallback: extraire depuis les liens
            links = response.css('a[href*="/product/"]')
            for link in links:
                url = link.css('::attr(href)').get('')
                if not url or 'product' not in url:
                    continue
                    
                full_url = "https://www.footlocker.fr" + url if url.startswith('/') else url
                image = link.css('img::attr(src)').get('')
                brand, name = self.extract_info_from_url(full_url)
                
                # Prix depuis data attributes ou texte
                price = link.css('[data-price]::attr(data-price)').get('')
                if not price:
                    price = link.css('.price::text, .ProductPrice::text').get('').strip()

                yield {
                    'source': 'footlocker',
                    'name': name,
                    'brand': brand,
                    'price': price if price else 'N/A',
                    'currency': 'EUR',
                    'url': full_url,
                    'image': image,
                    'ingested_at': datetime.now().isoformat(),
                    'source_layer': 'bronze',
                }

        self.logger.info(f"Page scrapée : {response.url}")