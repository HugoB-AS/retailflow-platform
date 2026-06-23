#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# RetailFlow PostgreSQL restore script
# ============================================================
# Restores a RetailFlow PostgreSQL backup created by
# scripts/postgres_backup.sh into the running Docker container.
#
# Usage:
# ./scripts/postgres_restore.sh backups/postgres/retailflow_db_YYYYmmdd_HHMMSS.dump
# ============================================================

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <backup_file.dump>"
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_FILE}" ]; then
  echo "Backup file not found: ${BACKUP_FILE}"
  exit 1
fi

CONTAINER_NAME="${POSTGRES_CONTAINER_NAME:-retailflow_postgres}"
POSTGRES_USER="${POSTGRES_USER:-retailflow}"
POSTGRES_DB="${POSTGRES_DB:-retailflow_db}"
CONTAINER_BACKUP_FILE="/tmp/$(basename "${BACKUP_FILE}")"

echo "WARNING: this restore will overwrite database objects in ${POSTGRES_DB}."
echo "Container: ${CONTAINER_NAME}"
echo "Backup file: ${BACKUP_FILE}"
echo ""
read -r -p "Type RESTORE to continue: " CONFIRMATION

if [ "${CONFIRMATION}" != "RESTORE" ]; then
  echo "Restore cancelled."
  exit 1
fi

docker cp "${BACKUP_FILE}" "${CONTAINER_NAME}:${CONTAINER_BACKUP_FILE}"

docker exec "${CONTAINER_NAME}" pg_restore \
  -U "${POSTGRES_USER}" \
  -d "${POSTGRES_DB}" \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  "${CONTAINER_BACKUP_FILE}"

docker exec "${CONTAINER_NAME}" rm -f "${CONTAINER_BACKUP_FILE}"

echo "Restore completed successfully"
