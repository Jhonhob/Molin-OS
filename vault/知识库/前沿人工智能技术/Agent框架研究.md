---
title: AI Agent框架深度研究
status: 活跃
last_updated: 2026-05-19
agent_sync: true
frameworks_applied:
  - 金字塔原理
  - MECE
---

对Agency仓库(226个Agent定义)的深度评估与吸收，以及多Agent教育架构设计、交互原型、技术选型。核心发现：TheAgency是墨麟OS最有价值的外部参考库。

---

## 总体判断

TheAgency是一个AI Agent人格库，每个Agent是一份结构化Markdown定义文件，包含身份定位、核心使命、工作流程、交付物规范、成功指标五个部分。与墨麟OS的SKILL.md互补——Agency的人格层可以嫁接到墨麟的SOP骨架和工具链上。

## Tier 1吸收清单(直接填补空白)

Private Domain Operator私域运营→墨域私域：企业微信架构、社群分层SOP、SCRM工具选型。Xiaohongshu Specialist小红书→银月传媒：品牌定位、微内容优化、UGC裂变。Trend Researcher趋势研究→墨研竞情：弱信号检测、跨行业模式识别。Reality Checker质量门控→门禁Agent：默认拒绝需压倒性证据才放行哲学。Cross-Border E-Commerce跨境电商→梅凝出海：Amazon/Shopee运营、多国合规。Douyin Strategist抖音→银月传媒：账号诊断到数据复盘五步。Bookkeeper财务→墨算财务：月末结账、科目对账。Agents Orchestrator Agent编排→墨梦AutoDream：多Agent编排管道13个Phase。

## 多Agent教育架构

三Agent分工模型：逻辑诊断师(发现思维漏洞)+逻辑讲解师(分类型讲解)+逻辑教练(互动纠错)。不同Agent用不同教学风格：诊断师冷静客观、讲解师生动类比、教练鼓励驱动。

技术选型：Python/BKT引擎+py-fsrs+matplotlib可视化。BKT跟踪200+知识点掌握度，SM-2动态计算复习间隔(1天→6天→指数递增)。苏格拉底式追问：不直接给答案，通过追问引导学生暴露逻辑漏洞。
