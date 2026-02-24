#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$PROJECT_ROOT/.pids"

RAG_DIR="$PROJECT_ROOT/rag-service"
GATEWAY_DIR="$PROJECT_ROOT/api-gateway"

RAG_HOST="0.0.0.0"
RAG_PORT="8000"

mkdir -p "$PID_DIR"

log() { printf "%s\n" "$*"; }

die() {
  echo "ERROR: $*" >&2
  exit 1
}

find_venv_python() {
  # Try common venv folder names inside rag-service
  local candidates=(
    "$RAG_DIR/.venv/bin/python"
    "$RAG_DIR/venv/bin/python"
    "$RAG_DIR/env/bin/python"
  )

  for p in "${candidates[@]}"; do
    if [ -x "$p" ]; then
      echo "$p"
      return 0
    fi
  done

  return 1
}

is_running_pidfile() {
  local pid_file="$1"
  if [ ! -f "$pid_file" ]; then
    return 1
  fi
  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"
  if [ -z "$pid" ]; then
    return 1
  fi
  kill -0 "$pid" 2>/dev/null
}

start_ollama() {
  local pid_file="$PID_DIR/ollama.pid"
  local log_file="$PID_DIR/ollama.log"

  # If already running (by pidfile) keep it
  if is_running_pidfile "$pid_file"; then
    log "Ollama already running (PID $(cat "$pid_file"))."
    return 0
  fi

  # If running without pidfile, do not start another
  if pgrep -x "ollama" >/dev/null 2>&1; then
    log "Ollama already running (detected via pgrep)."
    return 0
  fi

  command -v ollama >/dev/null 2>&1 || die "ollama not found in PATH. Install Ollama first."

  log "Starting Ollama..."
  nohup ollama serve >"$log_file" 2>&1 &
  echo $! >"$pid_file"
  log "Ollama started (PID $(cat "$pid_file")). Logs: $log_file"
}

start_rag() {
  local pid_file="$PID_DIR/rag.pid"
  local log_file="$PID_DIR/rag.log"

  if is_running_pidfile "$pid_file"; then
    log "rag-service already running (PID $(cat "$pid_file"))."
    return 0
  fi

  [ -d "$RAG_DIR" ] || die "rag-service directory not found: $RAG_DIR"

  local venv_python=""
  if venv_python="$(find_venv_python)"; then
    :
  else
    die "Could not find venv python in rag-service (.venv/venv/env). Create venv and install deps first."
  fi

  log "Starting rag-service using venv python: $venv_python"
  cd "$RAG_DIR"

  # Use the venv python to run uvicorn, no reliance on global uvicorn
  nohup "$venv_python" -m uvicorn app.main:app \
    --app-dir "src" \
    --host "$RAG_HOST" \
    --port "$RAG_PORT" \
    >"$log_file" 2>&1 &


  echo $! >"$pid_file"
  log "rag-service started (PID $(cat "$pid_file")). Logs: $log_file"
}

start_gateway() {
  local pid_file="$PID_DIR/gateway.pid"
  local log_file="$PID_DIR/gateway.log"

  if is_running_pidfile "$pid_file"; then
    log "api-gateway already running (PID $(cat "$pid_file"))."
    return 0
  fi

  [ -d "$GATEWAY_DIR" ] || die "api-gateway directory not found: $GATEWAY_DIR"
  command -v node >/dev/null 2>&1 || die "node not found in PATH. Install Node.js first."

  cd "$GATEWAY_DIR"

  # Install deps if node_modules missing (safe dev convenience)
  if [ ! -d "$GATEWAY_DIR/node_modules" ]; then
    if command -v npm >/dev/null 2>&1; then
      log "node_modules not found. Running npm install..."
      npm install >/dev/null
    else
      die "npm not found in PATH (needed to install gateway deps)."
    fi
  fi

  log "Starting api-gateway with: node src/server.js"
  nohup node src/server.js >"$log_file" 2>&1 &
  echo $! >"$pid_file"
  log "api-gateway started (PID $(cat "$pid_file")). Logs: $log_file"
}

stop_one() {
  local name="$1"
  local pid_file="$PID_DIR/$name.pid"

  if [ ! -f "$pid_file" ]; then
    log "$name: no pid file (already stopped)."
    return 0
  fi

  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"
  if [ -z "$pid" ]; then
    rm -f "$pid_file"
    log "$name: empty pid file removed."
    return 0
  fi

  if kill -0 "$pid" 2>/dev/null; then
    log "Stopping $name (PID $pid)..."
    kill "$pid" 2>/dev/null || true

    # Give it a moment; then hard kill if needed
    sleep 0.5
    if kill -0 "$pid" 2>/dev/null; then
      log "$name still alive, sending SIGKILL..."
      kill -9 "$pid" 2>/dev/null || true
    fi
  else
    log "$name: stale pid $pid (not running)."
  fi

  rm -f "$pid_file"
  log "$name stopped."
}

status() {
  for name in ollama rag gateway; do
    local pid_file="$PID_DIR/$name.pid"
    if is_running_pidfile "$pid_file"; then
      log "$name: running (PID $(cat "$pid_file"))"
    else
      log "$name: not running"
    fi
  done
}

health() {
  echo "Health checks:"

  # Ollama
  if curl -fsS --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "  ollama: OK"
  else
    echo "  ollama: FAIL"
  fi

  # rag-service (porta 8000)
  if curl -fsS --max-time 2 http://127.0.0.1:8000/docs >/dev/null 2>&1; then
    echo "  rag-service: OK"
  else
    echo "  rag-service: FAIL"
  fi

  # api-gateway (porta 3000)
  if curl -fsS --max-time 2 http://127.0.0.1:3000/health >/dev/null 2>&1; then
    echo "  api-gateway: OK"
  else
    echo "  api-gateway: FAIL"
  fi
}

start_all() {
  start_ollama
  start_rag
  start_gateway
  log "All services started."
}

stop_all() {
  stop_one gateway
  stop_one rag
  stop_one ollama
  log "All services stopped."
}

usage() {
  cat <<EOF
Usage: ./dev.sh {start|stop|restart|status|logs}

Commands:
  start    Start ollama, rag-service, api-gateway in background
  stop     Stop all services started by this script (via pid files)
  restart  Stop then start
  status   Show status based on pid files
  logs     Tail logs (gateway + rag + ollama)
  health   Run HTTP checks for ollama, rag-service, api-gateway
EOF
}

logs() {
  log "Tailing logs (Ctrl+C to exit)..."
  tail -n 200 -f \
    "$PID_DIR/gateway.log" \
    "$PID_DIR/rag.log" \
    "$PID_DIR/ollama.log"
}

cmd="${1:-}"
case "$cmd" in
  start) start_all ;;
  stop) stop_all ;;
  restart) stop_all; start_all ;;
  status) status ;;
  logs) logs ;;
  health) health ;;
  *) usage; exit 1 ;;
esac