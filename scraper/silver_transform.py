import json
import os
import re
from datetime import datetime

def load_bronze(source):
    bronze_dir = 'data/bronze'
    files = [f for f in os.listdir(bronze_dir) if f.startswith(source)]
    all_items = []
    for file in sorted(files):
        with open(f"{bronze_dir}/{file}", 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    all_items.extend(data)
            except:
                continue
    return all_items

def clean_price(price):
    if isinstance(price, (int, float)):
        return float(price)
    if not price:
        return None
    price = str(price).replace('€','').replace('$','').replace(',','.').strip()
    nums = re.findall(r'\d+\.?\d*', price)
    return float(nums[0]) if nums else None

def parse_footlocker_name(raw):
    if not raw:
        return '', ''
    
    lines = [l.strip() for l in raw.split('\n') if l.strip()]
    
    if len(lines) >= 3:
        model    = lines[0]
        colorway = lines[2]
    elif len(lines) == 2:
        model    = lines[0]
        colorway = lines[1] if '-' in lines[1] else ''
    else:
        model    = lines[0] if lines else ''
        colorway = ''
    
    # Supprimer la marque du début du nom
    brand_prefixes = [
        'Nike ', 'Adidas ', 'Jordan ', 'New Balance ',
        'Asics ', 'Puma ', 'Reebok ', 'Converse ',
        'Vans ', 'Salomon ', 'Hoka ', 'Saucony ',
        'Under Armour ', 'Timberland ', 'Lacoste ',
        'Birkenstock ', 'Crocs ', 'On ',
    ]
    for prefix in brand_prefixes:
        if model.startswith(prefix):
            model = model[len(prefix):]
            break
    
    return model.strip(), colorway.strip()

def detect_brand(raw_name, brand_field):
    name_lower = raw_name.lower()
    
    # Jordan AVANT Nike !
    if 'jordan' in name_lower or 'air jordan' in name_lower:
        return 'Jordan'
    if 'yeezy' in name_lower or 'yzy' in name_lower:
        return 'Adidas'
    if 'nike' in name_lower:
        return 'Nike'
    if 'adidas' in name_lower:
        return 'Adidas'
    if 'new balance' in name_lower:
        return 'New Balance'
    if 'asics' in name_lower:
        return 'Asics'
    if 'puma' in name_lower:
        return 'Puma'
    if 'reebok' in name_lower:
        return 'Reebok'
    if 'converse' in name_lower:
        return 'Converse'
    if 'vans' in name_lower:
        return 'Vans'
    if 'salomon' in name_lower:
        return 'Salomon'
    if 'hoka' in name_lower:
        return 'Hoka'
    if 'saucony' in name_lower:
        return 'Saucony'
    if 'under armour' in name_lower:
        return 'Under Armour'
    if 'timberland' in name_lower:
        return 'Timberland'
    if 'lacoste' in name_lower:
        return 'Lacoste'
    if 'on running' in name_lower or ' on ' in name_lower:
        return 'On Running'
    if 'birkenstock' in name_lower:
        return 'Birkenstock'
    if 'crocs' in name_lower:
        return 'Crocs'
    
    # Utilise le champ brand si disponible
    if brand_field and brand_field.strip() and brand_field != 'Unknown':
        return brand_field.strip().title()
    
    return 'Unknown'

def transform_to_silver():
    os.makedirs('data/silver', exist_ok=True)
    
    all_items = []
    
    for source in ['footlocker', 'kickscrew']:
        items = load_bronze(source)
        print(f"  Bronze {source}: {len(items)} items chargés")
        
        for item in items:
            raw_name = item.get('name', '')
            price    = clean_price(item.get('price', 0))
            
            # Parse le nom Footlocker
            if source == 'footlocker':
                model, colorway = parse_footlocker_name(raw_name)
            else:
                model    = raw_name.strip()
                colorway = ''
            
            if not model or not price or price <= 0:
                continue
            
            brand = detect_brand(model, item.get('brand', ''))
            
            silver_item = {
                'name':         model,
                'colorway':     colorway,
                'brand':        brand,
                'price_retail': price,
                'currency':     item.get('currency', 'EUR'),
                'source':       source,
                'url':          item.get('url', ''),
                'image':        item.get('image', ''),
                'ingested_at':  item.get('ingested_at', ''),
                'transformed_at': datetime.now().isoformat(),
                'source_layer': 'silver',
            }
            all_items.append(silver_item)
    
    # Déduplication LÉGÈRE — par url seulement
    # Garde TOUS les colorways différents !
    seen_urls = set()
    unique_items = []
    
    for item in all_items:
        url = item.get('url', '')
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)
        unique_items.append(item)
    
    # Sauvegarde
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename  = f"data/silver/sneakers_clean_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(unique_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n[SILVER] {len(unique_items)} items sauvegardés ✅")
    
    # Stats marques
    from collections import Counter
    brands = Counter(i['brand'] for i in unique_items)
    print("\n📊 Par marque :")
    for b, c in brands.most_common(10):
        print(f"  {b}: {c}")
    
    return unique_items

if __name__ == "__main__":
    transform_to_silver()