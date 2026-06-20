# RetailFlow — Infrastructure et opérations

Ce document décrit les éléments principaux d’exploitation de la plateforme RetailFlow : configuration, services Docker, healthchecks, sauvegarde/restauration PostgreSQL et accès read-only.

L’objectif est de fournir une base claire pour l’exploitation locale, la démonstration technique et la soutenance du projet.

---

## 1. Configuration d’environnement

Le fichier `.env.example` sert de modèle de configuration.

Il documente les principales variables utilisées par la plateforme :

- PostgreSQL applicatif ;
- PostgreSQL Airflow ;
- pgAdmin ;
- Redpanda / Kafka ;
- FastAPI ;
- Streamlit ;
- Airflow ;
- Prometheus ;
- Grafana ;
- scripts de backup.

Le fichier `.env.example` est versionné dans Git.

Le fichier `.env`, s’il est créé localement, ne doit pas contenir de secrets de production et ne doit pas être commité.

Dans l’état actuel du projet, la démo locale fonctionne même sans `.env`, car les valeurs nécessaires sont déjà définies dans `docker-compose.yml`.

---

## 2. Services Docker principaux

La plateforme est orchestrée avec Docker Compose.

Services principaux :

| Service | Rôle | Port local |
|---|---|---:|
| `postgres` | Base PostgreSQL applicative RetailFlow | `5432` |
| `pgadmin` | Interface d’administration PostgreSQL | `5050` |
| `redpanda` | Broker Kafka-compatible pour événements temps réel | `9092`, `19092`, `9644` |
| `fastapi` | API backend RetailFlow | `8000` |
| `event_consumer` | Consumer Kafka vers PostgreSQL | interne |
| `streamlit` | Interface de démonstration | `8501` |
| `airflow-webserver` | Interface Airflow | `8080` |
| `airflow-scheduler` | Planification des DAGs Airflow | interne |
| `prometheus` | Collecte de métriques | `9090` |
| `grafana` | Dashboards de monitoring | `3000` |
| `postgres_exporter` | Exporter métriques PostgreSQL | `9187` |

Commande de vérification :

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## 3. Healthchecks

Des healthchecks Docker sont configurés pour les services cœur :

| Service | Healthcheck |
|---|---|
| `postgres` | `pg_isready` sur `retailflow_db` |
| `redpanda` | `rpk cluster info` |
| `fastapi` | appel HTTP sur `/openapi.json` |
| `streamlit` | appel HTTP sur `/_stcore/health` |
| `airflow_postgres` | `pg_isready` sur la base Airflow |

Ces healthchecks permettent de démontrer que les services principaux ne sont pas seulement démarrés, mais réellement disponibles.

Commandes utiles :

```bash
docker compose config --quiet
docker compose up -d
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Vérification API :

```bash
curl -s http://localhost:8000/openapi.json | head
```

Vérification Streamlit :

```bash
curl -s http://localhost:8501/_stcore/health
```

---

## 4. Sauvegarde PostgreSQL

Le projet fournit un script de sauvegarde PostgreSQL :

```bash
scripts/postgres_backup.sh
```

Il crée un backup compressé au format custom PostgreSQL dans :

```text
backups/postgres/
```

Exemple :

```bash
./scripts/postgres_backup.sh
```

Le fichier généré suit le format :

```text
retailflow_db_YYYYmmdd_HHMMSS.dump
```

Les fichiers `.dump` ne sont pas versionnés dans Git. Le dossier `backups/postgres` contient un `.gitignore` pour éviter de commiter des sauvegardes de données.

Variables supportées :

| Variable | Valeur par défaut |
|---|---|
| `POSTGRES_CONTAINER_NAME` | `retailflow_postgres` |
| `POSTGRES_USER` | `retailflow` |
| `POSTGRES_DB` | `retailflow_db` |
| `BACKUP_DIR` | `backups/postgres` |
| `BACKUP_RETENTION_DAYS` | `7` |

---

## 5. Restauration PostgreSQL

Le projet fournit un script de restauration :

```bash
scripts/postgres_restore.sh
```

Utilisation :

```bash
./scripts/postgres_restore.sh backups/postgres/retailflow_db_YYYYmmdd_HHMMSS.dump
```

Le script demande une confirmation manuelle :

```text
Type RESTORE to continue:
```

Cette protection évite une restauration accidentelle.

Le restore utilise :

```bash
pg_restore --clean --if-exists --no-owner --no-privileges
```

Cela permet de restaurer les objets de base en supprimant d’abord les objets existants lorsque nécessaire.

---

## 6. Rôle PostgreSQL read-only

Un rôle PostgreSQL lecture seule est défini dans :

```text
database/init/05_create_readonly_role.sql
```

Rôle :

```text
retailflow_readonly
```

Mot de passe local de démonstration :

```text
readonly
```

Ce rôle dispose de droits :

- `CONNECT` sur la base `retailflow_db` ;
- `USAGE` sur les schémas `raw`, `core`, `analytics`, `governance` ;
- `SELECT` sur les tables existantes ;
- `SELECT` par défaut sur les futures tables des schémas concernés.

Il ne dispose pas de droits d’écriture.

Test de lecture :

```bash
docker exec -it retailflow_postgres psql \
  "postgresql://retailflow_readonly:readonly@localhost:5432/retailflow_db" \
  -c "SELECT COUNT(*) FROM core.customers;"
```

Test d’écriture attendu en échec :

```bash
docker exec -it retailflow_postgres psql \
  "postgresql://retailflow_readonly:readonly@localhost:5432/retailflow_db" \
  -c "INSERT INTO core.customers (customer_id) VALUES ('cust_readonly_test');"
```

Résultat attendu :

```text
ERROR: permission denied for table customers
```

Cette erreur est normale et prouve que le rôle est bien limité en lecture seule.

---

## 7. Commandes de vérification rapides

Valider Docker Compose :

```bash
docker compose config --quiet
```

Voir l’état des services :

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Vérifier PostgreSQL :

```bash
docker exec -it retailflow_postgres psql -U retailflow -d retailflow_db -c "SELECT COUNT(*) FROM core.customers;"
```

Vérifier Redpanda :

```bash
docker exec -it retailflow_redpanda rpk cluster info
```

Vérifier FastAPI :

```bash
curl -s http://localhost:8000/openapi.json | head
```

Vérifier Streamlit :

```bash
curl -s http://localhost:8501/_stcore/health
```

Lancer les tests Python :

```bash
python -m pytest tests/test_*.py -q
```

---

## 8. Limites actuelles

Cette infrastructure est conçue pour une démonstration locale complète.

Limites connues par rapport à une production réelle :

- mots de passe de démonstration présents dans `docker-compose.yml` ;
- pas de TLS activé entre services ;
- pas de haute disponibilité PostgreSQL ;
- pas de cluster Redpanda multi-nœuds ;
- pas de gestion de secrets type Vault ou Docker secrets ;
- healthchecks Prometheus/Grafana non encore ajoutés ;
- pas encore de base PostgreSQL dédiée aux tests d’intégration API.

Ces limites sont assumées dans le cadre d’un projet de Master, mais elles sont identifiées et peuvent être présentées comme des axes d’amélioration production.

---

## 9. Positionnement soutenance

Les éléments ajoutés permettent de démontrer :

- une configuration d’environnement documentée ;
- une base de données sauvegardable et restaurable ;
- des services critiques supervisés par healthchecks ;
- une séparation entre compte applicatif et compte lecture seule ;
- une première approche du principe du moindre privilège ;
- une exploitation locale reproductible.
