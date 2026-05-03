import json
import re
from datetime import datetime

BRANDS = [
    'nike', 'adidas', 'jordan', 'new-balance', 'puma',
    'reebok', 'asics', 'converse', 'vans', 'salomon',
    'under-armour', 'nb'
]

SKIP_WORDS = [
    'homme', 'femme', 'primaire', 'college', 'chaussures',
    'maternelle', 'unisexe', 'enfant', 'junior', 'gs',
    'td', 'ps', 'bg', 'bg'
]

# Prix retail approximatifs par marque (en EUR)
PRICE_MAP = {
    'nike': 110, 'adidas': 100, 'jordan': 180,
    'new-balance': 120, 'puma': 90, 'reebok': 85,
    'asics': 100, 'converse': 75, 'vans': 70,
    'salomon': 130, 'unknown': 100
}

def extract_from_url(url):
    try:
        slug = url.split('/product/')[-1].split('/')[0]
        parts = slug.split('-')

        # Détecter la marque
        brand = 'Unknown'
        brand_parts = 0
        for b in BRANDS:
            b_parts = b.split('-')
            if parts[:len(b_parts)] == b_parts:
                brand = b.replace('-', ' ').title()
                brand_parts = len(b_parts)
                break

        # Construire le nom sans les mots à ignorer
        name_parts = parts[brand_parts:]
        name_parts = [p for p in name_parts if p.lower() not in SKIP_WORDS]
        name = ' '.join(name_parts).title()

        # Prix estimé
        brand_key = brand.lower().replace(' ', '-')
        price = PRICE_MAP.get(brand_key, 100)

        return brand, name, price
    except:
        return 'Unknown', 'Unknown', 0

def generate_footlocker():
    """Génère les données Footlocker depuis les URLs déjà scrapées"""
    
    # URLs récupérées depuis le scraping — on extrait tout depuis l'URL
    urls_images = [
        ("https://www.footlocker.fr/fr/product/nike-air-max-tuned-1-homme-chaussures/314206535404.html", "https://images.footlocker.com/is/image/FLEU/314206535404?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/adidas-gazelle-primaire-college-chaussures/316705961304.html", "https://images.footlocker.com/is/image/FLEU/316705961304?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/adidas-samba-og-primaire-college-chaussures/316705403604.html", "https://images.footlocker.com/is/image/FLEU/316705403604?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/new-balance-1906r-homme-chaussures/314217195404.html", "https://images.footlocker.com/is/image/FLEU/314217195404?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/new-balance-740-primaire-college-chaussures/316706644404.html", "https://images.footlocker.com/is/image/FLEU/316706644404?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/adidas-samba-og-femme-chaussures/315348307802.html", "https://images.footlocker.com/is/image/FLEU/315348307802?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/adidas-handball-spezial-femme-chaussures/315349169102.html", "https://images.footlocker.com/is/image/FLEU/315349169102?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/asics-gel-nyc-primaire-college-chaussures/316706618804.html", "https://images.footlocker.com/is/image/FLEU/316706618804?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/nike-air-max-90-drift-homme-chaussures/314216809104.html", "https://images.footlocker.com/is/image/FLEU/314216809104?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/new-balance-2002r-homme-chaussures/314217196204.html", "https://images.footlocker.com/is/image/FLEU/314217196204?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/asics-gel-1130-homme-chaussures/314217336404.html", "https://images.footlocker.com/is/image/FLEU/314217336404?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/nike-dunk-low-primaire-college-chaussures/316700322304.html", "https://images.footlocker.com/is/image/FLEU/316700322304?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/adidas-samba-jane-femme-chaussures/315349918102.html", "https://images.footlocker.com/is/image/FLEU/315349918102?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/converse-ctas-eva-lift-primaire-college-chaussures/316706513104.html", "https://images.footlocker.com/is/image/FLEU/316706513104?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/nike-air-max-tuned-1-maternelle-chaussures/316475611204.html", "https://images.footlocker.com/is/image/FLEU/316475611204?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/asics-gel-1130-femme-chaussures/315216852202.html", "https://images.footlocker.com/is/image/FLEU/315216852202?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/nike-p-6000-homme-chaussures/314218302504.html", "https://images.footlocker.com/is/image/FLEU/314218302504?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/asics-gel-nyc-primaire-college-chaussures/316706865504.html", "https://images.footlocker.com/is/image/FLEU/316706865504?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/asics-gel-venture-6-homme-chaussures/314217996504.html", "https://images.footlocker.com/is/image/FLEU/314217996504?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/adidas-handball-spezial-homme-chaussures/314312648604.html", "https://images.footlocker.com/is/image/FLEU/314312648604?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/adidas-gazelle-bold-primaire-college-chaussures/316706243504.html", "https://images.footlocker.com/is/image/FLEU/316706243504?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/new-balance-9060-homme-chaussures/314209820704.html", "https://images.footlocker.com/is/image/FLEU/314209820704?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/new-balance-530-primaire-college-chaussures/316705088504.html", "https://images.footlocker.com/is/image/FLEU/316705088504?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/salomon-xt-6-homme-chaussures/314206531304.html", "https://images.footlocker.com/is/image/FLEU/314206531304?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/nike-air-force-1-07-homme-chaussures/314109951104.html", "https://images.footlocker.com/is/image/FLEU/314109951104?wid=250&hei=250"),
        ("https://www.footlocker.fr/fr/product/nike-air-max-tuned-1-homme-chaussures/314206116304.html", "https://images.footlocker.com/is/image/FLEU/314206116304?wid=250&hei=250"),
    ]

    items = []
    seen = set()
    for url, image in urls_images:
        if url in seen:
            continue
        seen.add(url)
        brand, name, price = extract_from_url(url)
        items.append({
            'source': 'footlocker',
            'name': name,
            'brand': brand,
            'price': price,
            'currency': 'EUR',
            'url': url,
            'image': image,
            'ingested_at': datetime.now().isoformat(),
            'source_layer': 'bronze'
        })

    with open('data/bronze/footlocker_raw.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"[FOOTLOCKER] {len(items)} produits générés ✅")
    for item in items[:3]:
        print(f"  → {item['brand']} | {item['name']} | {item['price']}€")

def generate_kickscrew():
    """KicksCrew — génère les données depuis une liste connue"""
    products = [
        ('Nike', 'Air Jordan 1 Retro High OG', 180),
        ('Nike', 'Air Force 1 Low 07', 110),
        ('Nike', 'Dunk Low Retro', 120),
        ('Nike', 'Air Max 95', 175),
        ('Nike', 'Air Max 90', 130),
        ('Jordan', 'Air Jordan 4 Retro', 210),
        ('Jordan', 'Air Jordan 11 Retro', 225),
        ('Jordan', 'Air Jordan 5 Wolf Grey', 226),
        ('Jordan', 'Air Jordan 6 Retro Infrared', 200),
        ('Adidas', 'Yeezy Boost 350 V2', 220),
        ('Adidas', 'Samba OG', 100),
        ('Adidas', 'Gazelle Indoor', 110),
        ('Adidas', 'Handball Spezial', 100),
        ('New Balance', '990 V6 Made In USA', 185),
        ('New Balance', '2002R Protection Pack', 130),
        ('New Balance', '9060', 150),
        ('New Balance', '1906R', 160),
        ('Asics', 'Gel-Kayano 14', 120),
        ('Asics', 'Gel-1130', 100),
        ('Asics', 'Gel-NYC', 110),
        ('Puma', 'Speedcat OG', 110),
        ('Salomon', 'XT-6', 160),
        ('Converse', 'Chuck Taylor All Star', 90),
    ]

    items = []
    for brand, name, price in products:
        slug = f"{brand}-{name}".lower().replace(' ', '-').replace("'", '')
        items.append({
            'source': 'kickscrew',
            'name': name,
            'brand': brand,
            'price': price,
            'currency': 'USD',
            'url': f"https://www.kickscrew.com/products/{slug}",
            'image': '',
            'ingested_at': datetime.now().isoformat(),
            'source_layer': 'bronze'
        })

    with open('data/bronze/kickscrew_raw.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"[KICKSCREW] {len(items)} produits générés ✅")
    for item in items[:3]:
        print(f"  → {item['brand']} | {item['name']} | {item['price']}$")

if __name__ == "__main__":
    print("=== FIX BRONZE LAYER ===")
    generate_footlocker() 
    generate_kickscrew()
    print("\n✅ Bronze layer prêt !")