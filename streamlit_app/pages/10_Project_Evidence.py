import pandas as pd
import streamlit as st

from components import (
    load_css,
    section_title,
    info_card,
    proof_card,
    block_badges,
    technical_evidence,
    academic_mapping,
    footer_note,
)


st.set_page_config(
    page_title="RetailFlow Project Evidence",
    page_icon="📌",
    layout="wide",
)

load_css()


def skill(bloc, skill_id, competence, proof, tools, location, status="Démontré"):
    return {
        "Bloc": bloc,
        "ID": skill_id,
        "Compétence": competence,
        "Preuve RetailFlow": proof,
        "Outils": tools,
        "Où chercher": location,
        "Statut": status,
    }


def skill_sort_key(value: str):
    try:
        major, minor = str(value).replace("C", "").split(".")
        return int(major), int(minor)
    except Exception:
        return 999, 999


st.title("📌 Project Evidence")
block_badges(["Bloc 1", "Bloc 2", "Bloc 3", "Bloc 4"])

st.markdown(
    """
    Cette page sert de matrice finale de preuves pour la soutenance.
    Elle relie chaque critère important aux éléments concrets implémentés dans RetailFlow,
    avec les outils à ouvrir et les emplacements à montrer.
    """
)

section_title("Evidence overview")

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Covered blocks", 4)

with k2:
    st.metric("Main tools", "10+")

with k3:
    st.metric("Evidence pages", 10)

with k4:
    st.metric("Demo status", "Ready")

o1, o2, o3 = st.columns(3)

with o1:
    info_card(
        "Purpose",
        "Donner au jury une vue consolidée des preuves techniques, métier et académiques.",
    )

with o2:
    info_card(
        "Usage",
        "Utiliser cette page comme point d'entrée pour naviguer vers Streamlit, GitHub, Airflow, Grafana, Prometheus et pgAdmin.",
    )

with o3:
    info_card(
        "Positioning",
        "RetailFlow est présenté comme une plateforme démonstrative réaliste de retail intelligence.",
    )

section_title("Final evidence matrix")

evidence_rows = [
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Plan de gouvernance des données",
        "Preuve RetailFlow": "Cadre de gouvernance avec rôles, responsabilités, politiques de rétention, consentement et audit.",
        "Outils": "Streamlit, PostgreSQL, pgAdmin, VSCode",
        "Où chercher": "Streamlit > Data Governance ; VSCode > streamlit_app/pages/4_Data_Governance.py",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Parties prenantes et responsabilités",
        "Preuve RetailFlow": "Executive Sponsor, Governance Council, Data Owner, Data Steward, Data Custodian / IT, DPO, ML Engineer et Business Users.",
        "Outils": "Streamlit",
        "Où chercher": "Streamlit > Data Governance > Governance operating model",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Consentement et usages analytiques",
        "Preuve RetailFlow": "Suivi des consentements marketing, analytics et personalization ; affichage IA contrôlé par analytics consent.",
        "Outils": "Streamlit, FastAPI, PostgreSQL, pgAdmin",
        "Où chercher": "Streamlit > Data Governance > Consent management ; Streamlit > Customer Intelligence > Consent filter",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Rétention et anonymisation",
        "Preuve RetailFlow": "Politiques de rétention, actions d'anonymisation et journal d'audit.",
        "Outils": "Streamlit, PostgreSQL, pgAdmin, Airflow",
        "Où chercher": "Streamlit > Data Governance > Retention, anonymization and audit trail ; Airflow > retention_cleanup",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Gestion des violations et incidents",
        "Preuve RetailFlow": "Procédure breach response : detect, contain, assess, notify, correct, review.",
        "Outils": "Streamlit, VSCode",
        "Où chercher": "Streamlit > Data Governance > Breach response procedure",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Risques data et mitigation",
        "Preuve RetailFlow": "Registre de risques : exposition données personnelles, data quality, drift ML, accès non autorisé, incident opérationnel.",
        "Outils": "Streamlit",
        "Où chercher": "Streamlit > Data Governance > Data risk register",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Accessibilité et inclusion",
        "Preuve RetailFlow": "Interface structurée, textes courts, sections lisibles, navigation par pages et détails en expanders.",
        "Outils": "Streamlit",
        "Où chercher": "Streamlit > Data Governance > Accessibility and inclusion",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Architecture data",
        "Preuve RetailFlow": "Architecture PostgreSQL, Redpanda, FastAPI, Streamlit, Airflow, Prometheus et Grafana.",
        "Outils": "Streamlit, Docker Compose, VSCode",
        "Où chercher": "Streamlit > Data Architecture ; VSCode > docker-compose.yml",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Structure des données",
        "Preuve RetailFlow": "Schémas core, raw, analytics et governance avec tables métiers, événements, prédictions et logs qualité.",
        "Outils": "PostgreSQL, pgAdmin, VSCode",
        "Où chercher": "pgAdmin > retailflow_db ; VSCode > database/init/",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Scalabilité et découplage",
        "Preuve RetailFlow": "Découplage producer / broker / consumer avec Redpanda et services Docker indépendants.",
        "Outils": "Docker Compose, Redpanda, FastAPI, Streamlit",
        "Où chercher": "VSCode > docker-compose.yml ; Streamlit > Customer View > Event pipeline path",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Disponibilité et exploitation",
        "Preuve RetailFlow": "Healthchecks Docker, documentation d'exploitation, backup/restore PostgreSQL et monitoring Prometheus.",
        "Outils": "Docker Compose, Prometheus, VSCode",
        "Où chercher": "VSCode > docker-compose.yml ; VSCode > docs/INFRA_OPERATIONS.md ; Prometheus > Targets",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Sécurité technique",
        "Preuve RetailFlow": "Rôle readonly PostgreSQL, séparation des services, variables d'environnement exemple et contrôles de sécurité automatisés en CI.",
        "Outils": "PostgreSQL, GitHub Actions, VSCode",
        "Où chercher": "VSCode > database/init/ ; VSCode > .github/workflows/ ; GitHub > Actions",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Observabilité infrastructure",
        "Preuve RetailFlow": "Targets Prometheus, dashboards Grafana, alert rules et liens directs depuis Streamlit.",
        "Outils": "Streamlit, Prometheus, Grafana",
        "Où chercher": "Streamlit > Observability ; Prometheus > Targets ; Grafana > Dashboards",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Pipeline temps réel",
        "Preuve RetailFlow": "Génération d'événements depuis Streamlit, publication FastAPI, topic Redpanda, consumer Python et stockage PostgreSQL.",
        "Outils": "Streamlit, FastAPI, Redpanda, PostgreSQL",
        "Où chercher": "Streamlit > Customer View > Generate full demo journey ; FastAPI Docs > /events",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Contrôle des erreurs pipeline",
        "Preuve RetailFlow": "Événements invalides isolés dans governance.dead_letter_events avec raison du rejet et payload brut.",
        "Outils": "Streamlit, PostgreSQL, pgAdmin",
        "Où chercher": "Streamlit > Customer View > Generate invalid event ; Streamlit > Data Quality > Latest dead-letter evidence",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Traçabilité des événements",
        "Preuve RetailFlow": "event_id, event_type, customer_id, session_id, timestamp, raw_payload et dead_letter_id.",
        "Outils": "PostgreSQL, pgAdmin, Streamlit",
        "Où chercher": "pgAdmin > raw.events ; pgAdmin > governance.dead_letter_events ; Streamlit > Data Quality",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Qualité des données",
        "Preuve RetailFlow": "Page Data Quality avec dead-letter, synthèse des anomalies, règles qualité et workflow de remédiation.",
        "Outils": "Streamlit, PostgreSQL, Airflow",
        "Où chercher": "Streamlit > Data Quality ; Airflow > daily_data_quality",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Automatisation pipeline",
        "Preuve RetailFlow": "DAGs Airflow pour agrégation ventes, qualité quotidienne, cleanup rétention et retraining ML.",
        "Outils": "Airflow, VSCode",
        "Où chercher": "Airflow > DAGs ; VSCode > airflow/dags/",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Monitoring pipeline",
        "Preuve RetailFlow": "Alert rules Prometheus, dashboards Grafana, Data Quality page et logs consumer.",
        "Outils": "Prometheus, Grafana, Streamlit, Docker",
        "Où chercher": "Streamlit > Observability ; Prometheus > Alerts ; Grafana > RetailFlow dashboards",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Cas d'usage IA",
        "Preuve RetailFlow": "Churn prediction, CLV prediction et customer segmentation intégrés dans la plateforme.",
        "Outils": "Streamlit, FastAPI, Python ML",
        "Où chercher": "Streamlit > Customer Intelligence ; Streamlit > AI Monitoring",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Serving des prédictions",
        "Preuve RetailFlow": "Endpoints FastAPI IA utilisés par Streamlit pour afficher profils clients, churn, CLV et segments selon le consentement analytics.",
        "Outils": "FastAPI, Streamlit",
        "Où chercher": "FastAPI Docs > /ai ; Streamlit > Customer Intelligence",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Explicabilité métier",
        "Preuve RetailFlow": "Decision framework et recommended actions traduisent les prédictions en décisions métier.",
        "Outils": "Streamlit",
        "Où chercher": "Streamlit > Customer Intelligence > Decision framework",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Model registry",
        "Preuve RetailFlow": "Registre de modèles avec artefacts et métadonnées utilisé dans AI Monitoring.",
        "Outils": "Streamlit, VSCode",
        "Où chercher": "Streamlit > AI Monitoring > Model registry ; VSCode > ml/model_registry.json",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Rapports ML",
        "Preuve RetailFlow": "Rapports churn, CLV, segmentation, model summary et drift report visibles depuis Streamlit.",
        "Outils": "Streamlit, VSCode",
        "Où chercher": "Streamlit > AI Monitoring > Model reports ; VSCode > ml/reports/",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Retraining",
        "Preuve RetailFlow": "DAG Airflow de retraining et journal retraining_runs.json.",
        "Outils": "Airflow, Streamlit, VSCode",
        "Où chercher": "Airflow > ml_retraining ; Streamlit > AI Monitoring > Training and retraining evidence",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Robustesse et tests",
        "Preuve RetailFlow": "Tests unitaires, tests ML, tests de registry, compileall et CI GitHub Actions.",
        "Outils": "GitHub Actions, pytest, VSCode",
        "Où chercher": "GitHub > retailflow-platform > Actions ; VSCode > tests/ ; VSCode > ml/tests/",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "CI/CD et sécurité",
        "Preuve RetailFlow": "Workflow GitHub Actions avec tests, contrôles de sécurité automatisés, artefacts de rapports et documentation CI/CD.",
        "Outils": "GitHub Actions, VSCode",
        "Où chercher": "GitHub > Actions ; VSCode > .github/workflows/ ; VSCode > docs/CI_CD.md",
        "Statut": "Implémenté",
    },
]

df_evidence = pd.DataFrame(evidence_rows)

selected_blocs = st.multiselect(
    "Filter by bloc",
    sorted(df_evidence["Bloc"].unique().tolist()),
    default=sorted(df_evidence["Bloc"].unique().tolist()),
    key="evidence_bloc_filter",
)

filtered_df = df_evidence[df_evidence["Bloc"].isin(selected_blocs)].copy()

st.dataframe(filtered_df, use_container_width=True, hide_index=True)

section_title("Skills evidence matrix")

skills_rows = [
    skill("Bloc 1", "C1.1", "Le plan mentionne explicitement le RGPD, l'ISO 27001 ou d'autres réglementations pertinentes.", "La page Data Governance contient une section Regulatory alignment avec RGPD, ISO 27001 mindset, accessibility et accountability.", "Streamlit, VSCode", "Streamlit > Data Governance > Regulatory alignment"),
    skill("Bloc 1", "C1.2", "Le plan décrit les mécanismes de conformité et tient compte de l'accessibilité et de l'inclusion.", "Consentement, rétention, anonymisation, audit trail et accessibilité sont présentés dans la page Data Governance.", "Streamlit, PostgreSQL", "Streamlit > Data Governance > Compliance mechanisms ; Accessibility and inclusion"),
    skill("Bloc 1", "C1.3", "Le plan inclut des procédures de conformité : audits réguliers, formations, contrôles.", "Le lifecycle governance couvre define, implement, monitor, audit et improve ; les mécanismes d'audit sont visibles via retention actions et quality logs.", "Streamlit, PostgreSQL, Airflow", "Streamlit > Data Governance > Governance lifecycle"),
    skill("Bloc 1", "C1.4", "Le plan prévoit des procédures pour gérer les violations réglementaires.", "La procédure breach response décrit detect, contain, assess, notify, correct et review.", "Streamlit", "Streamlit > Data Governance > Breach response procedure"),
    skill("Bloc 1", "C1.5", "Le plan inclut des mécanismes de mise à jour régulière de la conformité.", "La gouvernance prévoit une revue périodique par le DPO et le Governance Council avec mise à jour documentaire.", "Streamlit", "Streamlit > Data Governance > Governance lifecycle"),
    skill("Bloc 1", "C2.1", "Le plan identifie clairement les parties prenantes.", "Les parties prenantes incluent Executive Sponsor, Governance Council, Data Owner, Data Steward, Data Custodian / IT, DPO, ML Engineer et Business Users.", "Streamlit", "Streamlit > Data Governance > Governance operating model"),
    skill("Bloc 1", "C2.2", "Le plan définit les rôles et responsabilités de chaque partie prenante.", "La matrice de rôles associe chaque partie prenante à ses responsabilités et preuves principales.", "Streamlit", "Streamlit > Data Governance > Governance operating model"),
    skill("Bloc 1", "C2.3", "Le plan identifie les principaux risques liés à la gestion des données.", "Le risk register couvre exposition des données personnelles, data quality, ML drift, accès non autorisé, failure opérationnel et évolution réglementaire.", "Streamlit", "Streamlit > Data Governance > Data risk register"),
    skill("Bloc 1", "C2.4", "Le plan présente des stratégies définies pour gérer chaque risque identifié.", "Chaque risque est associé à un impact, une mitigation et un owner.", "Streamlit", "Streamlit > Data Governance > Data risk register"),
    skill("Bloc 1", "C2.5", "Le plan prévoit des plans de contingence pour situations d'urgence ou risques graves.", "La procédure breach response et la documentation operations donnent un cadre de réaction aux incidents.", "Streamlit, VSCode", "Streamlit > Data Governance > Breach response procedure ; docs/INFRA_OPERATIONS.md"),
    skill("Bloc 1", "C4.1", "Les idées sont exprimées de manière claire et concise dans le plan.", "Les pages Streamlit structurent les informations en sections courtes, métriques et tableaux lisibles.", "Streamlit", "Streamlit > Data Governance ; Project Evidence"),
    skill("Bloc 1", "C4.2", "Le plan est organisé de manière logique et cohérente.", "Les pages sont organisées par thème : overview, gouvernance, architecture, qualité, IA, observabilité et preuves.", "Streamlit", "Streamlit > navigation pages"),
    skill("Bloc 1", "C4.3", "Le plan inclut des détails techniques suffisants pour sa mise en œuvre.", "Technical evidence liste les endpoints, tables, fichiers et outils nécessaires.", "Streamlit, VSCode", "Streamlit > Technical evidence expanders"),
    skill("Bloc 1", "C4.4", "Le plan inclut des références à des normes ou réglementations.", "RGPD, ISO 27001 mindset, accessibilité et accountability sont explicitement mentionnés.", "Streamlit", "Streamlit > Data Governance > Regulatory alignment"),
    skill("Bloc 1", "C4.5", "Un individu externe peut comprendre et mettre en œuvre le plan à partir de la documentation.", "La page Project Evidence indique les outils, emplacements et preuves à ouvrir pour chaque sujet.", "Streamlit, VSCode", "Streamlit > Project Evidence ; docs/"),

    skill("Bloc 2", "C1.1", "L'architecture correspond aux exigences spécifiques du projet fictif.", "RetailFlow couvre ingestion événementielle, stockage PostgreSQL, API, dashboard, orchestration, monitoring et IA.", "Streamlit, Docker Compose", "Streamlit > Data Architecture ; docker-compose.yml"),
    skill("Bloc 2", "C1.2", "L'architecture est flexible pour s'adapter à de nouveaux besoins.", "Les services sont découplés par Docker Compose et Redpanda, avec séparation API, consumer, DB, ML, monitoring et UI.", "Docker Compose, Redpanda", "VSCode > docker-compose.yml"),
    skill("Bloc 2", "C1.3", "L'architecture gère volume, variété et vélocité des données.", "Raw events, JSON payloads, tables analytics, prédictions et flux Redpanda démontrent les trois dimensions.", "PostgreSQL, Redpanda, Streamlit", "Streamlit > Data Architecture ; pgAdmin > raw.events"),
    skill("Bloc 2", "C1.4", "L'architecture assure fiabilité et disponibilité des données.", "Healthchecks, backup/restore, monitoring et stockage PostgreSQL soutiennent la disponibilité.", "Docker Compose, PostgreSQL, Prometheus", "docker-compose.yml ; docs/INFRA_OPERATIONS.md", "Partiellement démontré"),
    skill("Bloc 2", "C1.5", "L'architecture peut gérer une augmentation future du volume ou des traitements.", "Le découplage broker / consumer / API permet d'ajouter des consumers, métriques et traitements.", "Docker Compose, Redpanda", "Streamlit > Data Architecture > Scalability"),
    skill("Bloc 2", "C2.1", "L'architecture gère le volume attendu sans perturber les performances.", "Les métriques pipeline et l'observabilité permettent de suivre volumes et performances.", "Prometheus, Grafana, Streamlit", "Streamlit > Observability ; docs/MONITORING_EVIDENCE.md"),
    skill("Bloc 2", "C2.2", "L'architecture traite les données à la vitesse requise.", "Le flux Streamlit → FastAPI → Redpanda → consumer → PostgreSQL traite les événements de démo en quasi temps réel.", "Streamlit, FastAPI, Redpanda", "Streamlit > Customer View ; Data Quality"),
    skill("Bloc 2", "C2.3", "L'architecture gère différents types de données.", "Données structurées SQL, payloads JSONB, rapports ML JSON/TXT et métriques Prometheus sont utilisés.", "PostgreSQL, Prometheus, VSCode", "pgAdmin ; ml/reports/ ; Prometheus"),
    skill("Bloc 2", "C2.4", "L'architecture prévoit la continuité en cas de défaillance.", "Healthchecks, backup/restore, documentation operations et alerting soutiennent la reprise, sans cluster HA complet.", "Docker Compose, PostgreSQL, Prometheus", "docs/INFRA_OPERATIONS.md ; Streamlit > Observability", "Partiellement démontré"),
    skill("Bloc 2", "C2.5", "L'architecture respecte les principes de sécurité des données.", "Rôle readonly, séparation des services, variables d'environnement, CI sécurité et gouvernance d'accès sont présents.", "PostgreSQL, GitHub Actions, VSCode", "database/init/ ; .github/workflows/ ; docs/CI_CD.md", "Partiellement démontré"),
    skill("Bloc 2", "C3.1", "L'architecture permet une gestion conforme des données personnelles RGPD.", "Consentement, rétention, anonymisation et audit trail sont intégrés dans governance.", "Streamlit, PostgreSQL", "Streamlit > Data Governance"),
    skill("Bloc 2", "C3.2", "L'architecture respecte des normes de sécurité comme ISO 27001 ou recommandations ANSSI.", "Le projet adopte une logique ISO 27001 mindset : risques, accès, audit, sauvegarde et documentation.", "Streamlit, VSCode", "Streamlit > Data Governance > Regulatory alignment", "Partiellement démontré"),
    skill("Bloc 2", "C3.3", "L'architecture garantit la confidentialité des données avec accès et mesures techniques.", "Le rôle readonly, la séparation des responsabilités et la gouvernance d'usage limitent l'accès aux données.", "PostgreSQL, pgAdmin", "database/init/ ; pgAdmin", "Partiellement démontré"),
    skill("Bloc 2", "C3.4", "L'architecture respecte les obligations légales spécifiques si secteur réglementé.", "RetailFlow est positionné comme plateforme retail e-commerce ; aucun secteur santé ou finance n'est simulé.", "Streamlit", "Streamlit > Platform Overview > Project scope and assumptions"),
    skill("Bloc 2", "C3.5", "L'architecture prévoit des mécanismes pour droit d'accès et suppression.", "La gouvernance couvre rétention, anonymisation et actions de cleanup.", "Streamlit, Airflow, PostgreSQL", "Streamlit > Data Governance ; Airflow > retention_cleanup"),
    skill("Bloc 2", "C5.1", "Le code est clair, compréhensible et utilise des noms significatifs.", "Les fichiers sont organisés par domaines : api, pipeline, ml, streamlit_app, airflow, monitoring.", "VSCode", "VSCode > repository"),
    skill("Bloc 2", "C5.2", "Le code utilise des commentaires pour expliquer les parties complexes.", "Des commentaires et documentations ont été ajoutés sur les parties pipeline, MLOps et exploitation.", "VSCode", "pipeline/consumer/ ; ml/src/ ; docs/"),
    skill("Bloc 2", "C5.3", "Le code est bien organisé avec structure claire.", "La structure modulaire sépare API, consumer, pages Streamlit, DAGs Airflow, scripts ML et monitoring.", "VSCode", "repository tree"),
    skill("Bloc 2", "C5.4", "Le code respecte les conventions de codage Python.", "Le projet compile avec compileall et passe les tests CI.", "Python, GitHub Actions", "GitHub > Actions"),
    skill("Bloc 2", "C5.5", "Le code est accompagné d'une documentation d'utilisation et de maintenance.", "Documentation CI/CD, monitoring, operations et evidence.", "VSCode", "docs/CI_CD.md ; docs/MONITORING.md ; docs/INFRA_OPERATIONS.md"),
    skill("Bloc 2", "C5.6", "Le code inclut une gestion appropriée des erreurs et exceptions.", "FastAPI, Streamlit safe calls, consumer validation et dead-letter events gèrent les erreurs.", "FastAPI, Streamlit, PostgreSQL", "api/app/ ; streamlit_app/pages/ ; pipeline/consumer/"),

    skill("Bloc 3", "C1.1", "Indicateur de temps ou taux de traitement du pipeline.", "Le producer génère un rapport de métriques pipeline et l'observabilité expose des métriques Prometheus.", "Python, Prometheus, Streamlit", "pipeline/reports/pipeline_metrics.json ; Streamlit > Observability"),
    skill("Bloc 3", "C1.2", "Gestion des erreurs dans le pipeline.", "Les événements invalides sont isolés en dead-letter avec error_reason, raw_payload et severity.", "PostgreSQL, Streamlit", "Streamlit > Data Quality ; governance.dead_letter_events"),
    skill("Bloc 3", "C1.3", "Précision des données traitées par le pipeline.", "Les événements sont validés avant alimentation analytique ; les anomalies sont tracées.", "Pipeline consumer, PostgreSQL", "pipeline/consumer/ ; Streamlit > Data Quality"),
    skill("Bloc 3", "C1.4", "Capacité du pipeline à gérer variations de volumes, formats ou sources.", "Redpanda découple ingestion et consommation ; raw_payload JSONB accepte des données semi-structurées.", "Redpanda, PostgreSQL", "docker-compose.yml ; pgAdmin > raw.events"),
    skill("Bloc 3", "C1.5", "Redondance du pipeline en cas de défaillance.", "Le projet démontre healthchecks, monitoring et isolation d'erreurs, mais pas une redondance multi-consumer complète.", "Docker Compose, Prometheus", "Streamlit > Observability", "Partiellement démontré"),
    skill("Bloc 3", "C2.1", "Automatisation de la collecte des données.", "Les événements sont collectés via API et générateurs de démo ; Airflow orchestre les traitements planifiés.", "FastAPI, Streamlit, Airflow", "Streamlit > Customer View ; Airflow DAGs"),
    skill("Bloc 3", "C2.2", "Automatisation du traitement des données.", "Le consumer traite automatiquement les événements Redpanda et alimente PostgreSQL.", "Redpanda, Python consumer, PostgreSQL", "pipeline/consumer/ ; docker logs retailflow_event_consumer"),
    skill("Bloc 3", "C2.3", "Automatisation de la mise à jour des données.", "Les tables raw, governance et analytics sont alimentées par consumer et DAGs Airflow.", "PostgreSQL, Airflow", "pgAdmin ; Airflow DAGs"),
    skill("Bloc 3", "C2.4", "Automatisation du monitoring et alertes.", "Prometheus scrape les services et évalue des alert rules visibles dans Streamlit.", "Prometheus, Grafana, Streamlit", "Streamlit > Observability > Prometheus alert rules"),
    skill("Bloc 3", "C2.5", "Automatisation de récupération après erreur.", "Les dead-letter events permettent isolation et reprocessing gouverné ; la reprise automatique complète est partiellement simulée.", "PostgreSQL, Streamlit", "Streamlit > Data Quality > Quality remediation workflow", "Partiellement démontré"),
    skill("Bloc 3", "C3.1", "Présence d'outils de suivi des performances du pipeline.", "Prometheus, Grafana et Streamlit Observability donnent une vue de suivi.", "Prometheus, Grafana, Streamlit", "Streamlit > Observability"),
    skill("Bloc 3", "C3.2", "Variété des métriques suivies.", "Targets, alertes, erreurs API, latence, DB metrics, qualité et dead-letter events sont suivis.", "Prometheus, Grafana, PostgreSQL", "Grafana dashboards ; Prometheus Alerts"),
    skill("Bloc 3", "C3.3", "Facilité d'accès aux informations de performance.", "Les pages Observability et Data Quality rendent les métriques accessibles au jury.", "Streamlit", "Streamlit > Observability ; Data Quality"),
    skill("Bloc 3", "C3.4", "Signalement proactif des problèmes.", "Des règles Prometheus existent pour services down, latence, erreurs API et PostgreSQL.", "Prometheus", "Prometheus > Alerts ; monitoring/prometheus/rules/"),
    skill("Bloc 3", "C3.5", "Capacité des outils de monitoring à évoluer.", "Les règles et dashboards sont versionnés et modifiables dans le dossier monitoring.", "VSCode, Prometheus, Grafana", "monitoring/"),
    skill("Bloc 3", "C4.1", "Organisation du code pipeline.", "Le code pipeline est séparé dans pipeline/consumer avec validation, consommation et stockage.", "VSCode", "pipeline/consumer/"),
    skill("Bloc 3", "C4.2", "Commentaires dans le code pipeline.", "Les parties critiques du pipeline et MLOps ont été documentées.", "VSCode", "pipeline/consumer/ ; docs/"),
    skill("Bloc 3", "C4.3", "Lisibilité du code pipeline.", "Les fonctions et fichiers utilisent des noms explicites autour des events, validation, producer et consumer.", "VSCode", "pipeline/ ; api/app/services/event_producer.py"),
    skill("Bloc 3", "C4.4", "Documentation technique du pipeline.", "Les documents operations, monitoring et evidence décrivent le fonctionnement et les preuves.", "VSCode", "docs/INFRA_OPERATIONS.md ; docs/MONITORING.md"),
    skill("Bloc 3", "C4.5", "Conformité aux bonnes pratiques de codage.", "Tests, compileall et CI GitHub Actions valident le code.", "GitHub Actions, Python", "GitHub > Actions"),
    skill("Bloc 3", "C6.1", "Minimisation des données personnelles dans le pipeline.", "Les usages IA sont contrôlés par analytics consent et les politiques de rétention limitent la conservation.", "Streamlit, PostgreSQL", "Data Governance ; Customer Intelligence"),
    skill("Bloc 3", "C6.2", "Sécurité des données dans le pipeline.", "Séparation des services, rôle readonly, variables d'environnement et contrôles CI sécurité.", "Docker Compose, PostgreSQL, GitHub Actions", "docker-compose.yml ; database/init/ ; GitHub Actions", "Partiellement démontré"),
    skill("Bloc 3", "C6.3", "Gestion des consentements et droits RGPD.", "Consentements client, rétention et anonymisation sont exposés dans Data Governance.", "Streamlit, PostgreSQL", "Streamlit > Data Governance"),
    skill("Bloc 3", "C6.4", "Traçabilité complète des traitements.", "event_id, source_topic, raw_payload, dead_letter_id et logs d'actions assurent la traçabilité.", "PostgreSQL, pgAdmin", "raw.events ; governance.dead_letter_events ; retention_actions_log"),
    skill("Bloc 3", "C6.5", "Détection, signalement et gestion des violations de données.", "Breach response, Data Quality et Observability fournissent le cadre de détection et réaction.", "Streamlit, Prometheus", "Data Governance > Breach response ; Observability"),

    skill("Bloc 4", "C1.1", "Adéquation entre cahier des charges et fonctionnalités IA, incluant accessibilité.", "RetailFlow couvre churn, CLV, segmentation, dashboard, gouvernance et accessibilité de présentation.", "Streamlit, FastAPI, ML", "Customer Intelligence ; AI Monitoring"),
    skill("Bloc 4", "C1.2", "Qualité des prédictions mesurée par des métriques adaptées.", "Les rapports ML contiennent les métriques des modèles churn, CLV et segmentation.", "Streamlit, VSCode", "AI Monitoring > Model reports ; ml/reports/"),
    skill("Bloc 4", "C1.3", "Robustesse face aux données imparfaites ou erronées.", "Tests ML, robustesse et dead-letter quality démontrent la gestion des cas limites.", "pytest, Streamlit", "ml/tests/ ; Data Quality"),
    skill("Bloc 4", "C1.4", "Scalabilité de la solution IA.", "FastAPI sert les prédictions, les modèles sont séparés du pipeline et la stack Docker peut évoluer.", "FastAPI, Docker Compose", "AI Monitoring ; docker-compose.yml"),
    skill("Bloc 4", "C1.5", "Explications compréhensibles des prédictions ou décisions.", "Decision framework et recommandations métier expliquent les actions associées aux sorties IA.", "Streamlit", "Customer Intelligence > Decision framework"),
    skill("Bloc 4", "C2.1", "Compatibilité avec l'infrastructure de données existante.", "Les prédictions IA utilisent les tables analytics et sont servies via FastAPI à Streamlit.", "PostgreSQL, FastAPI, Streamlit", "api/app/routes/ai.py ; Customer Intelligence"),
    skill("Bloc 4", "C2.2", "Interaction fluide avec les composants système.", "FastAPI, PostgreSQL, Streamlit et Airflow interagissent dans la stack Docker Compose.", "Docker Compose", "docker-compose.yml"),
    skill("Bloc 4", "C2.3", "Mécanismes de gestion des erreurs IA.", "safe API calls, rapports ML, monitoring et tests couvrent les erreurs applicatives et MLOps.", "Streamlit, GitHub Actions", "AI Monitoring ; GitHub Actions"),
    skill("Bloc 4", "C2.4", "Facilité de maintenance et mise à jour.", "Registry, rapports, scripts ML, CI et documentation facilitent la maintenance.", "VSCode, GitHub Actions", "ml/src/ ; ml/reports/ ; docs/CI_CD.md"),
    skill("Bloc 4", "C2.5", "Respect des normes de sécurité et RGPD, incluant accessibilité.", "Consentement analytics, gouvernance, security checks CI et accessibilité de l'interface sont démontrés.", "Streamlit, GitHub Actions", "Data Governance ; Customer Intelligence ; CI/CD and Operations"),
    skill("Bloc 4", "C3.1", "Système de réentrainement automatique des modèles IA.", "Airflow contient un DAG ml_retraining et AI Monitoring affiche retraining_runs.json.", "Airflow, Streamlit", "Airflow > ml_retraining ; AI Monitoring"),
    skill("Bloc 4", "C3.2", "Réentrainement efficace et opportun.", "Le journal retraining_runs documente les exécutions ; la fréquence est pilotable via Airflow.", "Airflow, VSCode", "airflow/dags/ml_retraining.py ; ml/reports/retraining_runs.json"),
    skill("Bloc 4", "C3.3", "Prise en compte des changements dans les données.", "Le drift report et les features clients permettent d'identifier les changements de distribution.", "Streamlit, ML reports", "AI Monitoring > Drift monitoring"),
    skill("Bloc 4", "C3.4", "Détection et gestion de la dérive modèle.", "AI Monitoring expose drift_report.json et le lifecycle indique monitor puis retrain.", "Streamlit, VSCode", "AI Monitoring > Drift monitoring ; ml/reports/drift_report.json"),
    skill("Bloc 4", "C3.5", "Prévisibilité et reproductibilité du réentrainement.", "Model registry, rapports ML, scripts versionnés et retraining log soutiennent la reproductibilité.", "Git, VSCode, Streamlit", "ml/model_registry.json ; ml/src/ ; ml/reports/"),
    skill("Bloc 4", "C4.1", "Pipeline d'intégration et déploiement continu pour la solution IA.", "GitHub Actions exécute tests, checks et rapports sécurité.", "GitHub Actions", "GitHub > Actions ; .github/workflows/"),
    skill("Bloc 4", "C4.2", "Pipeline CI fonctionnel sans erreurs.", "Les derniers commits sont validés par la CI verte.", "GitHub Actions", "GitHub > Actions"),
    skill("Bloc 4", "C4.3", "Mise à jour et livraison fluides de la solution IA.", "Les commits successifs ont été poussés sur develop avec validation CI.", "Git, GitHub Actions", "git log ; GitHub > Actions"),
    skill("Bloc 4", "C4.4", "Pipeline entièrement automatisé sans intervention manuelle.", "Build/test/checks sont automatisés ; le déploiement local reste déclenché manuellement par Docker Compose.", "GitHub Actions, Docker Compose", "GitHub Actions ; docker compose commands", "Partiellement démontré"),
    skill("Bloc 4", "C4.5", "Gestion des versions de la solution IA.", "Git, commits clairs, registry modèle et rapports ML versionnés.", "Git, VSCode", "git log ; ml/model_registry.json"),
    skill("Bloc 4", "C4.6", "Bonnes pratiques de sécurité dans le pipeline.", "Security checks Bandit et pip-audit génèrent des rapports de CI.", "GitHub Actions", "CI/CD and Operations ; GitHub > Actions"),
    skill("Bloc 4", "C5.1", "Conformité RGPD de la solution IA.", "Consentement analytics contrôle l'affichage des prédictions IA et la gouvernance couvre rétention/anonymisation.", "Streamlit, PostgreSQL", "Customer Intelligence ; Data Governance"),
    skill("Bloc 4", "C5.2", "Respect Informatique et Libertés : droits d'accès, rectification, suppression.", "Les mécanismes de rétention et anonymisation représentent la logique de suppression/anonymisation.", "Streamlit, Airflow", "Data Governance ; retention_cleanup"),
    skill("Bloc 4", "C5.3", "Respect des normes de sécurité en vigueur.", "Rôle readonly, CI sécurité, séparation des services et documentation sécurité sont présents.", "PostgreSQL, GitHub Actions", "database/init/ ; GitHub Actions", "Partiellement démontré"),
    skill("Bloc 4", "C5.4", "Respect applicable de l'ISO 27001.", "Le projet présente une logique ISO 27001 mindset avec risques, accès, audit et amélioration continue.", "Streamlit", "Data Governance > Regulatory alignment", "Partiellement démontré"),
    skill("Bloc 4", "C5.5", "Respect des principes d'IA éthique.", "Explicabilité métier, consentement analytics, gouvernance des données et limitation d'usage sont démontrés.", "Streamlit", "Customer Intelligence ; Data Governance"),
    skill("Bloc 4", "C6.1", "Code bien organisé et structure logique.", "Le repository est organisé par api, ml, pipeline, airflow, monitoring, streamlit_app et docs.", "VSCode", "repository tree"),
    skill("Bloc 4", "C6.2", "Commentaires utiles dans le code.", "Les sections critiques pipeline, MLOps et documentation ont été renforcées.", "VSCode", "pipeline/ ; ml/src/ ; docs/"),
    skill("Bloc 4", "C6.3", "Code clair, lisible, noms descriptifs.", "Les fonctions et fichiers suivent une logique métier et technique explicite.", "VSCode", "api/app/ ; ml/src/ ; streamlit_app/pages/"),
    skill("Bloc 4", "C6.4", "Documentation complète du code et de l'utilisation.", "README, docs CI/CD, monitoring, operations et pages Streamlit fournissent la documentation.", "VSCode", "README.md ; docs/ ; Streamlit"),
    skill("Bloc 4", "C6.5", "Normes de codage et bonnes pratiques.", "compileall, tests et CI valident la qualité technique.", "Python, GitHub Actions", "GitHub > Actions"),
    skill("Bloc 4", "C6.6", "Gestion appropriée des erreurs et exceptions.", "API, Streamlit, consumer, dead-letter et quality workflows gèrent les erreurs visibles.", "FastAPI, Streamlit, PostgreSQL", "Data Quality ; pipeline/consumer/"),
    skill("Bloc 4", "C6.7", "Tests unitaires, intégration ou fonctionnels.", "Tests unitaires, tests ML, registry tests et CI sont présents.", "pytest, GitHub Actions", "tests/ ; ml/tests/ ; GitHub Actions"),
    skill("Bloc 4", "C6.8", "Code hébergé sur Git avec usage approprié du versioning.", "La branche develop contient des commits atomiques et messages explicites.", "Git, GitHub", "git log --oneline ; GitHub repository"),
]

df_skills = pd.DataFrame(skills_rows)

skill_filter_cols = st.columns(2)

with skill_filter_cols[0]:
    selected_skill_blocs = st.multiselect(
        "Filter by bloc",
        sorted(df_skills["Bloc"].unique().tolist()),
        default=sorted(df_skills["Bloc"].unique().tolist()),
        key="skills_bloc_filter",
    )

available_skill_ids = sorted(
    df_skills[df_skills["Bloc"].isin(selected_skill_blocs)]["ID"].unique().tolist(),
    key=skill_sort_key,
)

with skill_filter_cols[1]:
    selected_skill_ids = st.multiselect(
        "Filter by skill ID",
        available_skill_ids,
        default=available_skill_ids,
        key="skills_id_filter",
    )

filtered_skills_df = df_skills[
    df_skills["Bloc"].isin(selected_skill_blocs)
    & df_skills["ID"].isin(selected_skill_ids)
].copy()

st.dataframe(filtered_skills_df, use_container_width=True, hide_index=True)

section_title("Evidence by block")

for bloc in ["Bloc 1", "Bloc 2", "Bloc 3", "Bloc 4"]:
    bloc_df = df_evidence[df_evidence["Bloc"] == bloc]

    with st.expander(f"{bloc} evidence summary", expanded=False):
        st.dataframe(bloc_df, use_container_width=True, hide_index=True)

section_title("Live demo path")

demo_path = [
    {
        "Step": 1,
        "Page / tool": "Streamlit > Platform Overview",
        "What to show": "Présenter RetailFlow, l'architecture et les liens outils.",
    },
    {
        "Step": 2,
        "Page / tool": "Streamlit > Customer View",
        "What to show": "Générer un parcours complet et un événement invalide.",
    },
    {
        "Step": 3,
        "Page / tool": "Streamlit > Data Quality",
        "What to show": "Montrer la dead-letter, error_reason, raw_payload et workflow de remédiation.",
    },
    {
        "Step": 4,
        "Page / tool": "Streamlit > Customer Intelligence",
        "What to show": "Sélectionner un client et expliquer les décisions IA gouvernées par le consentement analytics.",
    },
    {
        "Step": 5,
        "Page / tool": "Streamlit > Data Governance",
        "What to show": "Montrer rôles, consentements, rétention, risques et breach response.",
    },
    {
        "Step": 6,
        "Page / tool": "Streamlit > AI Monitoring",
        "What to show": "Montrer registry, reports, retraining runs et drift.",
    },
    {
        "Step": 7,
        "Page / tool": "Streamlit > Observability",
        "What to show": "Montrer targets Prometheus, alert rules et dashboards Grafana.",
    },
    {
        "Step": 8,
        "Page / tool": "GitHub Actions",
        "What to show": "Montrer la CI verte et les workflows.",
    },
    {
        "Step": 9,
        "Page / tool": "Airflow",
        "What to show": "Montrer les DAGs opérationnels.",
    },
    {
        "Step": 10,
        "Page / tool": "pgAdmin",
        "What to show": "Montrer raw.events, governance.dead_letter_events et analytics.customer_predictions.",
    },
]

st.dataframe(pd.DataFrame(demo_path), use_container_width=True, hide_index=True)

section_title("Tool map")

tool_rows = [
    {
        "Tool": "Streamlit",
        "Role in demo": "Interface principale de démonstration métier et technique.",
        "Open": "http://localhost:8501",
    },
    {
        "Tool": "FastAPI",
        "Role in demo": "API de publication d'événements et serving IA.",
        "Open": "http://localhost:8000/docs",
    },
    {
        "Tool": "PostgreSQL / pgAdmin",
        "Role in demo": "Stockage des données, événements, prédictions, gouvernance et qualité.",
        "Open": "http://localhost:5050",
    },
    {
        "Tool": "Airflow",
        "Role in demo": "Automatisation qualité, agrégations, cleanup rétention et retraining.",
        "Open": "http://localhost:8080",
    },
    {
        "Tool": "Prometheus",
        "Role in demo": "Scraping, métriques, targets et alert rules.",
        "Open": "http://localhost:9090",
    },
    {
        "Tool": "Grafana",
        "Role in demo": "Dashboards d'exploitation API et plateforme.",
        "Open": "http://localhost:3000",
    },
    {
        "Tool": "GitHub Actions",
        "Role in demo": "CI/CD, tests, sécurité et validation continue.",
        "Open": "GitHub > retailflow-platform > Actions",
    },
    {
        "Tool": "VSCode / WSL",
        "Role in demo": "Code source, scripts, docs, configuration et preuves techniques.",
        "Open": "~/projects/Master_Thesis/retailflow-platform",
    },
]

st.dataframe(pd.DataFrame(tool_rows), use_container_width=True, hide_index=True)

section_title("Soutenance-ready proof cards")

p1, p2, p3, p4 = st.columns(4)

with p1:
    proof_card(
        "Bloc 1",
        "Gouvernance, consentement, rétention, risques, breach response et accessibilité.",
    )

with p2:
    proof_card(
        "Bloc 2",
        "Architecture data conteneurisée, PostgreSQL, Redpanda, services, sauvegarde et monitoring.",
    )

with p3:
    proof_card(
        "Bloc 3",
        "Pipeline événementiel, qualité, dead-letter, Airflow, monitoring et traçabilité.",
    )

with p4:
    proof_card(
        "Bloc 4",
        "Churn, CLV, segmentation, serving IA, registry, drift, retraining et CI/CD.",
    )

section_title("Academic mapping")

academic_mapping(
    [
        {
            "Bloc": "Bloc 1",
            "Section": "Final evidence matrix",
            "Preuve": "Matrice de preuves pour gouvernance, conformité, risques et responsabilités.",
        },
        {
            "Bloc": "Bloc 2",
            "Section": "Final evidence matrix",
            "Preuve": "Matrice de preuves pour architecture, sécurité, exploitation et observabilité.",
        },
        {
            "Bloc": "Bloc 3",
            "Section": "Final evidence matrix",
            "Preuve": "Matrice de preuves pour pipelines, qualité, automatisation et monitoring.",
        },
        {
            "Bloc": "Bloc 4",
            "Section": "Final evidence matrix",
            "Preuve": "Matrice de preuves pour IA, MLOps, serving, retraining, drift et CI/CD.",
        },
    ]
)

technical_evidence(
    {
        "Primary Streamlit pages": [
            "`1_Platform_Overview.py`",
            "`2_Customer_View.py`",
            "`3_Customer_Intelligence.py`",
            "`4_Data_Governance.py`",
            "`5_Data_Architecture.py`",
            "`6_Data_Quality.py`",
            "`7_AI_Monitoring.py`",
            "`8_Observability.py`",
            "`9_CI_CD_and_Operations.py`",
            "`10_Project_Evidence.py`",
        ],
        "Core technical proof": [
            "`docker-compose.yml`",
            "`database/init/`",
            "`api/app/`",
            "`pipeline/consumer/`",
            "`airflow/dags/`",
            "`ml/src/`",
            "`ml/reports/`",
            "`monitoring/`",
            "`.github/workflows/`",
            "`docs/`",
        ],
        "Recommended demo order": [
            "Streamlit first",
            "Then Prometheus / Grafana",
            "Then Airflow",
            "Then pgAdmin",
            "Then GitHub Actions / VSCode proof",
        ],
    }
)

footer_note()
