#!/bin/bash
# (Phase 1) Local Postgres/pgvector backup script
# This script dumps the database contents from the Docker container to a local backups folder.

# Exit on any error
set -e

# Define paths relative to the script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$REPO_ROOT/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/travel_exp_planner_backup_$TIMESTAMP.sql"

# Create the backups directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Container and database variables
CONTAINER_NAME="travel_exp_planner_rfl_db"
DB_USER="postgres"
DB_NAME="travel_exp_planner_rfl_db"

echo "Starting database backup for $DB_NAME..."

# Execute pg_dump inside the container and write output directly to the host backup file
# Using docker exec -t (without -i to avoid stdin issues in non-interactive shells/cron jobs)
docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"

echo "Backup completed successfully! Saved to: $BACKUP_FILE"
