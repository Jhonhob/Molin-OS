# 设计 Agent Prompt 模板集

## 通用封面图 Prompt 模板

### 模板 1：小红书封面（1080×1440, 3:4）

```
A vertical cover image for Xiaohongshu (RED), 3:4 aspect ratio.
Style: {写实/插画/3D/极简/国风}
Main subject: {核心视觉元素，具体描述}
Color scheme: {主色} + {强调色} + {背景色}
Mood: {专业/温暖/活力/高级感/治愈}
Key requirements:
- Top 1/3 reserved for text overlay (CTA/标题)
- Clean composition, not cluttered
- Brand color accent: {品牌色代码}
- {其他要求}
Resolution: 1080×1440px
```

### 模板 2：公众号封面（900×500, 16:9）

```
A landscape cover image for WeChat Official Account, 16:9 ratio.
Style: {写实/插画/3D/极简/国风}
Main subject: {具体主题}
Color scheme: {主色} + {强调色}
Mood: {专业/温暖/高级感}
Key requirements:
- Center space clear for text overlay (title)
- Wide left-right format
- {其他要求}
Resolution: 900×500px
```

### 模板 3：广告图（1200×628, 1.91:1）

```
A horizontal ad banner, 1.91:1 ratio.
Style: {写实/插画/产品展示}
Main subject: {产品/服务核心卖点}
Color scheme: {主色} + CTA按钮强调色{M}
Mood: 专业+行动导向
Key requirements:
- CTA button area clearly defined (right side)
- Product/feature visible
- Text area on left
- Brand logo top-left corner
- {其他要求}
Resolution: 1200×628px
```

---

## 品牌色卡（墨麟）

| 用途 | 色号 | RGB |
|------|------|-----|
| 品牌主色 | #??? | (?, ?, ?) |
| 强调色 | #??? | (?, ?, ?) |
| 背景色 | #??? | (?, ?, ?) |
| 文字色 | #??? | (?, ?, ?) |

> ⚠️ 品牌色卡需要从 supermemory 获取最新版本

---

## 各平台设计规范

### 小红书
- 封面 1080×1440（3:4），文字在上方 1/3
- 配图 1080×1080（1:1）
- 风格：生活化/真实感/不硬广
- 避免：过度文字堆砌、过度 PS

### 抖音
- 封面 1080×1920（9:16）
- 文字在中间区域，上下留白
- 风格：冲击力/刷到即停
- 封面文字不超过 15 字

### 公众号
- 封面 900×500（16:9）
- 配图 1080×1080（1:1）
- 风格：专业/简洁/辨识度高
- 封面可放 logo 水印

### SEO 站点
- 特色图 1200×630（1.91:1）
- 风格：信息图风格/关键词可视化
- 图片 alt 标签要写

---

## 设计自检清单

### 通用
- [ ] 分辨率满足平台要求
- [ ] 无色差/锯齿
- [ ] 文字清晰可读
- [ ] 品牌色使用正确
- [ ] 无 AI 明显瑕疵

### 平台特定
- [ ] 尺寸符合目标平台
- [ ] 格式正确（JPG/PNG/WebP）
- [ ] 文件大小在平台限制内
- [ ] 文字未超出安全区域

### 合规
- [ ] 无版权图片/字体
- [ ] 无敏感内容
- [ ] 图片上文字不包含违规承诺
