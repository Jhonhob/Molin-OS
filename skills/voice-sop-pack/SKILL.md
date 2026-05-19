---
name: voice-sop-pack
description: 墨声配音 Agent SOP 技能包 — AI语音合成/配音/播客制作/音频内容标准化
category: molin-org
version: 1.0.0
tags: [sop, voice, audio, tts, podcast, dubbing]
trigger: 所有语音相关任务（配音/TTS/播客制作/音频内容）必须先加载此技能
---

# 墨声配音 Agent SOP 技能包

## 适用 Agent
- 墨声配音 (voice_actor.py)
- 集成：molin-audio-engine, songwriting, text-to-speech

---

## 一、Lead SOP（配音需求获取）

### 需求来源

| 来源 | 方式 | 优先级 |
|------|------|--------|
| 视频 Agent 联动 | 短视频脚本生成后自动触发配音需求 | P0 |
| 播客制作 | 播客脚本完成 | P1 |
| 教育 Agent 联动 | 课程音频内容 | P1 |
| 独立配音请求 | 直接指定 | P2 |

### 需求标准化

```yaml
voice_request:
  text_source: "脚本文件路径或文本"
  language: "zh-CN / zh-TW / en"
  voice_style: "专业/亲和/故事/教学/活泼"
  gender: "male / female"
  speed: 1.0  # 0.8-1.5
  output_format: "mp3 / wav"
  duration_estimate: "秒（可选）"
  background_music: "轻快/情感/无"
  use_case: "短视频配音 / 播客 / 课程讲解 / 广告"
```

---

## 二、Execution SOP（配音制作流程）

### 配音制作流水线

```
文本输入 → 语音合成 → 音质检查 → 后期处理 → 输出交付
```

### Step 1: 文本预处理

配音前文本优化：
- 数字读法标注（"2026年" → "二零二六年"）
- 英文缩写处理（"API" → "A-P-I" 或 "艾派" 按上下文）
- 标点替换（长句加逗号分割便于断句）
- 情感标记插入（[兴奋] [低沉] [强调]）

### Step 2: 语音合成

| 场景 | 推荐工具 | 参数 |
|------|----------|------|
| 短视频配音 | molin-audio-engine | 语速 1.1-1.2x，清晰活泼 |
| 播客 | molin-audio-engine | 语速 1.0x，自然对话感 |
| 课程讲解 | text-to-speech | 语速 0.9-1.0x，清晰稳重 |
| 广告/推广 | molin-audio-engine | 语速 1.2x，激昂有感染力 |

### Step 3: 音质检查

检查项：
- [ ] 无杂音/爆音
- [ ] 断句自然，无机器感
- [ ] 语气与内容情感匹配
- [ ] 语速符合场景要求
- [ ] 音量一致（无突然增大/减小）
- [ ] 多段拼接处过渡流畅

### Step 4: 后期处理

- BGM 匹配（如果要求）
- 音量归一化（-14 LUFS 标准）
- 首尾淡入淡出
- 格式转换（按要求输出）

### Step 5: 输出交付

- 音频文件 → `relay/audio/{type}_{timestamp}.mp3`
- 元数据 → 同目录 `_meta.json`（时长/采样率/参数）
- 视频联动：音频路径传递给 Video Agent 合入视频

---

## 三、QA SOP（音频质量质检）

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 语音自然度 | 30% | 是否接近真人发音 |
| 语速适配 | 20% | 是否符合场景要求 |
| 情感表达 | 20% | 语气是否匹配内容 |
| 音质 | 15% | 无杂音/失真/爆音 |
| 文本准确性 | 15% | 是否完全按文本念 |



---

## 四、Escalation SOP

| 场景 | 触发 | 动作 |
|------|------|------|
| TTS API 故障 | 连续 3 次生成失败 | 切换备选 TTS Provider |
| 音质不达标 | QA 音质分 < 70 | 重新生成 + 换参数 |
| 文本朗读错误 | 关键术语读错 | 修正文本标注后重生成 |

---

## 五、Cron 经营节奏

| 时间 | 任务 | 产出 |
|------|------|------|
| 跟随短视频 Cron | 短视频配音 | 音频文件 |
| 按需 | 播客/课程配音 | 音频文件 |

---

## 六、集成

### 视频联动
```
video-sop-pack 脚本完成
    ↓ 文本传给 voice-sop
配音生成
    ↓ 音频返回
视频合成（配音+画面+字幕）
```

### 内容联动
```
内容 Agent 产出（适合音频化的内容）
    ↓ 标记 needs_audio: true
voice-sop 播客版制作
    ↓
发布到播客平台
```

---

## 七、参考

- TTS 配置：`text-to-speech` tool 配置
- BGM 库：`supermemory_search("背景音乐库")`
- 配音规范：各 skill 的具体参数
