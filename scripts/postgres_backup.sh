#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# RetailFlow PostgreSQL backup script
# ============================================================
# Creates a compressed custom-format backup of the RetailFlow
# PostgreSQL database from the running Docker container.
#
# Output format:
# backups/postgres/retailflow_db_YYYYmmdd_HHMMSS.dump
# ============================================================

CONTAINER_NAME="${POSTGRES_CONTAINER_NAME:-retailflow_postgres}"
POSTGRES_USER="${POSTGRES_USER:-retailflow}"
POSTGRES_DB="${POSTGRES_DB:-retailflow_db}"
BACKUP_DIR="${BACKUP_DIR:-backups/postgres}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"

TIMESTAMP="$(date -u +%Y%m%d_%H%M%S)"
BACKUP_FILE="${BACKUP_DIR}/${POSTGRES_DB}_${TIMESTAMP}.dump"

mkdir -p "${BACKUP_DIR}"

echo "Starting PostgreSQL backup"
echo "Container: ${CONTAINER_NAME}"
echo "Database: ${POSTGRES_DB}"
echo "Output: ${BACKUP_FILE}"

docker exec "${CONTAINER_NAME}" pg_dump \
  -U "${POSTGRES_USER}" \
  -d "${POSTGRES_DB}" \
  -F c \
  -f "/tmp/${POSTGRES_DB}_${TIMESTAMP}.dump"

docker cp \
  "${CONTAINER_NAME}:/tmp/${POSTGRES_DB}_${TIMESTAMP}.dump" \
  "${BACKUP_FILE}"

docker exec "${CONTAINER_NAME}" rm -f "/tmp/${POSTGRES_DB}_${TIMESTAMP}.dump"

find "${BACKUP_DIR}" \
  -name "${POSTGRES_DB}_*.dump" \
  -type f \
  -mtime "+${RETENTION_DAYS}" \
  -print \
  -delete

echo "Backup completed successfully"
echo "Backup file: ${BACKUP_FILE}"
