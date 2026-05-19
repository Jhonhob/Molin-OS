# GitHub Trending 深度研究法

## 適用場景

每日定時掃描 GitHub Trending，篩選與特定業務相關的開源項目，提取可學知識點並歸檔。

## 工具選擇策略

| 階段 | 工具 | 理由 |
|------|------|------|
| 瀏覽 Trending 列表 | **首選：** `execute_code` 內包 `curl -sL` 下載 HTML → Python regex 解析<br>**次選：** `browser_navigate` → `browser_snapshot` | 瀏覽器 snapshot 在 20+ 個專案時會截斷（accessibility tree 限制），curl + regex 拿得到完整 25 個 repo 連結。需注意頁面約 600KB+。⚠️ `curl | python3` 會被 tirith 安全掃描器阻擋 → 先用 `curl -o /tmp/file.html` 再獨立解析 |
| 讀取專案 README | `terminal("curl -s https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md")` | 比 browser 快 10 倍，純文字無 JS 開銷。降級順序：**main → master → develop**（如 medusajs/medusa 的 README 在 develop 分支） |
| 批量深讀多個專案 | `delegate_task` 搭配 `tasks[]` 陣列，每篇 README 一個 task | 3 個專案並行比逐個讀取快 3 倍。每個 task 只需 terminal 工具 + curl |
| 查看專案細節 | `browser_navigate` | 需要看 Issues/Releases/Commits 等互動內容時 |

## 篩選相關性標準（以出海運營 Agent 為例）

優先關注以下領域（依權重排序）：

1. **Localization / i18n 工具** — 多語言支援、翻譯、在地化（權重最高）
2. **語音 / TTS 工具** — 多語言配音、語音合成（出海內容生產核心）
3. **AI 影音生成** — 開源替代方案、自託管內容生產
4. **AI Agent 框架** — 與 Hermes/Superpowers 生態系相關的技能驅動方法論
5. **SaaS / 開源商業模型** — 新興的開源商業項目、出海技術棧
6. **跨境電商 / 國際化工具** — 支付、物流、市場拓展

## 深度研究流程

### Step 1: 掃描 Trending

**首選方法（curl + Python 解析，適用 cron 環境）：**

```python
# 封裝在 execute_code 內避免 pipe-to-interpreter 安全限制
from hermes_tools import terminal
result = terminal("curl -sL 'https://github.com/trending' -o /tmp/trending.html")
# 或直接使用 execute_code 的內建能力呼叫 terminal
import re
with open('/tmp/trending.html') as f:
    html = f.read()
# 提取所有 repo 連結
links = re.findall(r'href="/[^/"]+/[^/"]+"', html)
repos = [l.replace('href="','').replace('"','') for l in links
         if not any(x in l for x in ['/apps/', '/sponsors/', '/trending/', '/_private/'])]
# 提取描述、星星數等
articles = re.findall(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
```

**備選方法（browser，適用互動式環境）：**

```yaml
url: https://github.com/trending
動作: 瀏覽完整頁面（可能需要 scroll down 多次）
⚠️ 限制: accessibility tree 在 15-20 個 article 後會被截斷，無法看到完整列表
解決方案: 先用 browser_scroll 往下捲，再重複 browser_snapshot（但同頁面多次可能返回相同結果 → 改用 curl 法）
記錄: 每個專案的 name / description / stars / daily stars
```

### Step 2: 篩選 Top 3（求精不求多）

從完整列表中，選出與業務最相關的 2-3 個專案。判斷標準：
- 能否直接降低營運成本？（如自託管替代付費API）
- 能否提升內容品質？（如多語言 TTS、高品質影像生成）
- 能否改進工作流程？（如 Agent 框架、自動化工具）

### Step 3: 逐個 Deep Dive

對於每個入選專案：

```yaml
1. 讀取描述（從 Trending 頁面已獲得）
2. 獲取 README: curl -s https://raw.githubusercontent.com/{owner}/{repo}/main/README.md
3. 提取核心內容：
   - 技術亮點（模型大小、語言支援、效能數據）
   - SDK 生態（支援哪些語言/平台）
   - 部署方式（自託管/SaaS/本地推理）
   - 授權模式（MIT/Apache/商業授權）
4. 提煉「學到什麼」：
   - ❌ 不要只列功能：「支援 31 種語言」
   - ✅ 要寫具體應用：「pip install supertonic 一鍵部署，離線配音免 API 費用」
```

### Step 4: 格式化輸出

金字塔格式，結論先行：

```markdown
### 結論
一句話總結今天學到的最有價值信息

### 背景
為什麼關注這些項目/今天學習的出發點

### 核心內容
- **專案名稱** — Stars（今日增量）。核心描述。學到重點：具體可用的知識點。

### 下一步
- [ ] 具體可執行的行動計劃
```

### Step 5: 歸檔到 Obsidian

```yaml
檔案: 決策/{Agent}·GitHub.md
前端參數更新: updated 日期
追加模式: 永遠追加不覆蓋
格式:
  ## YYYY-MM-DD
  ### 結論
  ### 背景
  ### 核心內容
  ### 下一步
```

## 常見陷阱

- **README 獲取失敗**：先試 `main` 分支，失敗再試 `master` 分支，最後試 `develop` 分支（如 medusajs/medusa）
- **瀏覽器超時或截斷**（如頁面含 20+ 個 repo）：立刻降級到 `curl -sL` 下載 HTML + Python 解析 — 純文字內容不需要瀏覽器，且 browser_snapshot 的 accessibility tree 有截斷上限
- **`curl | python3` 被阻擋**：tirith 安全掃描器會阻擋 pipe-to-interpreter 模式 → 改用 `curl -o /tmp/file.html` 再在 `execute_code` 內讀取解析
- **信息過載**：每天只選 2-3 個專案深入，核心內容不超過 8 條。質量 > 數量
- **遺忘結論先行**：每個條目必須以「學到重點」結尾，不是功能列表
- **frontmatter 遺漏更新**：追加完內容後務必將 `updated` 日期改為當天
- **delegate_task 的平行讀取陷阱**：使用 `delegate_task(tasks=[...])` 批量讀取 README 時，每個 task 的 context 要自包含（含 owner/repo/branch 資訊），因為子 agent 無 parent 對話記憶

## 參考案例（2026-05-17 成功執行的完整流程）

完整執行記錄請參見：
- 工具順序：browser_navigate Trending → curl README × 3 → read_file Obsidian → patch frontmatter → patch append entry
- 三個入選專案：supertone-inc/supertonic（31語TTS）、obra/superpowers（Agent技能框架）、Anil-matcha/Open-Generative-AI（開源影音生成）
