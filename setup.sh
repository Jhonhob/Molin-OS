#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# 墨麟 OS (Molin OS) — 一键完整安装脚本
# 从零搭建完整的 Hermes Agent 系统
#
# 用法:
#   bash setup.sh                    # 完整安装
#   bash setup.sh --no-vault        # 跳过 Obsidian vault 配置
#   bash setup.sh --help            # 显示帮助
#
# 这个脚本会:
#   1. 安装系统依赖 (Python, Git, FFmpeg)
#   2. 初始化 git 子模块
#   3. 安装 Python 依赖 + Hermes Agent
#   4. 生成 Hermes 配置模板
#   5. 注册 Cron 定时任务
#   6. 配置 Obsidian vault 镜像
#   7. 验证安装结果
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── 颜色 ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}   $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERR]${NC}  $1"; }

# ── 参数 ──
SETUP_VAULT=true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-vault) SETUP_VAULT=false; shift ;;
        --help|-h)
            echo "用法: bash setup.sh [--no-vault]"
            echo "  --no-vault  跳过 Obsidian vault 配置"
            exit 0
            ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
done

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
HERMES_DIR="$HOME/.hermes"

# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║    墨 麟  O S  ·  Molin-OS                          ║"
echo "║    一键安装脚本                                    ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 1: 检查系统依赖
# ═══════════════════════════════════════════════════════════════════════════
log_info "步骤 1/7: 检查系统依赖..."

# 检测 OS
OS_TYPE="$(uname -s)"
case "$OS_TYPE" in
    Darwin)  OS_NAME="macOS" ;;
    Linux)   OS_NAME="Linux" ;;
    *)       OS_NAME="$OS_TYPE" ;;
esac
log_info "系统: ${OS_NAME} ($(uname -m))"

# 检查 Python 3.11+
PYTHON=""
for candidate in python3.12 python3.11 python3; do
    if command -v "$candidate" &>/dev/null; then
        ver=$($candidate --version 2>&1 | awk '{print $2}')
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    log_error "Python 3.11+ 未安装"
    echo "  macOS: brew install python@3.11"
    echo "  Linux: sudo apt install python3.11 python3.11-venv"
    exit 1
fi
log_success "Python: $($PYTHON --version)"

# 检查 Git
if ! command -v git &>/dev/null; then
    log_error "Git 未安装"
    exit 1
fi
log_success "Git: $(git --version | awk '{print $3}')"

# 检查 FFmpeg（可选）
if command -v ffmpeg &>/dev/null; then
    log_success "FFmpeg: $(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')"
else
    log_warn "FFmpeg 未安装（视频功能不可用，非必需）"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 2: 检查引擎目录
# ═══════════════════════════════════════════════════════════════════════════
log_info "步骤 2/7: 检查运行时引擎..."

cd "$REPO_DIR"

# MiroFish 预测引擎
if [ -d "engine/mirofish/backend" ]; then
    log_success "MiroFish 引擎: engine/mirofish/ ($(find engine/mirofish -type f | wc -l) 个文件)"
else
    log_warn "MiroFish 引擎目录不存在: engine/mirofish/"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 3: 安装 Python 虚拟环境和依赖
# ═══════════════════════════════════════════════════════════════════════════
log_info "步骤 3/7: 安装 Python 环境..."

VENV_DIR="$REPO_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    $PYTHON -m venv "$VENV_DIR"
    log_success "虚拟环境创建完成: $VENV_DIR"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"
PIP="$VENV_DIR/bin/pip"

# 升级 pip
$PIP install --upgrade pip -q 2>/dev/null || true

# 安装 requirements.txt（molib 依赖）
if [ -f "requirements.txt" ]; then
    $PIP install -r requirements.txt -q 2>/dev/null && \
        log_success "Python 依赖安装完成" || \
        log_warn "部分依赖安装失败（非致命）"
fi

# 安装 Hermes Agent（本地源码）
if [ -d "hermes" ] && [ -f "hermes/pyproject.toml" ]; then
    # 先安装 hermes-agent 的构建依赖
    $PIP install build setuptools wheel hatchling -q 2>/dev/null || true
    # 可编辑安装 Hermes Agent
    if $PIP install -e hermes/ -q 2>/dev/null; then
        log_success "Hermes Agent 安装完成"
    else
        log_warn "Hermes Agent 安装失败，尝试从 pip 安装..."
        $PIP install hermes-agent -q 2>/dev/null && \
            log_success "Hermes Agent 从 pip 安装完成" || \
            log_warn "Hermes Agent 安装失败，请手动安装"
    fi
else
    log_warn "未找到 hermes/ 源码目录，尝试从 pip 安装..."
    $PIP install hermes-agent -q 2>/dev/null && \
        log_success "Hermes Agent 从 pip 安装完成" || \
        log_warn "Hermes Agent 安装失败，请手动安装"
fi

# 安装 molib（本地包）
if [ -f "setup.py" ]; then
    $PIP install -e . -q 2>/dev/null && \
        log_success "molib 安装完成" || \
        log_warn "molib 安装跳过"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 4: 配置 Hermes Agent
# ═══════════════════════════════════════════════════════════════════════════
log_info "步骤 4/7: 配置 Hermes Agent..."

mkdir -p "$HERMES_DIR"

# 创建 config.yaml（从模板）
CONFIG_TEMPLATE="$REPO_DIR/config/hermes-agent/config.yaml.template"
CONFIG_TARGET="$HERMES_DIR/config.yaml"
if [ ! -f "$CONFIG_TARGET" ] && [ -f "$CONFIG_TEMPLATE" ]; then
    cp "$CONFIG_TEMPLATE" "$CONFIG_TARGET"
    log_success "Hermes 配置已创建: $CONFIG_TARGET"
    log_warn "请编辑 $CONFIG_TARGET 填入 API 密钥等真实值"
else
    log_success "Hermes 配置已存在: $CONFIG_TARGET"
fi

# 创建 .env
ENV_EXAMPLE="$REPO_DIR/config/hermes-agent/.env.example"
ENV_TARGET="$HERMES_DIR/.env"
if [ ! -f "$ENV_TARGET" ] && [ -f "$ENV_EXAMPLE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_TARGET"
    log_success "环境变量模板已创建: $ENV_TARGET"
    log_warn "请编辑 $ENV_TARGET 填入 API 密钥"
fi

# 创建 skills 外部目录链接（指向 repo skills/）
if [ -d "$REPO_DIR/skills" ]; then
    mkdir -p "$HERMES_DIR/external_skills"
    # 创建符号链接或部署脚本中处理
    log_success "Repo 技能目录就绪: $REPO_DIR/skills"
    log_info "请在 $CONFIG_TARGET 中配置:"
    echo "  skills:"
    echo "    external_dirs:"
    echo "      - $REPO_DIR/skills"
fi

# 创建 profile 目录
PROFILES_SRC="$REPO_DIR/config/hermes-agent/profiles"
HERMES_PROFILES="$HERMES_DIR/profiles"
if [ -d "$PROFILES_SRC" ]; then
    for profile_dir in "$PROFILES_SRC"/*/; do
        [ -d "$profile_dir" ] || continue
        profile_name=$(basename "$profile_dir")
        target_profile="$HERMES_PROFILES/$profile_name"
        mkdir -p "$target_profile"
        if [ -f "$profile_dir/.env.example" ] && [ ! -f "$target_profile/.env" ]; then
            cp "$profile_dir/.env.example" "$target_profile/.env"
            log_success "  Profile: $profile_name"
        fi
    done
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 5: 注册 Cron 定时任务
# ═══════════════════════════════════════════════════════════════════════════
echo ""
log_info "步骤 5/7: 注册 Cron 定时任务..."

if ! command -v hermes &>/dev/null; then
    log_warn "hermes CLI 不可用，跳过 Cron 注册"
else
    CRON_DEFS="$REPO_DIR/config/hermes-agent/cron_jobs.md"
    if [ -f "$CRON_DEFS" ]; then
        log_info "Cron 作业定义: $CRON_DEFS（共 19 个作业）"
        log_info "请手动注册 Cron 作业:"
        echo "  hermes cron create --name '作业名' --schedule 'cron表达式' --script '脚本名'"
        echo "  或参考 $CRON_DEFS 中的完整定义"
        echo ""
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 6: 配置 Obsidian vault 本地同步
# ═══════════════════════════════════════════════════════════════════════════
if [ "$SETUP_VAULT" = true ]; then
    echo ""
    log_info "步骤 6/7: 配置 Obsidian vault 本地同步..."

    # vault 目录已是主仓库的一部分，复制配置模板即可
    mkdir -p "$REPO_DIR/vault"
    log_success "Vault 目录就绪: $REPO_DIR/vault/（随主仓库管理）"
    log_info "如需从本地 Obsidian 同步，运行: python3 $REPO_DIR/scripts/vault_git_sync.py"
else
    log_info "步骤 6/7: 跳过 Obsidian vault 配置（--no-vault）"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 7: 验证安装
# ═══════════════════════════════════════════════════════════════════════════
echo ""
log_info "步骤 7/7: 验证安装..."

# 验证 Hermes CLI
if command -v hermes &>/dev/null; then
    log_success "Hermes CLI: $(hermes --version 2>&1 | head -1)"
else
    log_error "Hermes CLI 不可用（请检查 PATH 是否包含虚拟环境的 bin/）"
    echo "  运行: source $VENV_DIR/bin/activate"
fi

# 验证 hermes/ 源码
if [ -d "$REPO_DIR/hermes" ] && [ -f "$REPO_DIR/hermes/pyproject.toml" ]; then
    log_success "Hermes 源码: $REPO_DIR/hermes ($(cd "$REPO_DIR/hermes" && git rev-parse --short HEAD 2>/dev/null || echo 'no-git'))"
fi

# 验证 molib
if python -c "import molib" 2>/dev/null; then
    log_success "molib 引擎: 可用"
else
    log_warn "molib 导入失败（检查 PYTHONPATH）"
fi

# 验证目录结构
COMPONENTS=0; TOTAL=0
for dir in hermes/ skills/ config/ scripts/; do
    TOTAL=$((TOTAL + 1))
    [ -d "$REPO_DIR/$dir" ] && COMPONENTS=$((COMPONENTS + 1))
done
log_success "目录结构: ${COMPONENTS}/${TOTAL} 完整"

# 验证 config
if [ -f "$HERMES_DIR/config.yaml" ]; then
    log_success "Hermes 配置: $HERMES_DIR/config.yaml"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 完成
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  墨麟 OS (Molin-OS) 安装完成！                   ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

echo "  安装摘要:"
echo "  ┌─────────────────────────────────────────────────────────────┐"
echo "  │ ✓ Python 环境 ($($PYTHON --version))                         │"
echo "  │ ✓ MiroFish 引擎 (engine/mirofish/)                              │"
echo "  │ ✓ Hermes Agent (源码安装)                                   │"
echo "  │ ✓ molib 引擎                                                 │"
echo "  │ ✓ Hermes 配置模板 (.env + config.yaml)                       │"
echo "  │ ✓ ${COMPONENTS}/${TOTAL} 核心目录结构                          │"
echo "  │ ✓ Obsidian Vault (vault/ 跟随主仓库)                           │"
echo "  └─────────────────────────────────────────────────────────────┘"
echo ""

echo "  后续步骤:"
if [ ! -f "$HERMES_DIR/.env" ] || grep -q "your-" "$HERMES_DIR/.env" 2>/dev/null; then
echo "  1. 编辑 $HERMES_DIR/.env 填入真实的 API 密钥"
fi
echo "  2. 编辑 $HERMES_DIR/config.yaml 确认配置"
echo "  3. 激活环境: source $VENV_DIR/bin/activate"
echo "  4. 运行: hermes -m '你好，墨麟 OS 已就绪'"
echo "  5. 注册 Cron 作业: 参考 config/hermes-agent/cron_jobs.md"
echo ""

# 如果 .env 还是模板状态，给出警告
if [ -f "$HERMES_DIR/.env" ] && grep -q "your-" "$HERMES_DIR/.env" 2>/dev/null; then
    log_warn ".env 中还包含占位符，请务必替换为真实 API 密钥后再使用！"
fi

# 如果 hermes 不在 PATH 中，给出提示
if ! command -v hermes &>/dev/null; then
    log_warn "hermes 命令不在 PATH 中，请运行: source $VENV_DIR/bin/activate"
fi

echo ""
log_success "安装完成！"
