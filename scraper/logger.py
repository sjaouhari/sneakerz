import json
import os
from datetime import datetime
from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin123",
    secure=False
)

def log_pipeline(stage, status, details={}):
    """Sauvegarde un log de pipeline dans MinIO"""
    
    log = {
        'timestamp': datetime.now().isoformat(),
        'stage': stage,
        'status': status,
        'details': details
    }
    
    # Sauvegarde local
    os.makedirs('data/logs', exist_ok=True)
    log_file = f"data/logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump(log, f, indent=2)
    
    # Upload MinIO
    try:
        object_name = f"{datetime.now().strftime('%Y/%m/%d')}/{os.path.basename(log_file)}"
        client.fput_object('logs', object_name, log_file)
        print(f"📝 Log sauvegardé : {stage} → {status}")
    except Exception as e:
        print(f"⚠️ Log MinIO error: {e}")

if __name__ == "__main__":
    # Test
    log_pipeline('scraping',        'success', {'products': 949, 'source': 'footlocker'})
    log_pipeline('bronze_to_silver','success', {'items': 949})
    log_pipeline('silver_to_gold',  'success', {'margins': 949})
    log_pipeline('gold_to_postgres','success', {'loaded': 949})
    log_pipeline('quality_checks',  'success', {'score': '95%', 'tests': '19/20'})
    print("\n✅ Logs générés !")