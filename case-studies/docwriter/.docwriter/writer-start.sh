#!/usr/bin/env bash
# writer-start.sh
#
# Supervisor script for the "docwriter" Copilot agent.
# Launches the agent in a loop, restarting on failure or unexpected exit,
# until the agent prints a well-known done marker or the retry limit is hit.
#
# Usage: bash .docwriter/writer-start.sh
set -uo pipefail

# ---------------------------------------------------------------------------
# OpenTelemetry tracing (optional)
# Uncomment and configure these variables to export traces to an OTLP collector
# for observability of Copilot agent runs.
# ---------------------------------------------------------------------------
# export COPILOT_OTEL_ENABLED=true
# export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
# export COPILOT_OTEL_EXPORTER_TYPE="otlp-http"
# export OTEL_SERVICE_NAME="github-copilot"
# export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
# export OTEL_LOG_LEVEL="DEBUG"

# ---------------------------------------------------------------------------
# Copilot runtime tuning
# ---------------------------------------------------------------------------
# How long (seconds) the supervisor waits for a task before timing out.
export COPILOT_TASK_WAIT_TIMEOUT_SECONDS=360000
# Skip the interactive "configure agent" prompt so this script is non-interactive.
export CONFIGURE_COPILOT_AGENT=false
# Allow the agent to spawn background sub-agents for parallel work.
export COPILOT_SWE_AGENT_BACKGROUND_AGENTS=true
# Allow background agents to run tasks in parallel.
export COPILOT_SWE_AGENT_PARALLEL_TASK_EXECUTION=true
# Maximum bytes allowed in a single large tool output (100 MB).
export COPILOT_LARGE_OUTPUT_MAX_BYTES=104857600
# Fraction of the output buffer that must be consumed before Copilot starts
# dropping old content to prevent memory exhaustion (99%).
export COPILOT_BUFFER_EXHAUSTION_THRESHOLD=0.99
# Outputs larger than this threshold (200 KB) are considered "large" and
# subject to the COPILOT_LARGE_OUTPUT_MAX_BYTES cap.
export COPILOT_LARGE_OUTPUT_THRESHOLD_BYTES=204800

# ---------------------------------------------------------------------------
# Ensure the top-level log directory exists before any run starts.
# Individual run logs are written under this directory with timestamps.
# ---------------------------------------------------------------------------
mkdir -p /workspace/logs

# The string the agent must print to signal a successful, completed run.
# If this marker is absent from the log, the script treats the run as incomplete
# and retries (subject to MAX_RETRIES).
DONE_MARKER="===WRITER DONE==="

# Name of the Copilot agent to invoke and path to its definition file.
AGENT_NAME="docwriter"
AGENT_FILE="/workspace/.github/agents/${AGENT_NAME}.agent.md"

# ---------------------------------------------------------------------------
# Pre-flight checks
# Validate that the agent definition file exists and contains the done marker
# before attempting any runs. Failing fast here avoids wasting time on a
# misconfigured setup.
# ---------------------------------------------------------------------------
if [[ ! -f "$AGENT_FILE" ]]; then
  echo "ERROR: Agent file not found: ${AGENT_FILE}" >&2
  exit 1
fi

if ! grep -qF "$DONE_MARKER" "$AGENT_FILE"; then
  echo "ERROR: Stop marker '${DONE_MARKER}' not found in ${AGENT_FILE}" >&2
  exit 1
fi

echo "[$(date)] Pre-flight OK: agent '${AGENT_NAME}' contains stop marker."

# Ensure the docwriter-specific log sub-directory exists.
mkdir -p ./.docwriter/logs

# Maximum number of restart attempts before giving up.
# Prevents an infinite retry loop if the agent is persistently broken.
MAX_RETRIES=10
RETRY_COUNT=0

# ---------------------------------------------------------------------------
# Main retry loop
# Each iteration launches one Copilot run. The loop exits when:
#   (a) the done marker is found in the output  → success (exit 0)
#   (b) MAX_RETRIES is reached without success  → failure (exit 1)
# ---------------------------------------------------------------------------
while true; do
  # Use a Unix timestamp to give each run a unique, sortable log file name.
  TIMESTAMP=$(date +%s)
  LOG_DIR="logs"
  LOG_FILE="${LOG_DIR}/copilot_${TIMESTAMP}.log"
  # The --share file captures a human-readable summary of the run for review.
  SHARE_FILE="${LOG_DIR}/share_${TIMESTAMP}.md"

  echo "[$(date)] Starting copilot run (log: ${LOG_FILE})"

  # Launch the Copilot agent and tee all output to the timestamped log file
  # so it can be inspected after the run regardless of exit status.
  #
  # Flags:
  #   --yolo                 skip confirmation prompts (fully automated mode)
  #   --agent                which agent definition to use
  #   --disable-builtin-mcps disable built-in MCP servers (use only agent-defined ones)
  #   --log-level debug      emit verbose internal Copilot logs for diagnostics
  #   --log-dir              directory for Copilot's own debug/trace logs
  #   --share                write a shareable run summary to this path
  #   --experimental         enable experimental Copilot features
  #   --reasoning-effort     set reasoning depth to maximum (xhigh)
  #   -p "begin"             initial prompt that triggers the agent's entry point
  copilot \
    --yolo \
    --agent "docwriter" \
    --disable-builtin-mcps \
    --log-level "debug" \
    --log-dir "./.docwriter/${LOG_DIR}/" \
    --share "${SHARE_FILE}" \
    --experimental \
    --reasoning-effort xhigh \
    -p "begin" 2>&1 | tee "${LOG_FILE}"

  # Capture the Copilot exit code from the left side of the pipe.
  # $? would reflect tee's exit code, not Copilot's.
  EXIT_CODE=${PIPESTATUS[0]}

  # Check whether the agent signalled successful completion via the done marker.
  # This is the only "clean exit" condition — exit 0 here means the pipeline
  # finished its full run.
  if grep -qF "${DONE_MARKER}" "${LOG_FILE}"; then
    echo "[$(date)] Found '${DONE_MARKER}' in output. Exiting."
    exit 0
  fi

  # Increment the retry counter and bail out if the limit is reached.
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [[ ${RETRY_COUNT} -ge ${MAX_RETRIES} ]]; then
    echo "[$(date)] Reached maximum retries (${MAX_RETRIES}). Exiting." >&2
    exit 1
  fi

  # Distinguish between a crash (non-zero exit) and a silent no-op exit
  # (exit 0 without the done marker) for clearer log output, then pause
  # briefly before the next attempt to avoid hammering the API.
  if [[ ${EXIT_CODE} -ne 0 ]]; then
    echo "[$(date)] Copilot exited with code ${EXIT_CODE}. Restarting in 5s... (retry ${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 5
  else
    echo "[$(date)] Copilot exited cleanly without done marker. Restarting in 2s... (retry ${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 2
  fi
done
