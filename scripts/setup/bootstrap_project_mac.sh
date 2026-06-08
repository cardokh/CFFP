#!/bin/bash

set -e

PROJECT_ROOT="$(pwd)"
CONFIG_FILE_PATH="$PROJECT_ROOT/scripts/setup/config/bootstrap_project.json"

if [ ! -f "$CONFIG_FILE_PATH" ]; then
  echo "FAILED Project bootstrap failed. Missing config: scripts/setup/config/bootstrap_project.json"
  exit 1
fi

OUTPUT_DIRECTORY="scripts/setup/output"
SUMMARY_FILE_NAME="bootstrap_project_summary.json"
LOG_FILE_NAME="bootstrap_project.log"

mkdir -p "$OUTPUT_DIRECTORY"

SUMMARY_FILE_PATH="$OUTPUT_DIRECTORY/$SUMMARY_FILE_NAME"
LOG_FILE_PATH="$OUTPUT_DIRECTORY/$LOG_FILE_NAME"

: > "$LOG_FILE_PATH"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE_PATH"
}

run_command() {
  STEP_NAME="$1"
  COMMAND="$2"

  log "STARTED - $STEP_NAME - $COMMAND"

  if eval "$COMMAND" >> "$LOG_FILE_PATH" 2>&1; then
    log "PASSED - $STEP_NAME - Command completed successfully."
  else
    log "FAILED - $STEP_NAME - Command failed."
    write_summary "FAILED" "$STEP_NAME failed."
    echo "FAILED Project bootstrap failed. Summary: scripts/setup/output/bootstrap_project_summary.json"
    exit 1
  fi
}

write_summary() {
  STATUS="$1"
  ERROR_MESSAGE="$2"

  cat > "$SUMMARY_FILE_PATH" <<EOF
{
  "status": "$STATUS",
  "projectRoot": ".",
  "summaryFile": "scripts/setup/output/bootstrap_project_summary.json",
  "logFile": "scripts/setup/output/bootstrap_project.log",
  "error": "$ERROR_MESSAGE"
}
EOF
}

log "Project bootstrap started."
log "Project root: ."

if [ ! -d ".venv" ]; then
  run_command "Create virtual environment" "python3 -m venv .venv"
else
  log "SKIPPED - Create virtual environment - Existing .venv found."
fi

if [ ! -f ".venv/bin/activate" ]; then
  log "FAILED - Virtual environment activation script not found."
  write_summary "FAILED" "Virtual environment activation script not found: .venv/bin/activate"
  echo "FAILED Project bootstrap failed. Summary: scripts/setup/output/bootstrap_project_summary.json"
  exit 1
fi

source .venv/bin/activate
log "PASSED - Activate virtual environment - Virtual environment activated."

export PYTHONPATH="$PROJECT_ROOT"
log "PASSED - Set PYTHONPATH - PYTHONPATH set to project root."

run_command "Install dependencies" "python -m pip install -r requirements.txt"
run_command "Create SQLite database schema" "python -m scripts.db.sqlite_create_schema"
run_command "Seed SQLite database" "python -m scripts.db.sqlite_seed_data"

write_summary "PASSED" ""

echo "PASSED Project bootstrap completed. Summary: scripts/setup/output/bootstrap_project_summary.json"