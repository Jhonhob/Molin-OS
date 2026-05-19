---
name: ecommerce-sop-pack
description: 墨链电商 Agent SOP 技能包 — 订单管理/库存/交易/平台对接标准化
category: molin-org
version: 1.0.0
tags: [sop, ecommerce, order, transaction, inventory]
trigger: 所有电商相关任务（订单处理/库存检查/交易管理）必须先加载此技能
---

# 墨链电商 Agent SOP 技能包

## 适用 Agent
- 墨链电商 (ecommerce.py)
- 集成：molin-order

---

## 一、Lead SOP（订单/交易数据采集）

### 数据源

| 数据源 | 采集方式 | 频次 | 优先级 |
|--------|----------|------|--------|
| 闲鱼待处理订单 | 闲鱼 API 轮询 | 每小时 | P0 |
| 已完成订单 | 闲鱼订单历史 | 每日 | P1 |
| 退货/售后单 | 售后系统 | 实时 | P0 |
| 支付对账 | 支付平台 | 每日 | P1 |

### 订单标准化

所有订单统一格式：

```json
{
  "order_id": "XY20260517001",
  "platform": "xianyu",
  "status": "pending / paid / shipped / completed / refunded / cancelled",
  "customer": {"id": "xxx", "name": "xxx"},
  "items": [{"sku": "xxx", "name": "xxx", "qty": 1, "price": 100}],
  "total": 100,
  "paid_at": "2026-05-17T14:00:00+08:00",
  "shipped_at": null,
  "delivery": {"method": "快递", "tracking": null}
}
```

---

## 二、Execution SOP（订单处理流程）

### 订单全生命周期管理

```
订单创建 → 付款确认 → 发货 → 物流追踪 → 签收确认 → 售后跟进
```

### Step 1: 待处理订单检查
- 每小时检查待付款/待发货订单
- 超时未付款订单 → 自动催付消息
- 超时未发货订单 → 告警

### Step 2: 发货确认
- 接收到发货通知后更新物流信息
- 自动发送发货通知给买家
- 追踪物流异常（延迟/退回）

### Step 3: 售后处理
- 退货申请 → 检查退货政策
- 退款申请 → 确认退款金额
- 售后工单 → 转墨声客服跟进

### Step 4: 每日对账
- 订单金额 vs 实际收款
- 手续费计算
- 异常交易标记

---

## 三、QA SOP（订单数据质检）

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 订单准确性 | 30% | 商品/数量/金额匹配 |
| 状态一致性 | 25% | 各系统状态同步一致 |
| 时效性 | 20% | 订单是否在 SLA 时间内处理 |
| 物流准确性 | 15% | 物流单号正确，跟踪有效 |
| 对账完整性 | 10% | 资金流与订单流匹配 |

---

## 四、Escalation SOP

| 场景 | 触发 | 动作 |
|------|------|------|
| 订单长时间未处理 | > 24 小时未发货 | L1 通知 |
| 退款纠纷 | 买家投诉到平台 | L2 审批 + 转人工 |
| 支付对账不平 | 金额偏差 > 5% | L1 通知 |
| 库存不足 | 超卖 | 暂停销售 + 通知补货 |

---

## 五、Cron 经营节奏

| 时间 | 任务 | 产出 |
|------|------|------|
| 每小时 | 待处理订单检查 + 自动催付/发货提醒 | 处理动作 |
| 每日 21:00 | 日对账（订单 vs 收入） | 对账报告 |
| 每周日 | 电商周报（销量/收入/退货率） | 周报 |

---

## 六、集成

### 财务联动
```
电商订单收入 → relay/ecommerce_revenue_{date}.json
    ↓ finance-sop-pack 读取
财务日报 → 收入分析
```

### 客服联动
```
售后需求
    ↓ 
service-sop-pack 售后 SOP
    ↓ 处理结果回写
订单状态更新
```

---

## 七、参考

- 平台 API：闲鱼 API 文档
- 商品 SKU 表：`supermemory_search("商品列表")`
- 售后政策：`supermemory_search("退货政策")`
- Agent 模板：`skill_view('agent-sop-template')`
