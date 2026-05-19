# 五方法学习协议 v1.0

吸收来源: RetainCraft (kaixiad/RetainCraft)
依据: Donoghue & Hattie 2021 元分析 (250+研究, 数万样本)
适用: Coach Agent 教学方法选择器
集成: BKT引擎 (StruggleDetector + InterventionAdvisor)

## 协议目标

根据学员当前BKT掌握概率 + 烧脑状态，自动选择最有效的教学方法。
不是"所有学员用同一套话术"，而是"诊断驱动的方法匹配"。

## 五方法一览

| 方法 | 效应量(d) | 适用场景 | Coach Agent指令 |
|------|-----------|----------|-----------------|
| 分布式练习 | 0.85 | 任何学员，间隔复习 | SRS排期引擎选择最优复习时间 |
| 练习测试 | 0.74 | BKT高+烧脑(可能是slip) | 同知识点换题型再测 |
| 自我解释 | 0.54 | BKT中低+烧脑 | 让学员讲出解题思路(费曼法) |
| 交错练习 | 0.47 | BKT中高+正常 | 混合已掌握知识点出题 |
| 精细探究 | 0.56 | BKT中+烧脑 | 为什么式追问，引导深度思考 |

## 状态-方法匹配矩阵

```
学员状态                    BKT范围   烧脑?   优先方法
──────────────────────────────────────────────────────
健康状态                    >0.7      否      分布式练习(维持)
轻度薄弱                    0.4-0.7   否      交错练习 + 分布式练习
卡壳(可能slip)              >0.6      是      练习测试(换题型确认)
中度卡壳                    0.4-0.6   是      精细探究 + 自我解释
严重烧脑                    <0.4      是      自我解释 + 降级到前置知识
疲惫/连续错>5              任意      是(3级) 休息 + 情感鼓励(非教学)
```

## Coach Agent 调用接口

### 方法: select_method()

输入:
- bkt_p: float (0-1, BKT掌握概率)
- struggle_level: int (0-3, 烧脑级别)
- depth_flag: str (deep|tool, 知识点类型)
- kp_id: str (知识点ID)

输出:
- method: str (方法名)
- effect_size: float (效应量)
- prompt_template: str (话术模板)
- action: str (Coaching指令)

### 方法: generate_prompt(method, kp_id, bkt_p)

根据方法类型 + 知识点类型，生成Coach Agent的初始话术:

分布式练习:
  场景: 知识点掌握良好，需要巩固
  话术: "上一周我们学了{方法}，还记得怎么用吗？试试这道题"

练习测试:
  场景: 怀疑是一时失误(slip)
  话术: "同样的思路，换一种出题方式，看看能不能做对"
  如果再次答错 -> 升级为精细探究

自我解释:
  场景: 卡壳，需要理清思路
  话术: "不急着给答案，说说你是怎么想的。每一步的理由是什么？"
  追问: "那你觉得这个思路在哪里卡住了？"

交错练习:
  场景: 掌握度中等，需要打破块状记忆
  话术: "今天我们混着练，这道题和前面那道有点像但不太一样"
  知识点混合规则: 当前KP + 1个已掌握KP + 1个相关KP

精细探究:
  场景: 卡壳在中等掌握的知识点
  话术: "你选了这个答案，原因是什么？有没有其他可能性？"
  追问模式: 为什么->为什么不->如果换一个条件呢?

## 与BKT引擎的集成

InterventionAdvisor.advise() 已实现上述匹配逻辑:

- heavy干预: BKT<0.4 + struggling -> 自我解释 + 降级
- medium干预: BKT 0.4-0.6 + struggling -> 精细探究 + 自我解释
- light干预: BKT>0.6 + struggling -> 练习测试(换题型)
- normal: 无需干预

advise_schedule() 已实现优先级排期:
- P1: 烧脑中 -> 立即干预
- P2: BKT<0.4 -> 分布式练习(SRS)
- P3: BKT 0.4-0.7 -> 交错练习

## 协议使用示例

学员状态: L5_模型化思维, BKT=0.03, struggle_level=2
-> InterventionAdvisor.advise() 返回:
  intervention_level: heavy
  suggested_methods: ["self_explanation"]
  action: "学员连续错误...1.情感鼓励 2.降级到前置基础 3.自我解释"

学员状态: L1_有序思维, BKT=0.81, struggle_level=0
-> InterventionAdvisor.advise() 返回:
  intervention_level: normal
  action: "学员状态正常，继续推进"

学员状态: L3_分类思维, BKT=0.65, struggle_level=2
-> InterventionAdvisor.advise() 返回:
  intervention_level: light
  suggested_methods: ["practice_testing"]
  action: "BKT较高但答错，可能slip，换题型再测"
