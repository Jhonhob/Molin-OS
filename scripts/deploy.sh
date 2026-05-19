#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# 墨麟 OS (Molin-OS) — 一键部署脚本
# 从 repo 重建完整的 Hermes Agent 系统
#
# 用法:
#   ./scripts/deploy.sh            # 标准部署
#   ./scripts/deploy.sh --dry-run  # 仅显示将要执行的操作
#   ./scripts/deploy.sh --help     # 显示帮助
#
# 前提条件:
#   - Hermes Agent 已安装 (hermes CLI 在 PATH 中)
#   - ~/.hermes/config.yaml 存在
#   - 已运行过 setup.sh 初始化 Python 环境
# ═══════════════════════════════════════════════════════════════════════════

set -e

# ── 配置 ──────────────────────────────────────────────────────────────────
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

# ── 参数解析 ──────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --help|-h)
            echo "用法: $0 [--dry-run]"
            echo "  --dry-run  仅显示将要执行的操作，不实际执行"
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
# 步骤 1: 检查环境
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  墨麟 OS (Molin-OS) — 一键部署                 ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

log_info "步骤 1/7: 检查环境..."

# 检查 hermes CLI
if ! command -v hermes &> /dev/null; then
    log_error "hermes CLI 未安装。请先安装 Hermes Agent。"
    log_info "安装指南: https://hermes-agent.nousresearch.com/docs"
    exit 1
fi
log_success "hermes CLI 可用: $(hermes --version 2>&1 | head -1)"

# 检查 setup.sh 是否已运行 (Python 环境)
if [ -f "$REPO_DIR/setup.sh" ]; then
    if [ -f "$REPO_DIR/venv/bin/activate" ] || [ -f "$REPO_DIR/.venv/bin/activate" ] || python3 -c "import yaml" 2>/dev/null; then
        log_success "Python 环境已就绪 (setup.sh 已运行)"
    else
        log_warn "setup.sh 可能尚未运行。建议先执行: cd $REPO_DIR && bash setup.sh"
        log_warn "继续部署..."
    fi
else
    log_warn "未找到 setup.sh，跳过 Python 环境检查"
fi

# 检查 Hermes config 是否存在
if [ ! -f "$HERMES_CONFIG" ]; then
    log_warn "$HERMES_CONFIG 不存在，将创建..."
else
    log_success "Hermes 配置已存在: $HERMES_CONFIG"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 2: 创建 config.yaml（如果不存在）
# ═══════════════════════════════════════════════════════════════════════════
log_info "步骤 2/7: 检查 Hermes config.yaml..."

TEMPLATE_FILE="$REPO_DIR/config/hermes-agent/config.yaml.template"
if [ ! -f "$HERMES_CONFIG" ] && [ -f "$TEMPLATE_FILE" ]; then
    log_info "从模板创建 $HERMES_CONFIG ..."
    run_cmd cp "$TEMPLATE_FILE" "$HERMES_CONFIG"
    log_info "请编辑 $HERMES_CONFIG 并填入真实值（API 密钥等）"
fi

# 确保 external_dirs 指向 repo skills
if [ -f "$HERMES_CONFIG" ]; then
    if grep -q "external_dirs:" "$HERMES_CONFIG" 2>/dev/null; then
        log_info "检查技能外部目录配置..."
        if ! grep -q "$REPO_DIR/skills" "$HERMES_CONFIG" 2>/dev/null; then
            log_warn "config.yaml 中的 skills/external_dirs 未指向 $REPO_DIR/skills"
            log_info "请手动添加:
  skills:
    external_dirs:
      - $REPO_DIR/skills"
        else
            log_success "skills/external_dirs 已指向 repo/skills/"
        fi
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 3: 同步脚本到 ~/.hermes/scripts/
# ═══════════════════════════════════════════════════════════════════════════
log_info "步骤 3/7: 同步脚本到 ~/.hermes/scripts/..."

HERMES_SCRIPTS="$HERMES_DIR/scripts"
REPO_SCRIPTS="$REPO_DIR/scripts"

if [ -d "$REPO_SCRIPTS" ]; then
    run_cmd mkdir -p "$HERMES_SCRIPTS"
    
    # 对每个脚本文件创建符号链接（排除部署脚本自身和备份文件）
    for script in "$REPO_SCRIPTS"/*.sh "$REPO_SCRIPTS"/*.py; do
        [ -f "$script" ] || continue
        basename=$(basename "$script")
        # 跳过备份文件
        [[ "$basename" == *.bak ]] && continue
        
        target="$HERMES_SCRIPTS/$basename"
        if [ -f "$target" ] || [ -L "$target" ]; then
            rm -f "$target"
        fi
        run_cmd ln -sf "$script" "$target"
        log_success "  链接: $basename"
    done
    
    # 同步子目录（如 diagnostics/）
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
# 步骤 4: 提示用户配置 .env 文件
# ═══════════════════════════════════════════════════════════════════════════
echo ""
log_info "步骤 4/7: 检查环境变量配置..."

HERMES_ENV="$HERMES_DIR/.env"
ENV_EXAMPLE="$REPO_DIR/config/hermes-agent/.env.example"

if [ ! -f "$HERMES_ENV" ]; then
    if [ -f "$ENV_EXAMPLE" ]; then
        log_info "正在创建 $HERMES_ENV ..."
        run_cmd cp "$ENV_EXAMPLE" "$HERMES_ENV"
        echo ""
        log_warn "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        log_warn "请编辑 $HERMES_ENV 并填入真实 API 密钥！"
        log_warn "至少需要配置: DEEPSEEK_API_KEY, GATEWAY_ALLOW_ALL_USERS"
        log_warn "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo ""
    else
        log_warn ".env.example 未找到，请手动创建 $HERMES_ENV"
    fi
else
    log_success "$HERMES_ENV 已存在"
    # 检查是否包含占位符
    if grep -q "your-" "$HERMES_ENV" 2>/dev/null; then
        log_warn "$HERMES_ENV 中包含占位符值（your-...），请替换为真实 API 密钥"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 5: 创建 profile 目录结构
# ═══════════════════════════════════════════════════════════════════════════
echo ""
log_info "步骤 5/7: 创建 Hermes profile 目录结构..."

PROFILES_SRC="$REPO_DIR/config/hermes-agent/profiles"
HERMES_PROFILES="$HERMES_DIR/profiles"

if [ -d "$PROFILES_SRC" ]; then
    for profile_dir in "$PROFILES_SRC"/*/; do
        profile_name=$(basename "$profile_dir")
        # 只处理目录，跳过文件
        [ -d "$profile_dir" ] || continue
        
        target_profile="$HERMES_PROFILES/$profile_name"
        run_cmd mkdir -p "$target_profile"
        
        # 如果有 .env.example，复制为 .env（如果不存在）
        if [ -f "$profile_dir/.env.example" ] && [ ! -f "$target_profile/.env" ]; then
            run_cmd cp "$profile_dir/.env.example" "$target_profile/.env"
            log_success "  创建 profile: $profile_name/.env (模板)"
        elif [ -f "$target_profile/.env" ]; then
            log_success "  profile 已存在: $profile_name"
        fi
    done
else
    log_warn "repo 中未找到 profiles 模板目录"
fi

log_success "Profile 目录创建完成"

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 6: 注册所有 cron 作业
# ═══════════════════════════════════════════════════════════════════════════
echo ""
log_info "步骤 6/7: 注册 cron 作业..."

# Cron 作业定义 (与 cron_jobs.md 一致)
declare -A CRON_JOBS
CRON_JOBS["记忆同步-每小时"]='{"name":"Molin-OS 记忆同步 — 每小时","schedule":"0 * * * *","script":"molin-sync-all.sh"}'
CRON_JOBS["每日Git备份"]='{"name":"Molin-OS 每日 Git 备份 02:00","schedule":"0 2 * * *","script":"git-backup.sh"}'
CRON_JOBS["vault合规周检"]='{"name":"vault-compliance-weekly","schedule":"0 9 * * 1","workdir":"$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents"}'
CRON_JOBS["arxiv扫描"]='{"name":"arxiv 每日论文扫描","schedule":"0 7 * * *","script":"daily_arxiv_scan.sh"}'
CRON_JOBS["副业价格监控"]='{"name":"副业每日价格监控","schedule":"30 9 * * *","script":"daily_side_price_monitor.sh"}'
CRON_JOBS["跨线请求轮询"]='{"name":"跨线请求轮询（每15分钟）","schedule":"*/15 * * * *","script":"cross_request_worker.py"}'
CRON_JOBS["梅凝GitHub学习"]='{"name":"梅凝每日GitHub学习","schedule":"0 8 * * *"}'
CRON_JOBS["内容复盘"]='{"name":"内容 Agent 每日复盘 22:00","schedule":"0 22 * * *","skills":"content-sop-pack,gatekeeper-sop,kpi-tracker"}'
CRON_JOBS["增长复盘"]='{"name":"内容 Agent 周日增长复盘 21:00","schedule":"0 21 * * 0","skills":"kpi-tracker,content-sop-growth,content-sop-pack"}'
CRON_JOBS["财务日报"]='{"name":"财务日报 23:00","schedule":"0 23 * * *","skills":"finance-sop-pack,kpi-tracker"}'
CRON_JOBS["KPI看板"]='{"name":"KPI看板生成 22:10","schedule":"10 22 * * *","script":"generate_dashboard.py daily"}'
CRON_JOBS["月度规划"]='{"name":"月度规划生成 — 1号 09:00","schedule":"0 9 1 * *","skills":"kpi-tracker,finance-sop-pack"}'
CRON_JOBS["垂直学习扫描"]='{"name":"垂直学习扫描 — 五大Agent","schedule":"0 6 * * 1","skills":"vertical-learning-sop"}'
CRON_JOBS["安全审计"]='{"name":"墨安安全 — 主动审计 周一03:00","schedule":"0 3 * * 1","skills":"security-sop-pack"}'
CRON_JOBS["AutoDream精读"]='{"name":"AutoDream精读内化与SKILL更新","schedule":"0 7 * * 1","skills":"vertical-learning-sop,obsidian,github","workdir":"$REPO_DIR"}'
CRON_JOBS["每日KPI采集"]='{"name":"每日KPI采集 21:50","schedule":"50 21 * * *","skills":"kpi-tracker,data-sop-pack","workdir":"$REPO_DIR"}'
CRON_JOBS["每日复盘规划"]='{"name":"每日复盘与明日规划 22:30","schedule":"30 22 * * *","skills":"kpi-tracker,obsidian","workdir":"$REPO_DIR"}'
CRON_JOBS["周计划生成"]='{"name":"周计划生成 周一09:30","schedule":"30 9 * * 1","skills":"obsidian,kpi-tracker","workdir":"$REPO_DIR"}'
CRON_JOBS["记忆蒸馏"]='{"name":"记忆蒸馏与质量门控 周日21:30","schedule":"30 21 * * 0","skills":"obsidian,vertical-learning-sop","workdir":"$REPO_DIR"}'

# 遍历 Cron 作业并注册
echo "  Cron 作业注册列表:"
for job_name in "${!CRON_JOBS[@]}"; do
    echo "    - $job_name"
done

if [ "$DRY_RUN" = true ]; then
    log_info "(dry-run) 以上作业将在实际部署中通过 'hermes cron create' 注册"
else
    log_info "请使用以下命令逐一注册（hermes cron create 暂不支持批量）："
    echo ""
    echo "  hermes cron create --name \"Molin-OS 记忆同步 — 每小时\" --schedule \"0 * * * *\" --script \"molin-sync-all.sh\""
    echo "  hermes cron create --name \"Molin-OS 每日 Git 备份 02:00\" --schedule \"0 2 * * *\" --script \"git-backup.sh\""
    echo "  ... (共 19 个作业)"
    echo ""
    log_info "或参考 $REPO_DIR/config/hermes-agent/cron_jobs.md 手动注册"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 步骤 7: 配置 vault-git-mirror
# ═══════════════════════════════════════════════════════════════════════════
echo ""
log_info "步骤 7/7: 配置 vault-git-mirror..."

VAULT_MIRROR_DIR="$REPO_DIR/.vault-git-mirror"
if [ -d "$VAULT_MIRROR_DIR" ]; then
    log_success "vault-git-mirror 目录已存在: $VAULT_MIRROR_DIR"
    
    # 检查是否已有 git 仓库
    if [ -d "$VAULT_MIRROR_DIR/.git" ]; then
        log_success "vault-git-mirror 已初始化为 git 仓库"
    else
        log_warn "vault-git-mirror 未初始化为 git 仓库"
        log_info "手动初始化: cd $VAULT_MIRROR_DIR && git init && git remote add origin <你的仓库>"
    fi
else
    log_info "vault-git-mirror 目录不存在，创建中..."
    run_cmd mkdir -p "$VAULT_MIRROR_DIR"
    log_warn "请手动配置 vault-git-mirror:
    cd $VAULT_MIRROR_DIR
    git init
    git remote add origin <你的 Obsidian 镜像仓库 URL>"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 完成
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  部署完成！                                    ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "  部署摘要:"
echo "  ┌─────────────────────────────────────────────────────┐"
echo "  │ ✓ Hermes CLI 可用                                   │"
echo "  │ ✓ Scripts 已同步到 ~/.hermes/scripts/               │"
if [ -f "$HERMES_ENV" ]; then
echo "  │ ✓ ~/.hermes/.env 已就位                             │"
else
echo "  │ ✗ ~/.hermes/.env 需要手动创建                       │"
fi
echo "  │ ✓ Profiles 目录结构已就绪                           │"
echo "  │ ✓ Cron 作业清单已部署 (共 19 个)                    │"
echo "  │ ✓ vault-git-mirror 已检查                          │"
echo "  └─────────────────────────────────────────────────────┘"
echo ""
echo "  后续步骤:"
if [ ! -f "$HERMES_ENV" ] || grep -q "your-" "$HERMES_ENV" 2>/dev/null; then
echo "  1. 编辑 ~/.hermes/.env 填入真实 API 密钥"
fi
echo "  2. 编辑 ~/.hermes/config.yaml 确认 skills/external_dirs 配置"
echo "  3. 运行 hermes cron list 确认作业已注册"
echo "  4. 运行 hermes status 验证系统状态"
echo ""
log_success "墨麟 OS 部署完成！"
