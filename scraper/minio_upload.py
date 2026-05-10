from minio import Minio
from minio.error import S3Error
import os
import glob
from datetime import datetime

# Connexion MinIO
client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin123",
    secure=False
)

BUCKETS = ['bronze', 'silver', 'gold', 'logs', 'quality']

def init_buckets():
    """Crée les buckets s'ils n'existent pas"""
    for bucket in BUCKETS:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            print(f"✅ Bucket '{bucket}' créé")
        else:
            print(f"  Bucket '{bucket}' existe déjà")

def upload_layer(layer, pattern):
    """Upload les fichiers d'une couche vers MinIO"""
    files = glob.glob(f'data/{layer}/{pattern}')
    if not files:
        print(f"  ⚠️ Aucun fichier {layer}")
        return
    
    for file_path in files:
        filename = os.path.basename(file_path)
        object_name = f"{datetime.now().strftime('%Y/%m/%d')}/{filename}"
        
        client.fput_object(
            layer,           # bucket
            object_name,     # chemin dans MinIO
            file_path,       # fichier local
        )
        print(f"  ✅ {layer}/{object_name} uploadé")

def upload_all():
    print("🚀 Upload vers MinIO Data Lake...")
    init_buckets()
    
    print("\n🥉 Bronze →")
    upload_layer('bronze', '*.json')
    
    print("\n🥈 Silver →")
    upload_layer('silver', '*.json')
    
    print("\n🥇 Gold →")
    upload_layer('gold', '*.json')
    
    print("\n📊 Quality →")
    upload_layer('quality', '*.json')
    
    print("\n✅ Data Lake MinIO prêt !")

if __name__ == "__main__":
    upload_all()