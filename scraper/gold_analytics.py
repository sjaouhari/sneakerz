import json
import os
from datetime import datetime
from collections import defaultdict

def load_silver():
    silver_dir = 'data/silver'
    all_items = []
    for file in os.listdir(silver_dir):
        with open(f"{silver_dir}/{file}", 'r', encoding='utf-8') as f:
            all_items.extend(json.load(f))
    return all_items

# Prix de revente eBay simulés (markup réaliste du marché)
RESELL_MARKUP = {
    'Nike': 1.8,
    'Jordan': 2.5,
    'Adidas': 1.6,
    'New Balance': 1.7,
    'Asics': 1.5,
    'Puma': 1.4,
    'Salomon': 1.6,
    'Converse': 1.3,
    'Unknown': 1.4,
}

def compute_margins(items):
    margins = []
    for item in items:
        brand = item.get('brand', 'Unknown')
        retail_price = item.get('price_retail', 0)
        if not retail_price:
            continue

        markup = RESELL_MARKUP.get(brand, 1.4)
        resell_price = round(retail_price * markup, 2)
        margin = round(resell_price - retail_price, 2)
        margin_pct = round((margin / retail_price) * 100, 2)

        margins.append({
            'name': item['name'],
            'brand': brand,
            'price_retail': retail_price,
            'price_resell_ebay': resell_price,
            'margin_value': margin,
            'margin_percent': margin_pct,
            'currency': item.get('currency', 'EUR'),
            'source_retail': item.get('source'),
            'url': item.get('url'),
        })

    return sorted(margins, key=lambda x: x['margin_value'], reverse=True)

def top_brands(items):
    brand_count = defaultdict(int)
    for item in items:
        brand_count[item['brand']] += 1
    return dict(sorted(brand_count.items(), key=lambda x: x[1], reverse=True))

def transform_to_gold():
    os.makedirs('data/gold', exist_ok=True)

    items = load_silver()
    margins = compute_margins(items)

    gold_data = {
        'generated_at': datetime.now().isoformat(),
        'source_layer': 'gold',
        'stats': {
            'total_sneakers': len(items),
            'total_with_margin': len(margins),
            'top_brands': top_brands(items),
            'avg_margin_percent': round(
                sum(m['margin_percent'] for m in margins) / len(margins), 2
            ) if margins else 0,
        },
        'top_margins': margins[:10],
        'all_margins': margins,
    }

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/gold/sneakers_analytics_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(gold_data, f, ensure_ascii=False, indent=2)

    print(f"[GOLD] Analytics générées — {len(margins)} marges calculées ✅")
    print(f"[GOLD] Top 3 opportunités :")
    for s in margins[:3]:
        print(f"  → {s['brand']} {s['name']} | Retail: {s['price_retail']}€ | Revente: {s['price_resell_ebay']}€ | Marge: +{s['margin_value']}€ ({s['margin_percent']}%)")

    return gold_data

if __name__ == "__main__":
    transform_to_gold()