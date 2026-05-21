"""
Handoff 注册中心 v2.0 — 五域一枢架构 (2026-05-21)

25条路由，按5业务域+1基础设施层组织。
域边界规则：「付钱方唯一」原则。
废弃旧VP架构（VP营销/运营/技术/财务/战略/共同服务）。
"""
from molib.agencies.handoff import create_handoff


def register_all_handoffs():
    """注册全部25条Handoff路由 — 五域一枢架构"""
    from molib.agencies.handoff import HandoffManager

    # ═══════════════════════════════════════════
    # 域一：墨育 · 教育增长域（5条）
    # 付钱方：教育机构
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="edu_acquisition_worker",
        target_worker_name="墨招·获客",
        tool_name_override="transfer_to_edu_acquisition",
        tool_description_override="教育获客：广告投放策略、增长方案、招生Leads获取、获客渠道管理（合并ads+growth）"
    )

    create_handoff(
        target_worker="edu_conversion_worker",
        target_worker_name="墨化·转化",
        tool_name_override="transfer_to_edu_conversion",
        tool_description_override="教育转化：Leads跟进、转化漏斗优化、话术A/B测试、报名率提升"
    )

    create_handoff(
        target_worker="edu_retention_worker",
        target_worker_name="墨留·留存",
        tool_name_override="transfer_to_edu_retention",
        tool_description_override="教育留存：学员续费、NPS追踪、社群运营、流失预警（教育客户专属）"
    )

    create_handoff(
        target_worker="edu_prediction_worker",
        target_worker_name="墨预·预测",
        tool_name_override="transfer_to_edu_prediction",
        tool_description_override="教育预测：招生预测仿真、定价策略模拟、市场趋势分析（MiroFish教育化）"
    )

    create_handoff(
        target_worker="edu_content_worker",
        target_worker_name="墨料·内容",
        tool_name_override="transfer_to_edu_content",
        tool_description_override="教育内容：招生文案、课程描述、案例包装、教育行业内容产出"
    )

    # ═══════════════════════════════════════════
    # 域二：墨研 · AI情报域（4条）
    # 付钱方：情报消费者（知识星球订阅用户）
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="github_radar_worker",
        target_worker_name="墨雷·雷达",
        tool_name_override="transfer_to_github_radar",
        tool_description_override="GitHub雷达：AI开源项目监控、技术趋势扫描、Star趋势追踪、竞品代码分析"
    )

    create_handoff(
        target_worker="intel_brief_worker",
        target_worker_name="墨简·简报",
        tool_name_override="transfer_to_intel_brief",
        tool_description_override="情报简报：周报生成、行业分析、竞品情报、知识星球内容输出"
    )

    create_handoff(
        target_worker="ai_review_worker",
        target_worker_name="墨测·评测",
        tool_name_override="transfer_to_ai_review",
        tool_description_override="AI评测：AI工具实测、功能对比、性价比评估、推荐榜单、测评报告"
    )

    create_handoff(
        target_worker="knowledge_base_worker",
        target_worker_name="墨档·知识库",
        tool_name_override="transfer_to_knowledge_base",
        tool_description_override="知识管理：知识沉淀、文档管理、RAG检索、知识图谱维护"
    )

    # ═══════════════════════════════════════════
    # 域三：墨媒 · IP变现域（4条）
    # 付钱方：个人粉丝/品牌合作方/课程购买者
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="content_matrix_worker",
        target_worker_name="墨笔·内容矩阵",
        tool_name_override="transfer_to_content_matrix",
        tool_description_override="个人IP内容矩阵：全平台内容产出(公众号/小红书/知乎/B站)、品牌视觉、AI生图、配音、设计（合并ip+content_writer+designer+voice_actor）"
    )

    create_handoff(
        target_worker="knowledge_product_worker",
        target_worker_name="墨课·知识产品",
        tool_name_override="transfer_to_knowledge_product",
        tool_description_override="知识付费产品：课程设计、录播制作、训练营策划、知识产品定价"
    )

    create_handoff(
        target_worker="ip_commerce_worker",
        target_worker_name="墨商·成交",
        tool_name_override="transfer_to_ip_commerce",
        tool_description_override="IP成交全链路：商务洽谈→报价→订单→交付闭环（bd+shop+order三合一）"
    )

    create_handoff(
        target_worker="live_ops_worker",
        target_worker_name="墨播·直播运营",
        tool_name_override="transfer_to_live_ops",
        tool_description_override="直播运营：直播脚本、短视频策划、直播复盘、多平台分发（视频号/抖音/B站）"
    )

    # ═══════════════════════════════════════════
    # 域四：墨海 · 出海域（3条）
    # 付钱方：台湾/东南亚用户
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="taiwan_ops_worker",
        target_worker_name="墨台·台湾",
        tool_name_override="transfer_to_taiwan_ops",
        tool_description_override="台湾运营：台湾市场内容运营、繁体适配、台区社媒矩阵、Leads转化"
    )

    create_handoff(
        target_worker="localization_worker",
        target_worker_name="墨译·本地化",
        tool_name_override="transfer_to_localization",
        tool_description_override="本地化：多语言适配、文化本地化、繁简转换、质量审核"
    )

    create_handoff(
        target_worker="sea_market_worker",
        target_worker_name="墨东·东南亚",
        tool_name_override="transfer_to_sea_market",
        tool_description_override="东南亚市场：马来西亚/新加坡市场探索、英文内容适配、Leads获取（低优先级）"
    )

    # ═══════════════════════════════════════════
    # 域五：墨创 · 一人公司域（4条）
    # 付钱方：其他一人公司/SaaS用户
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="solo_finance_worker",
        target_worker_name="墨财·财务",
        tool_name_override="transfer_to_solo_finance",
        tool_description_override="财务管理：流水记录、成本核算、API费用追踪、月报生成、预算控制"
    )

    create_handoff(
        target_worker="solo_legal_worker",
        target_worker_name="墨法·法务",
        tool_name_override="transfer_to_solo_legal",
        tool_description_override="法务合规：合同审查、合规检查、风险评估、NDA生成、隐私合规（legal+secure合规合并）"
    )

    create_handoff(
        target_worker="solo_data_worker",
        target_worker_name="墨数·数据",
        tool_name_override="transfer_to_solo_data",
        tool_description_override="跨域数据：数据汇总、BI报表、KPI看板、数据分析、效果追踪（data+data_analyst合并）"
    )

    create_handoff(
        target_worker="solo_strategy_worker",
        target_worker_name="墨策·策略",
        tool_name_override="transfer_to_solo_strategy",
        tool_description_override="战略分析：战略规划、产品决策、商业模式评估、增长飞轮设计（product+research战略合并）"
    )

    # ═══════════════════════════════════════════
    # 墨枢 · 基础设施层（5条）
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="dev_infra_worker",
        target_worker_name="墨技·技术",
        tool_name_override="transfer_to_dev_infra",
        tool_description_override="技术设施：全栈开发、系统部署、DevOps运维、AI能力集成（dev+devops+ai三合一）"
    )

    create_handoff(
        target_worker="tech_security_worker",
        target_worker_name="墨卫·安全",
        tool_name_override="transfer_to_tech_security",
        tool_description_override="技术安全：安全审计、渗透测试、漏洞扫描、安全加固（纯技术安全，非合规）"
    )

    create_handoff(
        target_worker="auto_dream",
        target_worker_name="墨梦·实验",
        tool_name_override="transfer_to_auto_dream",
        tool_description_override="AI自动化实验：快速原型开发、记忆蒸馏、自学习闭环、自动化实验"
    )

    # scrapling 和 memory 保留为基础设施 worker（不注册 handoff，内部使用）
    create_handoff(
        target_worker="scrapling_worker",
        target_worker_name="数据采集",
        tool_name_override="transfer_to_scrapling",
        tool_description_override="数据采集：网页爬取、数据抓取、信息搜集（基础设施）"
    )

    print(f"[Handoff v2.0] 已注册 {len(HandoffManager._handoffs)} 条路由 — 五域一枢架构")


if __name__ == "__main__":
    register_all_handoffs()
    from molib.agencies.handoff import HandoffManager
    manifest = HandoffManager.get_manifest()
    print(f"\n注册清单 ({len(manifest)} 条路由):")
    # 按域分组显示
    domains = {
        "墨育·教育增长": ["edu_acquisition", "edu_conversion", "edu_retention", "edu_prediction", "edu_content"],
        "墨研·AI情报": ["github_radar", "intel_brief", "ai_review", "knowledge_base"],
        "墨媒·IP变现": ["content_matrix", "knowledge_product", "ip_commerce", "live_ops"],
        "墨海·出海": ["taiwan_ops", "localization", "sea_market"],
        "墨创·一人公司": ["solo_finance", "solo_legal", "solo_data", "solo_strategy"],
        "墨枢·基础设施": ["dev_infra", "tech_security", "auto_dream", "scrapling"],
    }
    for domain, prefixes in domains.items():
        print(f"\n  ▸ {domain}:")
        for m in manifest:
            for pfx in prefixes:
                if pfx in m['target_worker']:
                    print(f"    {m['tool_name']:<35s} → {m['target_worker_name']:<10s} [{'✅' if m['enabled'] else '❌'}]")
                    break
