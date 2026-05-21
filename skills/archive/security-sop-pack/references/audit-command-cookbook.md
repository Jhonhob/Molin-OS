# 安全审计命令速查表

## 密钥年龄检查

```bash
# 检查单个密钥文件最后修改时间 (macOS)
stat -f "%Sm" ~/.hermes/.env

# 检查所有 profile 密钥文件
stat -f "%Sm" ~/.hermes/profiles/*/.env
stat -f "%Sm" ~/Molin-OS/.env
stat -f "%Sm" ~/.hermes/config.yaml

# 检查密钥文件权限（应 600）
ls -la ~/.hermes/.env
ls -la ~/.hermes/profiles/*/.env
```

## GITHUB_TOKEN 权限检查

```bash
# 查看完整 scope 列表
curl -sI -H "Authorization: token $(grep GITHUB_TOKEN ~/Molin-OS/.env | cut -d= -f2)" \
  https://api.github.com/ | grep -i x-oauth-scopes

# 查看 token 所属用户
curl -s -H "Authorization: token $(grep GITHUB_TOKEN ~/Molin-OS/.env | cut -d= -f2)" \
  https://api.github.com/user | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('login'), d.get('type'))"
```

## Git 密钥泄露检查

```bash
# 检查当前 HEAD 中是否有密钥硬编码
cd ~/Molin-OS && git grep -n 'ghp_\|sk-\|sm_\|fc-\|api_key\|TOKEN=\|SECRET=' HEAD \
  -- ':!.env' ':!**/.env' ':!*.example' ':!node_modules' ':!.git' | grep -v '__pycache__'

# 检查 Git 历史中是否有 .env 文件提交
git log --all --name-only --format="%h %s" -- '*.env'

# 检查 .gitignore 是否覆盖了密钥模式
grep -E '\.env|secret|password|token|credential|key$' .gitignore

# 检查已删除的密钥文件记录
git log --all --diff-filter=D --name-only --format="%h %s" -- '*.env'
```

## CVE 扫描

```bash
# 安装 pip-audit（如未安装）
pip3 install pip-audit

# 扫描 requirements.txt
pip-audit --requirement requirements.txt --desc

# 扫描所有已安装的 Python 包
pip-audit --desc

# 查看关键包的已安装版本
python3 -c "
import pkg_resources
for pkg in ['aiohttp','cryptography','httpx','numpy','openai','pillow',
            'playwright','pyyaml','requests','sqlalchemy']:
    try:
        v = pkg_resources.get_distribution(pkg).version
        print(f'{pkg}: {v}')
    except: pass
"

# 列出过期包
python3 -m pip list --outdated
```

## Profile 密钥一致性检查

```bash
# 检查所有 profile 是否使用相同的 Key
for f in ~/.hermes/profiles/*/.env; do
  echo "=== $(basename $(dirname $f)) ==="
  grep -v '^#' "$f" | grep -v '^$'
done

# 提取各 profile 的 DEEPSEEK_API_KEY 并比较
grep -h DEEPSEEK_API_KEY ~/.hermes/profiles/*/.env | sort -u
grep -h SUPERMEMORY_API_KEY ~/.hermes/profiles/*/.env | sort -u
```

## Obsidian 输出路径

```bash
# Obsidian vault 物理路径（iCloud）
ls ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/

# 安全审计输出位置
ls ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/产出/

# 使用 output_writer 写入（Python）
python3 -c "
from molib.memory.output_writer import write_agent_output
write_agent_output(
    agent_id='security',
    output_type='active_audit',
    goal='审计目标',
    summary='摘要',
    analysis='分析',
    actions='行动项',
    risks='风险',
    learnings='可复用知识',
    relay_path='security/audit_YYYYMMDD.json',
)
"
```

## 快速验证清单

```bash
# 一行检查：密钥年龄 + Git泄露 + 权限
echo "=== Key Age ===" && \
  stat -f "%Sm %N" ~/.hermes/.env && \
  echo "=== Git Secrets ===" && \
  cd ~/Molin-OS && git grep -c 'ghp_\|sk-\|sm_' HEAD -- ':!.env' ':!*.example' 2>/dev/null && \
  echo "=== Token Scope ===" && \
  curl -sI -H "Authorization: token $(grep GITHUB_TOKEN .env 2>/dev/null | cut -d= -f2)" \
    https://api.github.com/ 2>/dev/null | grep -o 'x-oauth-scopes:.*'
```
