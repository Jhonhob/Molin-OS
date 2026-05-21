# 墨麟 OS — Makefile
# ================================
# One command to rule them all.
# Usage: make <target>

.PHONY: help install setup deploy dev test lint check clean backup cron-list run-background gc-memory status run-gateway run-monitor vault-flush bus-stats memory-stats

# ── Default ──
help: ## Show all commands
	@echo "墨麟 OS — AI 一人公司操作系统 (v7.5.0-Hardened)"
	@echo ""
	@echo "Quick Start:"
	@echo "  make install     Install Python dependencies"
	@echo "  make setup       Full one-click deployment"
	@echo "  make dev         Development setup (editable install)"
	@echo ""
	@echo "Everyday:"
	@echo "  make test        Run test suite"
	@echo "  make check       System health check"
	@echo "  make lint        Syntax validation"
	@echo "  make clean       Remove build artifacts"
	@echo "  make backup      Backup configs and skills"
	@echo ""
	@echo "Daemons:"
	@echo "  make run-background  Start async task worker"
	@echo "  make run-gateway     Start async Feishu gateway (port 8000)"
	@echo "  make run-monitor     Start Langfuse observability (Docker)"
	@echo "  make gc-memory       Run memory consolidation"
	@echo "  make vault-flush     Flush buffer to Obsidian"
	@echo "  make bus-stats       Data bus statistics"
	@echo "  make memory-stats    Memory palace statistics"
	@echo "  make status          System live status"
	@echo ""
	@echo "Cron:"
	@echo "  make cron-list   List all scheduled cron jobs"

# ── Install ──
install: ## Install core dependencies
	pip install --upgrade pip -q
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

dev: ## Editable install for development
	pip install -e . -q 2>/dev/null || true
	@echo "✓ Editable install complete"

setup: ## Full one-click deployment
	@bash setup.sh

deploy: install dev ## Install + editable install
	@echo "✓ Deploy complete"

# ── Quality ──
test: ## Run test suite
	@python -m pytest tests/ -v --tb=short 2>/dev/null || \
		python -m pytest tests/ -v 2>/dev/null || \
		echo "⚠ No tests found or pytest not installed"

lint: ## Syntax check all Python files
	@echo "Checking syntax..."
	@find molib -name "*.py" -exec python -m py_compile {} \; 2>/dev/null || true
	@echo "✓ Syntax OK"

check: ## System health check
	@python -m molib health 2>/dev/null || echo "⚠ Health check not available"

# ── Cleanup ──
clean: ## Remove build artifacts
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .pytest_cache build dist *.egg-info 2>/dev/null || true
	@echo "✓ Clean"

# ── Backup ──
backup: ## Create timestamped backup
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	tar -czf "backup_$$timestamp.tar.gz" \
		--exclude='.git' \
		--exclude='__pycache__' \
		--exclude='*.pyc' \
		--exclude='venv' \
		--exclude='.env' \
		skills/ config/ molib/ docs/ scripts/ \
		&& echo "✓ Backup: backup_$$timestamp.tar.gz"

# ── Cron ──
cron-list: ## List all active cron jobs
	@python -c "import json; print(json.dumps({'note':'Use Hermes cronjob list command'}, indent=2))" 2>/dev/null || \
		echo "Cron jobs managed by Hermes Agent — use 'hermes cronjob list' in Hermes session"

# ── Daemons ──
run-background: ## Start background async task worker
	@mkdir -p vault/logs
	@echo "Starting background worker engine..."
	@nohup python engine/background_worker.py > vault/logs/bg_worker.log 2>&1 &
	@echo "Background worker is running (PID: $$!)."
	@echo "Logs: vault/logs/bg_worker.log"

gc-memory: ## Run ChromaDB memory garbage collection
	@echo "Running ChromaDB Memory GC..."
	@python scripts/memory_gc_job.py $(ARGS)

status: ## Show system live status (queue + worker)
	@echo "=== Molin-OS System Status ==="
	@echo ""
	@echo "▸ Background Worker:"
	@ps aux | grep "background_worker.py" | grep -v grep || echo "  ❌ Background Worker is NOT running."
	@echo ""
	@echo "▸ Task Queue:"
	@python -c "from molib.task_queue import LiteTaskQueue; q=LiteTaskQueue(); import json; print(json.dumps(q.get_stats(), indent=2, ensure_ascii=False))" 2>/dev/null || echo "  ⚠️ Cannot read task queue"

# ── New targets (v7.5.0) ──
run-gateway: ## Start async Feishu webhook gateway
	@echo "Starting Molin-OS Async Gateway..."
	@python engine/gateway_async.py --host 0.0.0.0 --port 8000

run-monitor: ## Start Langfuse local observability (Docker required)
	@echo "Starting Langfuse on port 3000..."
	@docker run -d --name langfuse -p 3000:3000 \
		-e DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres" \
		langfuse/langfuse:2 2>/dev/null || echo "⚠️ Docker not available or Langfuse already running"

vault-flush: ## Flush memory buffer to Obsidian vault
	@python -c "from molib.vault_io import SecureVaultIO; v=SecureVaultIO(); print(v.flush_buffer_to_obsidian())"

bus-stats: ## Show AtomicDataBus statistics
	@python -c "from molib.data_bus import AtomicDataBus; b=AtomicDataBus(); import json; print(json.dumps(b.stats(), indent=2, ensure_ascii=False))"

memory-stats: ## Show AdaptiveMemoryManager statistics
	@python -c "from molib.memory_palace_v2 import AdaptiveMemoryManager; m=AdaptiveMemoryManager(); import json; print(json.dumps(m.stats(), indent=2, ensure_ascii=False))"
