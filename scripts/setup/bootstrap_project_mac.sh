#!/bin/bash

set -e

PROJECT_ROOT="$(pwd)"
CONFIG_FILE_PATH="$PROJECT_ROOT/scripts/setup/config/bootstrap_project.json"

if [ ! -f "$CONFIG_FILE_PATH" ]; then
  echo "FAILED Project bootstrap failed. Missing config: scripts/setup/config/bootstrap_project.json"
  exit 1
fi

OUTPUT_DIRECTORY=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE_PATH'))['outputDirectory'])")
SUMMARY_FILE_NAME=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE_PATH'))['summaryFileName'])")
LOG_FILE_NAME=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE_PATH'))['logFileName'])")

OUTPUT_DIRECTORY_PATH="$PROJECT_ROOT/$OUTPUT_DIRECTORY"
SUMMARY_FILE_PATH="$OUTPUT_DIRECTORY_PATH/$SUMMARY_FILE_NAME"
LOG_FILE_PATH="$OUTPUT_DIRECTORY_PATH/$LOG_FILE_NAME"

mkdir -p "$OUTPUT_DIRECTORY_PATH"
: > "$LOG_FILE_PATH"

LOG_CACHE=()
STEPS_JSON="[]"

log() {
  LOG_CACHE+=("[$(date '+%Y-%m-%d %H:%M:%S')] $1")
}

flush_log() {
  if [ "${#LOG_CACHE[@]}" -gt 0 ]; then
    printf "%s\n" "${LOG_CACHE[@]}" >> "$LOG_FILE_PATH"
    LOG_CACHE=()
  fi
}

add_step() {
  local NAME="$1"
  local STATUS="$2"
  local MESSAGE="$3"

  STEPS_JSON=$(python3 -c '
import json, sys
steps = json.loads(sys.argv[1])
steps.append({"name": sys.argv[2], "status": sys.argv[3], "message": sys.argv[4]})
print(json.dumps(steps))
' "$STEPS_JSON" "$NAME" "$STATUS" "$MESSAGE")

  log "$STATUS - $NAME - $MESSAGE"
}

write_summary() {
  local STATUS="$1"
  local ERROR_MESSAGE="$2"

  python3 -c '
import json, sys

status = sys.argv[1]
summary_file_path = sys.argv[2]
summary_file_name = sys.argv[3]
log_file_name = sys.argv[4]
error_message = sys.argv[5]
steps = json.loads(sys.argv[6])

summary = {
    "status": status,
    "projectRoot": ".",
    "summaryFile": f"scripts/setup/output/{summary_file_name}",
    "logFile": f"scripts/setup/output/{log_file_name}",
    "steps": steps,
}

if error_message:
    summary["error"] = error_message

with open(summary_file_path, "w", encoding="utf-8") as file:
    json.dump(summary, file, indent=2)
    file.write("\n")
' "$STATUS" "$SUMMARY_FILE_PATH" "$SUMMARY_FILE_NAME" "$LOG_FILE_NAME" "$ERROR_MESSAGE" "$STEPS_JSON"
}

run_command() {
  local STEP_NAME="$1"
  shift

  log "STARTED - $STEP_NAME - $*"

  if OUTPUT=$("$@" 2>&1); then
    while IFS= read -r LINE; do
      [ -n "$LINE" ] && log "$LINE"
    done <<< "$OUTPUT"

    add_step "$STEP_NAME" "PASSED" "Command completed successfully."
    flush_log
  else
    local EXIT_CODE=$?

    while IFS= read -r LINE; do
      [ -n "$LINE" ] && log "$LINE"
    done <<< "$OUTPUT"

    add_step "$STEP_NAME" "FAILED" "Command failed with exit code $EXIT_CODE."
    flush_log
    write_summary "FAILED" "$STEP_NAME failed with exit code $EXIT_CODE."
    echo "FAILED Project bootstrap failed. Summary: scripts/setup/output/$SUMMARY_FILE_NAME"
    exit 1
  fi
}

file_md5() {
  local FILE_PATH="$1"

  if [ ! -f "$FILE_PATH" ]; then
    echo ""
    return
  fi

  md5 -q "$FILE_PATH"
}

install_dependencies_if_needed() {
  local REQUIREMENTS_PATH="$PROJECT_ROOT/requirements.txt"
  local HASH_FILE_PATH="$PROJECT_ROOT/.venv/.requirements.hash"

  if [ ! -f "$REQUIREMENTS_PATH" ]; then
    add_step "Install dependencies" "SKIPPED" "requirements.txt not found."
    flush_log
    return
  fi

  local CURRENT_HASH
  CURRENT_HASH=$(file_md5 "$REQUIREMENTS_PATH")

  local PREVIOUS_HASH=""
  if [ -f "$HASH_FILE_PATH" ]; then
    PREVIOUS_HASH="$(cat "$HASH_FILE_PATH" | tr -d '[:space:]')"
  fi

  if [ "$CURRENT_HASH" = "$PREVIOUS_HASH" ]; then
    add_step "Install dependencies" "SKIPPED" "requirements.txt unchanged."
    flush_log
    return
  fi

  run_command "Install dependencies" python -m pip install -r requirements.txt

  echo "$CURRENT_HASH" > "$HASH_FILE_PATH"
  log "UPDATED - requirements hash cache - .venv/.requirements.hash"
  flush_log
}

handle_failure() {
  local ERROR_MESSAGE="$1"

  if [ -z "$ERROR_MESSAGE" ]; then
    ERROR_MESSAGE="Unknown bootstrap error. Check log file."
  fi

  log "FAILED - Project bootstrap failed - $ERROR_MESSAGE"
  flush_log
  write_summary "FAILED" "$ERROR_MESSAGE"

  echo "FAILED Project bootstrap failed. Summary: scripts/setup/output/$SUMMARY_FILE_NAME"
  exit 1
}

trap 'handle_failure "Unexpected bootstrap failure."' ERR

log "Project bootstrap started."
log "Project root: ."
flush_log

CREATE_VENV=$(python3 -c "import json; print(str(json.load(open('$CONFIG_FILE_PATH'))['steps'].get('createVirtualEnvironment', False)).lower())")
INSTALL_DEPENDENCIES=$(python3 -c "import json; print(str(json.load(open('$CONFIG_FILE_PATH'))['steps'].get('installDependencies', False)).lower())")
CREATE_DATABASE_SCHEMA=$(python3 -c "import json; print(str(json.load(open('$CONFIG_FILE_PATH'))['steps'].get('createDatabaseSchema', False)).lower())")
SEED_DATABASE=$(python3 -c "import json; print(str(json.load(open('$CONFIG_FILE_PATH'))['steps'].get('seedDatabase', False)).lower())")

if [ "$CREATE_VENV" = "true" ]; then
  if [ ! -d ".venv" ]; then
    run_command "Create virtual environment" python3 -m venv .venv
  else
    add_step "Create virtual environment" "SKIPPED" "Existing .venv found."
    flush_log
  fi
fi

if [ ! -f ".venv/bin/activate" ]; then
  handle_failure "Virtual environment activation script not found: .venv/bin/activate"
fi

source .venv/bin/activate
add_step "Activate virtual environment" "PASSED" "Virtual environment activated."
flush_log

export PYTHONPATH="$PROJECT_ROOT"
add_step "Set PYTHONPATH" "PASSED" "PYTHONPATH set to project root."
flush_log

if [ "$INSTALL_DEPENDENCIES" = "true" ]; then
  install_dependencies_if_needed
fi

if [ "$CREATE_DATABASE_SCHEMA" = "true" ]; then
  run_command "Create SQLite database schema" python -m scripts.db.sqlite_create_schema
fi

if [ "$SEED_DATABASE" = "true" ]; then
  run_command "Seed SQLite database" python -m scripts.db.sqlite_seed_data
fi

write_summary "PASSED" ""
log "Project bootstrap completed successfully."
flush_log

echo "PASSED Project bootstrap completed. Summary: scripts/setup/output/$SUMMARY_FILE_NAME"
exit 0