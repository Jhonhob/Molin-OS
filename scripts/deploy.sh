#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# 墨麟 OS (Molin-OS) — 部署脚本
# 在已运行 setup.sh 的基础上，将系统配置部署到 ~/.hermes/
#
# 用法:
#   ./scripts/deploy.sh            # 标准部署
#   ./scripts/deploy.sh --dry-run  # 仅显示将要执行的操作
#   ./scripts/deploy.sh --help     # 显示帮助
#
# 前提条件:
#   - 已运行 bash setup.sh 完成基础安装
#   - Hermes Agent 已安装 (hermes CLI 在 PATH 中)
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── 配置 ──
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_DIR="$HOME/.hermes"
HERMES_CONFIG="$HERMES_DIR/config.yaml"
DRY_RUN=false

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}   $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERR]${NC}  $1"; }

# ── 参数解析 ──
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --help|-h)
            echo "用法: $0 [--dry-run]"
            exit 0
            ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
done

run_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo "    (dry-run) $*"
        return 0
    fi
    "$@"
}

# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  墨麟 OS (Molin-OS) — 部署脚本                   ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 1: 检查环境
# ═══════════════════════════════════════════════════════════════════════════
log_info "步骤 1/5: 检查环境..."

if ! command -v hermes &> /dev/null; then
    log_error "hermes CLI 未安装。请先运行: bash setup.sh"
    exit 1
fi
log_success "Hermes CLI: $(hermes --version 2>&1 | head -1)"

if [ ! -f "$HERMES_CONFIG" ]; then
    log_warn "$HERMES_CONFIG 不存在，请先运行 setup.sh"
    exit 1
fi
log_success "Hermes 配置: $HERMES_CONFIG"

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 2: 同步脚本到 ~/.hermes/scripts/
# ═══════════════════════════════════════════════════════════════════════════
log_info "步骤 2/5: 同步脚本到 ~/.hermes/scripts/..."

HERMES_SCRIPTS="$HERMES_DIR/scripts"
REPO_SCRIPTS="$REPO_DIR/scripts"

if [ -d "$REPO_SCRIPTS" ]; then
    run_cmd mkdir -p "$HERMES_SCRIPTS"
    
    for script in "$REPO_SCRIPTS"/*.sh "$REPO_SCRIPTS"/*.py; do
        [ -f "$script" ] || continue
        basename=$(basename "$script")
        [[ "$basename" == deploy.sh ]] && continue  # 跳过部署脚本自身
        
        target="$HERMES_SCRIPTS/$basename"
        [ -f "$target" ] || [ -L "$target" ] && rm -f "$target"
        run_cmd ln -sf "$script" "$target"
        log_success "  链接: $basename"
    done
    
    # 同步子目录
    for subdir in "$REPO_SCRIPTS"/*/; do
        [ -d "$subdir" ] || continue
        subname=$(basename "$subdir")
        target_sub="$HERMES_SCRIPTS/$subname"
        run_cmd mkdir -p "$target_sub"
        for f in "$subdir"*; do
            [ -f "$f" ] || continue
            b=$(basename "$f")
            [ -L "$target_sub/$b" ] && rm -f "$target_sub/$b"
            run_cmd ln -sf "$f" "$target_sub/$b"
        done
        log_success "  链接目录: $subname/"
    done
else
    log_warn "repo 中未找到 scripts/ 目录"
fi

log_success "脚本同步完成"

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 3: 配置 skills 外部目录
# ═══════════════════════════════════════════════════════════════════════════
echo ""
log_info "步骤 3/5: 配置技能外部目录..."

if [ -f "$HERMES_CONFIG" ]; then
    if ! grep -q "$REPO_DIR/skills" "$HERMES_CONFIG" 2>/dev/null; then
        log_warn "config.yaml 中未配置 skills/external_dirs"
        log_info "请手动添加到 $HERMES_CONFIG:"
        echo "  skills:"
        echo "    external_dirs:"
        echo "      - $REPO_DIR/skills"
    else
        log_success "skills/external_dirs 已指向 $REPO_DIR/skills"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 4: 配置 .env 校验
# ═══════════════════════════════════════════════════════════════════════════
echo ""
log_info "步骤 4/5: 校验环境变量..."

HERMES_ENV="$HERMES_DIR/.env"
if [ -f "$HERMES_ENV" ]; then
    if grep -q "your-" "$HERMES_ENV" 2>/dev/null; then
        log_warn "$HERMES_ENV 中包含占位符，请替换为真实 API 密钥"
    else
        log_success "$HERMES_ENV 已配置"
    fi
else
    log_warn "$HERMES_ENV 不存在，请从模板创建:"
    log_info "  cp $REPO_DIR/config/hermes-agent/.env.example $HERMES_ENV"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 5: 注册 Cron 作业
# ═══════════════════════════════════════════════════════════════════════════
echo ""
log_info "步骤 5/5: 注册 Cron 作业..."

CRON_DEFS="$REPO_DIR/config/hermes-agent/cron_jobs.md"
if [ -f "$CRON_DEFS" ]; then
    log_info "参考 $CRON_DEFS 注册 19 个 Cron 作业"
    log_info "示例: hermes cron create --name \"作业名\" --schedule \"* * * * *\" --script \"脚本.py\""
else
    log_warn "cron_jobs.md 未找到"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 完成
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  部署完成！                                    ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "  后续步骤:"
echo "  1. 编辑 $HERMES_DIR/.env → 填入 API 密钥"
echo "  2. 运行 hermes cron list → 确认作业已注册"
echo "  3. 运行 hermes -m '系统就绪测试' → 验证功能"
echo ""
log_success "完成！"
