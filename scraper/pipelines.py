import json
import os
from datetime import datetime

class BronzePipeline:
    """Sauvegarde les données brutes telles quelles — couche Bronze"""
    
    def open_spider(self, spider):
        os.makedirs('data/bronze', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/bronze/{spider.name}_raw_{timestamp}.json"
        self.file = open(filename, 'w', encoding='utf-8')
        self.items = []
        spider.logger.info(f"[BRONZE] Fichier ouvert : {filename}")

    def process_item(self, item, spider):
        # Aucune transformation — données brutes
        item['ingested_at'] = datetime.now().isoformat()
        item['source_layer'] = 'bronze'
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        json.dump(self.items, self.file, ensure_ascii=False, indent=2)
        self.file.close()
        spider.logger.info(f"[BRONZE] {len(self.items)} items sauvegardés")