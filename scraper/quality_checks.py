import json
import os
import glob
from datetime import datetime

# ── Résultats des tests ───────────────────────────────────────
results = {
    'run_at': datetime.now().isoformat(),
    'tests': [],
    'total': 0,
    'passed': 0,
    'failed': 0,
}

def test(name, condition, detail=""):
    """Exécute un test et enregistre le résultat"""
    status = "✅ PASS" if condition else "❌ FAIL"
    results['tests'].append({
        'test': name,
        'status': 'PASS' if condition else 'FAIL',
        'detail': detail
    })
    results['total'] += 1
    if condition:
        results['passed'] += 1
    else:
        results['failed'] += 1
    print(f"{status} — {name} {f'({detail})' if detail else ''}")
    return condition

# ════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════")
print("   SNEAKERZ — QUALITY CHECKS")
print("══════════════════════════════════════\n")

# ── 1. BRONZE ────────────────────────────────────────────────
print("🥉 BRONZE")
bronze_files = glob.glob('data/bronze/*.json')
test("Bronze — fichiers existent", len(bronze_files) > 0,
     f"{len(bronze_files)} fichier(s)")

if bronze_files:
    all_bronze = []
    for f in bronze_files:
        with open(f, encoding='utf-8') as fp:
            all_bronze.extend(json.load(fp))

    test("Bronze — données non vides",
         len(all_bronze) > 0, f"{len(all_bronze)} items")

    missing_url = [i for i in all_bronze if not i.get('url')]
    test("Bronze — URLs présentes",
         len(missing_url) == 0, f"{len(missing_url)} manquantes")

    missing_source = [i for i in all_bronze if not i.get('source')]
    test("Bronze — Source présente",
         len(missing_source) == 0, f"{len(missing_source)} manquantes")

    missing_date = [i for i in all_bronze if not i.get('ingested_at')]
    test("Bronze — Date ingestion présente",
         len(missing_date) == 0, f"{len(missing_date)} manquantes")

# ── 2. SILVER ────────────────────────────────────────────────
print("\n🥈 SILVER")
silver_files = glob.glob('data/silver/*.json')
test("Silver — fichiers existent",
     len(silver_files) > 0, f"{len(silver_files)} fichier(s)")

if silver_files:
    with open(silver_files[-1], encoding='utf-8') as f:
        silver = json.load(f)

    test("Silver — données non vides",
         len(silver) > 0, f"{len(silver)} items")

    # Complétude
    no_name = [i for i in silver if not i.get('name')]
    test("Silver — Complétude : nom présent",
         len(no_name) == 0, f"{len(no_name)} manquants")

    no_brand = [i for i in silver if not i.get('brand')]
    test("Silver — Complétude : marque présente",
         len(no_brand) == 0, f"{len(no_brand)} manquantes")

    no_price = [i for i in silver if not i.get('price_retail')]
    test("Silver — Complétude : prix présent",
         len(no_price) == 0, f"{len(no_price)} manquants")

    # Validité
    neg_price = [i for i in silver if i.get('price_retail', 0) <= 0]
    test("Silver — Validité : prix positif",
         len(neg_price) == 0, f"{len(neg_price)} négatifs")

    valid_sources = ['kickscrew', 'footlocker']
    bad_source = [i for i in silver
                  if i.get('source') not in valid_sources]
    test("Silver — Validité : source connue",
         len(bad_source) == 0, f"{len(bad_source)} invalides")

    # Cohérence
    bad_url = [i for i in silver
               if i.get('url') and not i['url'].startswith('http')]
    test("Silver — Cohérence : URL valide",
         len(bad_url) == 0, f"{len(bad_url)} invalides")

    # Unicité
    names = [i['name'] for i in silver if i.get('name')]
    unique_names = set(names)
    test("Silver — Unicité : pas de doublons",
         len(names) == len(unique_names),
         f"{len(names) - len(unique_names)} doublons")

    # Score qualité global
    scores = []
    for item in silver:
        score = 0
        if item.get('name'):         score += 25
        if item.get('brand'):        score += 25
        if item.get('price_retail'): score += 25
        if item.get('url'):          score += 25
        scores.append(score)
    avg_score = sum(scores) / len(scores) if scores else 0
    test("Silver — Score qualité moyen ≥ 75",
         avg_score >= 75, f"Score moyen : {avg_score:.1f}/100")

# ── 3. GOLD ───────────────────────────────────────────────────
print("\n🥇 GOLD")
gold_files = glob.glob('data/gold/*.json')
test("Gold — fichiers existent",
     len(gold_files) > 0, f"{len(gold_files)} fichier(s)")

if gold_files:
    with open(max(gold_files, key=os.path.getctime)) as f:
        gold = json.load(f)

    margins = gold.get('all_margins', [])
    test("Gold — marges calculées",
         len(margins) > 0, f"{len(margins)} marges")

    neg_margin = [m for m in margins if m.get('margin_value', 0) <= 0]
    test("Gold — Validité : marges positives",
         len(neg_margin) == 0, f"{len(neg_margin)} négatives")

    no_brand = [m for m in margins if not m.get('brand')]
    test("Gold — Complétude : marque présente",
         len(no_brand) == 0, f"{len(no_brand)} manquantes")

    stats = gold.get('stats', {})
    test("Gold — Stats générées",
         bool(stats), f"avg_margin: {stats.get('avg_margin_percent', 0)}%")

# ── RÉSUMÉ ────────────────────────────────────────────────────
print("\n══════════════════════════════════════")
print(f"   RÉSULTATS : {results['passed']}/{results['total']} tests passés")
score = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
print(f"   SCORE QUALITÉ : {score:.0f}%")
if results['failed'] == 0:
    print("   STATUS : ✅ TOUTES LES DONNÉES SONT VALIDES")
else:
    print(f"   STATUS : ⚠️  {results['failed']} TEST(S) ÉCHOUÉ(S)")
print("══════════════════════════════════════\n")

# Sauvegarde rapport qualité
os.makedirs('data/quality', exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
report_path = f'data/quality/report_{timestamp}.json'
results['score'] = round(score, 1)
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"📄 Rapport sauvegardé : {report_path}")
