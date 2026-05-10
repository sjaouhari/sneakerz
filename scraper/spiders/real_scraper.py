from playwright.sync_api import sync_playwright
import json
import os
import re
import time
from datetime import datetime

os.makedirs('data/bronze', exist_ok=True)

BRANDS = [
    # Sneakers classiques
    'Nike', 'Jordan', 'Adidas', 'New Balance', 'Puma',
    'Reebok', 'Asics', 'Converse', 'Vans', 'Salomon',
    'Under Armour', 'Saucony', 'Hoka', 'On Running',
    'Mizuno', 'Merrell', 'Fila', 'Skechers', 'Timberland',
    'Birkenstock', 'Ugg', 'Onitsuka Tiger', 'Veja',
    'The North Face', 'Crocs', 'Li-Ning', 'Anta',
    '361 Degrees', 'Rigorer', 'Peak',
    # Luxe / Hype
    'Yzy', 'Off-White', 'Balenciaga', 'Gucci', 'Dior',
    'Louis Vuitton', 'Common Projects', 'Palm Angels',
    'A Bathing Ape', 'Kith', 'Supreme', 'Casablanca',
    'Comme Des Garcons', 'Maison Mihara Yasuhiro',
    'Alexander Mcqueen', 'Burberry', 'Fendi', 'Mschf',
    'Sp5Der', 'Denim Tears',
    # Autres
    'Dr. Martens', 'Clarks', 'Teva', 'Sprayground',
    'Mitchell & Ness', 'Canada Goose',
]

def detect_brand(name):
    name_lower = name.lower()
    # Jordan AVANT Nike !
    if 'jordan' in name_lower or 'air jordan' in name_lower:
        return 'Jordan'
    if 'yeezy' in name_lower or 'yzy' in name_lower:
        return 'Yzy'
    for brand in BRANDS:
        if brand.lower() in name_lower:
            return brand
    return 'Unknown'

# ══════════════════════════════════════════════════════════════
# SCRAPER FOOTLOCKER
# ══════════════════════════════════════════════════════════════
def scrape_footlocker():
    print("\n🕷️ Scraping Footlocker avec Playwright...")
    products = []

    # URLs par marque — chaque marque a ses propres modèles
    BRAND_URLS = [
        # ── Nike ──────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/nike.html?start=0&size=48",
        "https://www.footlocker.fr/fr/category/homme/nike.html?start=48&size=48",
        "https://www.footlocker.fr/fr/category/homme/nike.html?start=96&size=48",
        "https://www.footlocker.fr/fr/category/femme/nike.html?start=0&size=48",
        "https://www.footlocker.fr/fr/category/femme/nike.html?start=48&size=48",

        # ── Jordan ────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/jordan.html?start=0&size=48",
        "https://www.footlocker.fr/fr/category/homme/jordan.html?start=48&size=48",
        "https://www.footlocker.fr/fr/category/femme/jordan.html?start=0&size=48",

        # ── Adidas ────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/adidas.html?start=0&size=48",
        "https://www.footlocker.fr/fr/category/homme/adidas.html?start=48&size=48",
        "https://www.footlocker.fr/fr/category/femme/adidas.html?start=0&size=48",

        # ── New Balance ───────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/new-balance.html?start=0&size=48",
        "https://www.footlocker.fr/fr/category/homme/new-balance.html?start=48&size=48",
        "https://www.footlocker.fr/fr/category/femme/new-balance.html?start=0&size=48",

        # ── Asics ─────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/asics.html?start=0&size=48",
        "https://www.footlocker.fr/fr/category/femme/asics.html?start=0&size=48",

        # ── Puma ──────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/puma.html?start=0&size=48",
        "https://www.footlocker.fr/fr/category/femme/puma.html?start=0&size=48",

        # ── Reebok ────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/reebok.html?start=0&size=48",

        # ── Converse ──────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/converse.html?start=0&size=48",
        "https://www.footlocker.fr/fr/category/femme/converse.html?start=0&size=48",

        # ── Vans ──────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/vans.html?start=0&size=48",

        # ── Salomon ───────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/salomon.html?start=0&size=48",

        # ── Hoka ──────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/hoka.html?start=0&size=48",
        "https://www.footlocker.fr/fr/category/femme/hoka.html?start=0&size=48",

        # ── Saucony ───────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/saucony.html?start=0&size=48",

        # ── Under Armour ──────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/under-armour.html?start=0&size=48",

        # ── Timberland ────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/timberland.html?start=0&size=48",

        # ── On ────────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/on.html?start=0&size=48",

        # ── Lacoste ───────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/lacoste.html?start=0&size=48",

        # ── Mizuno ────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/mizuno.html?start=0&size=48",

        # ── DC Shoes ──────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/dc-shoes.html?start=0&size=48",

        # ── Crocs ─────────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/crocs.html?start=0&size=48",

        # ── Birkenstock ───────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/birkenstock.html?start=0&size=48",

        # ── Skechers ──────────────────────────────────────────────
        "https://www.footlocker.fr/fr/category/homme/skechers.html?start=0&size=48",
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
        )
        page = context.new_page()

        for url in BRAND_URLS:
            print(f"\n  📄 {url}")

            try:
                page.goto(url, timeout=30000, wait_until='networkidle')
                time.sleep(2)

                # Fermer cookie banner
                try:
                    cookie_btn = page.query_selector(
                        'button:has-text("TOUT REFUSER"), '
                        'button[id*="reject"], '
                        'button[title*="REFUSER"]'
                    )
                    if cookie_btn:
                        cookie_btn.click()
                        time.sleep(1)
                        print("  🍪 Cookie fermé")
                except:
                    pass

                # Attendre les produits
                try:
                    page.wait_for_selector(
                        'div[class*="ProductCard"], div[class*="product"]',
                        timeout=10000
                    )
                except:
                    print(f"  ⚠️ Timeout sélecteur — on continue")

                # Récupérer UNIQUEMENT les produits de la grille principale
                items = page.query_selector_all(
                    'div[class*="ProductCard"]:not([class*="carousel"]):not([class*="similar"]), '
                    'li[class*="product-grid"] div[class*="product"]'
                )

                # Fallback si pas de résultats
                if not items:
                    items = page.query_selector_all('div[class*="ProductCard"]')

                print(f"  🔍 {len(items)} éléments trouvés")

                page_products = []
                seen_on_page = set()

                for item in items:
                    try:
                        # ── Nom ──────────────────────────────────────────
                        name_el = item.query_selector(
                            '[class*="ProductName"], [class*="product-name"], '
                            'h3, h2, [class*="title"]'
                        )
                        name = name_el.inner_text().strip() if name_el else ''

                        # ── Brand ─────────────────────────────────────────
                        brand_el = item.query_selector(
                            '[class*="ProductBrand"], [class*="brand"], '
                            '[class*="vendor"]'
                        )
                        brand = brand_el.inner_text().strip() if brand_el else ''

                        # ── Prix ──────────────────────────────────────────
                        price_el = item.query_selector(
                            '[class*="ProductPrice"], [class*="price"]'
                        )
                        price_text = price_el.inner_text() if price_el else '0'
                        price_nums = re.findall(r'\d+[.,]?\d*', price_text.replace(',', '.'))
                        price_val = float(price_nums[0]) if price_nums else 0

                        # ── URL ───────────────────────────────────────────
                        link = item.query_selector('a')
                        href = link.get_attribute('href') if link else ''
                        full_url = (
                            f"https://www.footlocker.fr{href}"
                            if href and href.startswith('/') else href
                        )

                        # ── Image ─────────────────────────────────────────
                        img = item.query_selector('img')
                        img_src = img.get_attribute('src') if img else ''

                        # ── Validation ───────────────────────────────────
                        if not name and href:
                            slug = href.split('/product/')[-1].split('/')[0]
                            name = slug.replace('-', ' ').title()

                        if not name:
                            continue

                        if not price_val or price_val <= 0:
                            price_val = 100

                        # Détecter la marque
                        final_brand = detect_brand(name)
                        if not final_brand or final_brand == 'Unknown':
                            if brand:
                                final_brand = brand.strip().title()

                        # Dédup sur la page par nom+prix
                        page_key = f"{name.lower()}_{price_val}"
                        if page_key in seen_on_page:
                            continue
                        seen_on_page.add(page_key)

                        page_products.append({
                            'source':       'footlocker',
                            'name':         name,
                            'brand':        final_brand,
                            'price':        price_val,
                            'currency':     'EUR',
                            'url':          full_url,
                            'image':        img_src,
                            'ingested_at':  datetime.now().isoformat(),
                            'source_layer': 'bronze',
                        })

                    except:
                        continue

                print(f"  ✅ {len(page_products)} produits uniques sur cette page")
                products.extend(page_products)

            except Exception as e:
                print(f"  ❌ Erreur : {e}")
                continue

            time.sleep(2)  # Pause entre pages

        browser.close()

    # ── Déduplication globale par nom+prix ──────────────────
    seen_global = set()
    unique_products = []
    for p in products:
        key = f"{p['name'].lower()}_{p['price']}"
        if key not in seen_global:
            seen_global.add(key)
            unique_products.append(p)

    # ── Sauvegarde Bronze ────────────────────────────────────
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output = f'data/bronze/footlocker_raw_{timestamp}.json'
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(unique_products, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(unique_products)} produits uniques Footlocker → {output}")

    # Stats par marque
    from collections import Counter
    brands = Counter(p['brand'] for p in unique_products)
    print("\n📊 Par marque :")
    for b, c in brands.most_common(10):
        print(f"  {b}: {c}")

    return unique_products

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 50)
    print("   SNEAKERZ — REAL SCRAPING")
    print("=" * 50)

    fl = scrape_footlocker()
    kc = scrape_kickscrew()

    total = len(fl) + len(kc)
    print(f"\n{'='*50}")
    print(f"  TOTAL      : {total} produits scrapés !")
    print(f"  Footlocker : {len(fl)}")
    print(f"  KicksCrew  : {len(kc)}")
    print(f"{'='*50}")