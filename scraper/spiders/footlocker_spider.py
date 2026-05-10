import requests
import json
import os
import time
from datetime import datetime

def scrape_footlocker(max_pages=10):
    """Scrape Footlocker via leur API interne"""
    
    os.makedirs('data/bronze', exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Referer': 'https://www.footlocker.fr/',
        'x-fl-request-id': 'sneakerz-project',
    }
    
    all_products = []
    
    print("🕷️ Scraping Footlocker...")
    
    for page in range(0, max_pages * 48, 48):
        url = (f"https://www.footlocker.fr/api/products/search"
               f"?query=shoes&start={page}&size=48"
               f"&sort=newArrivals&lang=fr-FR")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"  Page {page//48 + 1} — Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                if not products:
                    break
                    
                for p in products:
                    price = p.get('grossPrice', {}).get('value', 0)
                    sku = p.get('sku', '')
                    
                    product = {
                        'source': 'footlocker',
                        'name': p.get('name', '').strip(),
                        'brand': p.get('brand', '').strip(),
                        'price': float(price) if price else 0,
                        'currency': 'EUR',
                        'sku': sku,
                        'url': f"https://www.footlocker.fr/fr/product/{p.get('url', '')}",
                        'image': f"https://images.footlocker.com/is/image/FLEU/{sku}?wid=250&hei=250",
                        'category': p.get('category', ''),
                        'ingested_at': datetime.now().isoformat(),
                        'source_layer': 'bronze',
                    }
                    all_products.append(product)
                
                print(f"  ✅ {len(products)} produits récupérés")
                time.sleep(1)
            else:
                break
                
        except Exception as e:
            print(f"  ❌ Erreur : {e}")
            break
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output = f'data/bronze/footlocker_raw_{timestamp}.json'
    
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ {len(all_products)} produits Footlocker → {output}")
    return all_products

if __name__ == "__main__":
    products = scrape_footlocker(max_pages=12)
    print(f"\n🎯 Total : {len(products)} produits scrapés !")