---
purpose: "各 Agent 每日 GitHub Trending 快速掃描的輕量輸出模板"
usage: "取代（或補充）每週深度5問模板，用於每日 quick scan + 金字塔摘要"
destination: "决策/{Agent}｜GitHub.md"
note: "⚠️ 實際 vault 目錄名稱為簡體「决策」而非傳統「決策」。分隔符為全形「｜」pipe，非「·」middle dot。詳見 Agent ID 對照表中各 Agent 的實際檔案路徑。"
---

# 模板：Agent 每日 GitHub 學習筆記（金字塔格式）

## frontmatter

```yaml
---
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
agent: {agent_id}      # edu/research/global/media/dev/autodream
category: 決策           # 決策目錄（非學習檔案）
status: 活躍
confidence: 已验证
importance: ⭐⭐⭐
source: GitHub Trending 每日學習
tags: [決策, {agent_name}, GitHub學習, {領域標籤}]
---
```

## 金字塔內容結構

### 結論

一句話總結今天學到的最有價值信息。
❌ 「今天看了三個有趣項目」
✅ 「Medusa 開源電商平台模組化架構 + 內建翻譯模組，可作為跨境電商基礎設施方案」

### 背景

為什麼關注這些項目、今天學習的出發點。

### 核心內容

每個項目一種完整結構：

```
{N}. **{owner/repo} ⭐ {stars}k — 一句亮點摘要**

   - 定位與描述（1-2句）
   - **技術架構或核心特色**（如語言、框架、設計模式）
   - **對 {Agent} 業務的價值**（具體對應什麼場景）
   - **關鍵學到**（具體可用的知識點、可借鑑的做法）
```

限制：核心內容不超過 8 條（每個項目 1 條，最多 3-4 個項目）

### 下一步

```
- [ ] 具體可執行的行動計劃 1
- [ ] 具體可執行的行動計劃 2
```

## Agent ID 對照表（含實際檔案路徑）

| Agent | agent_id | 實際檔案路徑 | 領域標籤 |
|-------|----------|------------|---------|
| 元瑤（墨學教育） | edu | `决策/元瑤｜GitHub.md` | 教育科技 |
| 銀月（墨筆/墨圖） | media | `决策/銀月｜GitHub.md` | 內容創作 |
| **梅凝（墨海出海）** | **global** | **`决策/梅凝｜GitHub.md`** | **出海運營** |
| 宋玉（副業） | side | `决策/宋玉｜GitHub.md` | 副業探索 |
| 系統（通用） | system | `决策/系統｜GitHub.md` | 通用 |

## 注意事項

- 永遠使用「追加模式」：每個日期一條 `## 【今日學習】YYYY-MM-DD` 為標題條目，不覆蓋舊內容
- 更新 frontmatter 的 `updated` 日期為當天
- frontmatter 其他欄位（agent/category/status/confidence/importance/source）保持不變
- 使用繁體中文（台灣用語）
- **重點是「學到什麼」，不是項目列表** — 每個條目必須包含具體的可學知識點，而非單純描述專案功能
- **結論必須是中文且有實質內容**，不能是「今天看了三個專案」這類填充台詞
- **Cron 排程限制**：若由 cron 驅動，不可使用 clarify 工具提問、不可使用記憶功能（cron 環境不可用）、無使用者互動。結果直接以最終回覆輸出，cron 會自動投遞
