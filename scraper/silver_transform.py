import json
import os
import re
from datetime import datetime

def load_bronze(source):
    """Charge les fichiers bronze d'une source"""
    bronze_dir = 'data/bronze'
    files = [f for f in os.listdir(bronze_dir) if f.startswith(source)]
    all_items = []
    for file in files:
        with open(f"{bronze_dir}/{file}", 'r', encoding='utf-8') as f:
            all_items.extend(json.load(f))
    return all_items

def clean_price(price_str):
    """Nettoie et normalise les prix en float"""
    # Si c'est déjà un nombre, le retourner directement
    if isinstance(price_str, (int, float)):
        return float(price_str)
    if not price_str:
        return None
    price_str = str(price_str).replace('€', '').replace('$', '')
    price_str = price_str.replace(',', '.').strip()
    numbers = re.findall(r'\d+\.?\d*', price_str)
    return float(numbers[0]) if numbers else None

def clean_name(name):
    """Normalise le nom du produit"""
    if not name:
        return None
    return name.strip().title()

def detect_brand(name, brand):
    """Détecte la marque depuis le nom si manquante"""
    brands = ['Nike', 'Jordan', 'Adidas', 'New Balance', 
              'Puma', 'Reebok', 'Asics', 'Converse', 'Vans']
    if brand:
        return brand.strip().title()
    for b in brands:
        if b.lower() in name.lower():
            return b
    return 'Unknown'

def transform_to_silver():
    os.makedirs('data/silver', exist_ok=True)
    
    all_items = []
    
    for source in ['kickscrew', 'footlocker']:
        items = load_bronze(source)
        
        for item in items:
            # Nettoyage
            name = clean_name(item.get('name', ''))
            price = clean_price(item.get('price', ''))
            brand = detect_brand(name or '', item.get('brand', ''))
            
            # Validation — on skip les items invalides
            if not name or not price:
                continue
            
            silver_item = {
                'name': name,
                'brand': brand,
                'price_retail': price,
                'currency': 'EUR' if source == 'footlocker' else 'USD',
                'source': item.get('source'),
                'url': item.get('url'),
                'image': item.get('image'),
                'ingested_at': item.get('ingested_at'),
                'transformed_at': datetime.now().isoformat(),
                'source_layer': 'silver'
            }
            all_items.append(silver_item)
    
    # Dédoublonnage par nom + source
    seen = set()
    unique_items = []
    for item in all_items:
        key = f"{item['name']}_{item['source']}"
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    
    # Sauvegarde Silver
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/silver/sneakers_clean_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(unique_items, f, ensure_ascii=False, indent=2)
    
    print(f"[SILVER] {len(unique_items)} items nettoyés sauvegardés")
    return unique_items

if __name__ == "__main__":
    transform_to_silver()