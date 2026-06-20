# RetailFlow — Documentation CI/CD

Ce document décrit la chaîne CI/CD mise en place pour le projet RetailFlow.

L’objectif est de montrer comment le projet est validé automatiquement à chaque changement de code, avec des contrôles de syntaxe, de tests, de qualité repository, de configuration Docker Compose et de build Docker.

---

## 1. Emplacement du workflow

Le workflow GitHub Actions principal est défini ici :

```text
.github/workflows/ci.yml
```

Nom du workflow :

```text
RetailFlow CI
```

Il s’exécute automatiquement sur :

```yaml
push:
  branches:
    - develop
    - "feature/**"

pull_request:
  branches:
    - develop
```

Cela signifie que la CI se lance :

- à chaque push sur `develop` ;
- à chaque push sur une branche `feature/**` ;
- à chaque pull request vers `develop`.

---

## 2. Objectifs de la CI

La CI RetailFlow vise à vérifier automatiquement que :

- le code Python est syntaxiquement valide ;
- les tests automatisés passent ;
- un rapport JUnit de tests est généré ;
- les fichiers JSON versionnés sont valides ;
- les scripts Bash sont syntaxiquement valides ;
- la configuration Docker Compose est valide ;
- les images Docker principales peuvent être construites.

Ces contrôles permettent de détecter rapidement les régressions avant une démonstration ou une intégration sur la branche principale de développement.

---

## 3. Jobs GitHub Actions

Le workflow est organisé en plusieurs jobs.

### 3.1 `python-tests`

Nom affiché :

```text
Python tests and syntax checks
```

Ce job réalise les étapes suivantes :

1. checkout du dépôt ;
2. installation de Python 3.11 ;
3. activation du cache pip ;
4. mise à jour de `pip`, `setuptools` et `wheel` ;
5. installation des dépendances Python ;
6. vérification de la syntaxe Python ;
7. exécution des tests avec génération d’un rapport JUnit ;
8. upload du rapport de tests en artefact GitHub Actions.

Commandes principales :

```bash
python -m compileall api ml pipeline data_generator tests streamlit_app
python -m pytest tests/test_*.py -q --junitxml=reports/ci/pytest-results.xml
```

Artefact généré :

```text
pytest-results
```

Fichier contenu dans l’artefact :

```text
reports/ci/pytest-results.xml
```

---

### 3.2 `repository-quality-checks`

Nom affiché :

```text
Repository quality checks
```

Ce job vérifie la qualité minimale du dépôt.

Contrôles réalisés :

- validation des fichiers JSON ;
- validation syntaxique des scripts Bash.

Les dossiers ignorés pendant la validation JSON sont notamment :

- `.git` ;
- `.venv` ;
- `venv` ;
- `__pycache__` ;
- `backups` ;
- `airflow/logs`.

Cette exclusion évite de valider des fichiers temporaires, locaux ou générés à l’exécution.

Validation Bash :

```bash
bash -n scripts/postgres_backup.sh
bash -n scripts/postgres_restore.sh
```

L’objectif n’est pas d’exécuter les scripts, mais de vérifier qu’ils ne contiennent pas d’erreur de syntaxe.

---

### 3.3 `docker-compose-validation`

Nom affiché :

```text
Docker Compose validation
```

Ce job vérifie que le fichier Docker Compose est valide.

Commande utilisée :

```bash
docker compose config --quiet
```

Cette commande échoue si la configuration Compose contient une erreur de syntaxe, une mauvaise indentation ou une structure invalide.

---

### 3.4 `docker-build`

Nom affiché :

```text
Docker image build validation
```

Ce job dépend des jobs précédents :

```yaml
needs:
  - python-tests
  - repository-quality-checks
  - docker-compose-validation
```

Il ne s’exécute donc que si les tests, les contrôles repository et la validation Docker Compose sont passés.

Images construites :

```bash
docker build -t retailflow-api-ci -f api/Dockerfile .
docker build -t retailflow-streamlit-ci -f streamlit_app/Dockerfile .
docker build -t retailflow-consumer-ci -f pipeline/consumer/Dockerfile .
```

Ce job prouve que les trois composants principaux peuvent être reconstruits dans un environnement CI propre :

- FastAPI ;
- Streamlit ;
- consumer pipeline Kafka/PostgreSQL.

---

## 4. Dépendances installées pendant la CI

Le job Python installe les dépendances depuis plusieurs fichiers :

```text
requirements.txt
requirements-dev.txt
api/requirements.txt
ml/requirements.txt
pipeline/requirements.txt
streamlit_app/requirements.txt
```

Cela permet de couvrir les différentes parties du projet :

- API ;
- machine learning ;
- pipeline ;
- application Streamlit ;
- tests ;
- dépendances transverses.

---

## 5. Stratégie de branches

La branche principale de développement est :

```text
develop
```

Les branches de travail recommandées suivent le format :

```text
feature/<nom-du-lot-ou-de-la-feature>
```

Exemples :

```text
feature/lot1-code-improvements
feature/lot2-infra
feature/lot3-ci-cd
```

La CI est déclenchée automatiquement sur ces branches, ce qui permet de vérifier les changements avant fusion vers `develop`.

---

## 6. Artefacts CI

La CI publie un artefact de test :

```text
pytest-results
```

Il contient le rapport JUnit :

```text
reports/ci/pytest-results.xml
```

Ce rapport peut être utilisé pour :

- prouver l’exécution des tests ;
- analyser les erreurs en cas d’échec ;
- documenter le niveau de validation automatisée du projet.

Le dossier local `reports/` est ignoré par Git afin d’éviter de versionner les rapports générés localement.

---

## 7. Commandes équivalentes en local

Avant de pousser du code, il est possible de reproduire les principaux contrôles CI en local.

Syntaxe Python :

```bash
python -m compileall api ml pipeline data_generator tests streamlit_app
```

Tests Python avec rapport JUnit :

```bash
mkdir -p reports/ci
python -m pytest tests/test_*.py -q --junitxml=reports/ci/pytest-results.xml
```

Validation Docker Compose :

```bash
docker compose config --quiet
```

Validation Bash :

```bash
bash -n scripts/postgres_backup.sh
bash -n scripts/postgres_restore.sh
```

Validation JSON ciblée :

```bash
python -m json.tool ml/model_registry.json >/dev/null
python -m json.tool ml/reports/retraining_runs.json >/dev/null
python -m json.tool pipeline/reports/pipeline_metrics.json >/dev/null
```

---

## 8. Dernier état validé

À la date de mise à jour de ce document, le workflow GitHub Actions le plus récent sur `develop` est vert.

Le dernier run validé correspond au commit :

```text
make model registry tests CI compatible
```

Ce commit corrige les tests de registre ML pour être compatibles avec la CI distante, où les artefacts `.joblib` ne sont pas versionnés dans Git.

Cette correction est normale : les modèles `.joblib` existent en local après entraînement, mais ils sont ignorés par Git pour éviter de versionner des artefacts binaires.

---

## 9. Limites actuelles de la CI/CD

La CI actuelle est volontairement légère et adaptée à un projet de démonstration Master.

Limites connues :

- pas de déploiement automatique vers un environnement distant ;
- pas de scan de sécurité bloquant avec `pip-audit` ou équivalent ;
- pas de base PostgreSQL de test dédiée pour les tests d’intégration API ;
- pas de tests end-to-end Streamlit ;
- pas de publication d’image Docker vers un registry ;
- pas de gestion de secrets de production ;
- pas de stratégie de promotion entre environnements `dev`, `staging`, `prod`.

Ces limites peuvent être présentées comme des axes d’évolution production.

---

## 10. Axes d’amélioration possibles

Améliorations futures recommandées :

1. ajouter un job de sécurité non bloquant avec `pip-audit` ;
2. ajouter une base PostgreSQL de test pour les endpoints API dépendants de la DB ;
3. ajouter des tests d’intégration API plus complets ;
4. publier les images Docker dans GitHub Container Registry ;
5. ajouter un environnement de staging ;
6. ajouter une étape de déploiement contrôlé ;
7. ajouter un badge CI dans le README ;
8. ajouter une politique de protection de branche sur `develop`.

---

## 11. Positionnement soutenance

La CI/CD RetailFlow permet de démontrer :

- une automatisation des tests ;
- une validation continue du code ;
- une validation de la configuration Docker ;
- une validation des scripts d’exploitation ;
- une capacité à reconstruire les images applicatives ;
- une traçabilité des résultats de tests via artefact JUnit ;
- une base réaliste pour une industrialisation future.

Même sans déploiement automatique complet, la chaîne CI actuelle couvre les contrôles essentiels attendus pour un projet data/IA industrialisé.
