# 👟 Sneakerz

Plateforme Big Data temps réel d'analyse du marché sneakers.

## 🎯 Objectif
Collecter, transformer et analyser les prix retail vs revente 
des sneakers pour aider les revendeurs à maximiser leurs marges.

## 🏗️ Architecture
- **Scraping** : Python + Scrapy (KicksCrew, Footlocker)
- **Ingestion** : Apache Kafka + Airflow
- **Data Lake** : MinIO
- **Médaillon** : Bronze / Silver / Gold
- **Transformation** : PySpark + dbt
- **Data Warehouse** : PostgreSQL
- **Backend** : FastAPI
- **Frontend** : React.js

## 🚀 Lancer le projet
```bash
docker-compose up
```
