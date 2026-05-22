"""
Handoff 注册中心 v8.0 — 六司四十一将架构 (2026-05-22)

44条路由，按6司（紫灵/元瑶/银月/梅凝/宋玉/玄骨）组织。
宋玉 v8.0 Songyu 修正：恢复 B2B 企业服务定位（墨商/墨案/墨关/墨聚/墨采）。
新增9个Agent：墨标/墨测/墨单(闲鱼)/墨试/墨文/墨排/墨汇/墨荐/墨路
"""
from molib.agencies.handoff import create_handoff


def register_all_handoffs():
    """注册全部41条Handoff路由 — 六司四十一将架构"""
    from molib.agencies.handoff import HandoffManager

    # ═══════════════════════════════════════════
    # 紫灵 · 情报雷达公司 (7条)
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="ziling.scanner",
        target_worker_name="墨嗅·情报抓取",
        tool_name_override="transfer_to_ziling_scanner",
        tool_description_override="每日情报抓取机器：arXiv/行业博客/竞品动态定时扫描，生成情报简报"
    )

    create_handoff(
        target_worker="ziling.spy",
        target_worker_name="墨影·竞品侦探",
        tool_name_override="transfer_to_ziling_spy",
        tool_description_override="7×24数字竞品侦探：竞品动态监控、产品更新追踪、市场份额分析"
    )

    create_handoff(
        target_worker="ziling.seo",
        target_worker_name="墨标·SEO关键词",
        tool_name_override="transfer_to_ziling_seo",
        tool_description_override="SEO关键词猎取：长尾关键词挖掘、搜索意图分析、关键词难度评估、内容选题建议"
    )

    create_handoff(
        target_worker="ziling.analyst",
        target_worker_name="墨数·数据分析",
        tool_name_override="transfer_to_ziling_analyst",
        tool_description_override="业务数据分析师：KPI看板生成、数据清洗、趋势可视化、异常检测"
    )

    create_handoff(
        target_worker="ziling.researcher",
        target_worker_name="墨研·研报蒸馏",
        tool_name_override="transfer_to_ziling_researcher",
        tool_description_override="结构化研报蒸馏：竞品深度研究、行业白皮书、投资备忘录、知识星球付费内容"
    )

    create_handoff(
        target_worker="ziling.validator",
        target_worker_name="墨测·MVP验证",
        tool_name_override="transfer_to_ziling_validator",
        tool_description_override="MVP最小验证：快速原型测试、市场需求验证、最小可行产品评估、上线前检查"
    )

    create_handoff(
        target_worker="ziling.invest",
        target_worker_name="墨投·ROI精算",
        tool_name_override="transfer_to_ziling_invest",
        tool_description_override="ROI精算与成本管控：项目投资回报测算、预算分配、成本效益分析、资源优化建议"
    )

    # ═══════════════════════════════════════════
    # 元瑶 · 知识变现公司 (8条)
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="yuanyao.growth",
        target_worker_name="墨增·公域引流",
        tool_name_override="transfer_to_yuanyao_growth",
        tool_description_override="公域流量猎手：小红书/抖音/知乎获客策略、投放优化、引流钩子设计"
    )

    create_handoff(
        target_worker="yuanyao.closer",
        target_worker_name="墨销·销售成交",
        tool_name_override="transfer_to_yuanyao_closer",
        tool_description_override="后端销售成交：私聊转化话术、朋友圈剧本、发售操盘、逼单策略"
    )

    create_handoff(
        target_worker="yuanyao.tutor",
        target_worker_name="墨导·督学复购",
        tool_name_override="transfer_to_yuanyao_tutor",
        tool_description_override="班主任/用户成功：学习进度追踪、作业批改反馈、续费提醒、NPS回访"
    )

    create_handoff(
        target_worker="yuanyao.curriculum",
        target_worker_name="墨学·课程设计",
        tool_name_override="transfer_to_yuanyao_curriculum",
        tool_description_override="教研课程设计：课程大纲规划、教学内容开发、练习题库设计、教学效果评估"
    )

    create_handoff(
        target_worker="yuanyao.pm",
        target_worker_name="墨创·产品经理",
        tool_name_override="transfer_to_yuanyao_pm",
        tool_description_override="知识产品经理：新产品概念验证、课程产品迭代、用户需求调研、竞品课程分析"
    )

    create_handoff(
        target_worker="yuanyao.community",
        target_worker_name="墨域·私域社群",
        tool_name_override="transfer_to_yuanyao_community",
        tool_description_override="私域社群操盘手：社群运营SOP、RFM分层管理、活动策划、用户裂变设计"
    )

    create_handoff(
        target_worker="yuanyao.order",
        target_worker_name="墨单·闲鱼接单",
        tool_name_override="transfer_to_yuanyao_order",
        tool_description_override="闲鱼接单运营：商品上架优化、自动回复话术、订单跟踪、评价管理、GMV统计"
    )

    create_handoff(
        target_worker="yuanyao.abtest",
        target_worker_name="墨试·A/B测试",
        tool_name_override="transfer_to_yuanyao_abtest",
        tool_description_override="A/B测试科学家：文案/定价/落地页多变量测试、统计显著性分析、实验设计"
    )

    # ═══════════════════════════════════════════
    # 银月 · 内容获客公司 (7条)
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="yinyue.writer",
        target_worker_name="墨笔·短内容",
        tool_name_override="transfer_to_yinyue_writer",
        tool_description_override="爆款短内容主笔：小红书/公众号/知乎短文创作、标题优化、情绪钩子设计"
    )

    create_handoff(
        target_worker="yinyue.designer",
        target_worker_name="墨图·视觉设计",
        tool_name_override="transfer_to_yinyue_designer",
        tool_description_override="AI视觉设计师：封面图/信息图/品牌素材生成、视觉风格统一、图片AIGC"
    )

    create_handoff(
        target_worker="yinyue.editor",
        target_worker_name="墨剪·视频剪辑",
        tool_name_override="transfer_to_yinyue_editor",
        tool_description_override="视频后期剪辑：短视频切片、字幕生成、转场特效、BGM匹配、多平台格式适配"
    )

    create_handoff(
        target_worker="yinyue.seowriter",
        target_worker_name="墨文·SEO长文",
        tool_name_override="transfer_to_yinyue_seowriter",
        tool_description_override="SEO深度长文：博客/知乎长文创作、关键词密度优化、内链策略、EEAT合规"
    )

    create_handoff(
        target_worker="yinyue.streamer",
        target_worker_name="墨播·AI直播",
        tool_name_override="transfer_to_yinyue_streamer",
        tool_description_override="AI直播主播：直播脚本策划、实时互动话术、产品讲解、直播间氛围管理"
    )

    create_handoff(
        target_worker="yinyue.pr",
        target_worker_name="墨星·品牌公关",
        tool_name_override="transfer_to_yinyue_pr",
        tool_description_override="品牌人设公关：IP人设维护、媒体关系、危机公关预案、品牌故事输出"
    )

    create_handoff(
        target_worker="yinyue.scheduler",
        target_worker_name="墨排·内容调度",
        tool_name_override="transfer_to_yinyue_scheduler",
        tool_description_override="内容发布总调度：内容日历管理、多平台定时发布、发布节奏优化、数据回收触发"
    )

    # ═══════════════════════════════════════════
    # 梅凝 · 出海收汇公司 (6条)
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="meining.translator",
        target_worker_name="墨译·本地化",
        tool_name_override="transfer_to_meining_translator",
        tool_description_override="母语级本地化翻译：多语言翻译、文化适配、繁简转换、翻译质量审核"
    )

    create_handoff(
        target_worker="meining.growth",
        target_worker_name="墨媒·海外社媒",
        tool_name_override="transfer_to_meining_growth",
        tool_description_override="海外社媒运营：Twitter/LinkedIn/ProductHunt内容运营、海外KOL合作、社区管理"
    )

    create_handoff(
        target_worker="meining.webmaster",
        target_worker_name="墨站·独立站",
        tool_name_override="transfer_to_meining_webmaster",
        tool_description_override="独立站操盘手：Shopify/WordPress建站、SEO优化、转化率优化、Landing Page设计"
    )

    create_handoff(
        target_worker="meining.payment",
        target_worker_name="墨汇·跨境支付",
        tool_name_override="transfer_to_meining_payment",
        tool_description_override="跨境支付收汇：Stripe/PayPal配置、多币种结算、汇率优化、拒付处理"
    )

    create_handoff(
        target_worker="meining.compliance",
        target_worker_name="墨盾·合规风控",
        tool_name_override="transfer_to_meining_compliance",
        tool_description_override="合规风控护城河：GDPR/CCPA合规检查、税务合规、知识产权审查、内容合规"
    )

    create_handoff(
        target_worker="meining.distribution",
        target_worker_name="墨荐·产品分发",
        tool_name_override="transfer_to_meining_distribution",
        tool_description_override="产品分发发版：App Store/Google Play/Product Hunt上架、版本管理、审核应对"
    )

    # ═══════════════════════════════════════════
    # 宋玉 · 产品孵化公司 (8条) — v8.0 产品孵化+威客接单
    # 从 B2B 企业服务转型为产品孵化: 墨图纸/墨架/墨钩/墨对/墨冷/墨价/墨单/墨开
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="songyu.prd",
        target_worker_name="墨图纸·产品需求",
        tool_name_override="transfer_to_songyu_prd",
        tool_description_override="产品需求文档：定义产品愿景、用户故事、功能规格与验收标准，输出完整PRD驱动开发"
    )

    create_handoff(
        target_worker="songyu.stack",
        target_worker_name="墨架·技术选型",
        tool_name_override="transfer_to_songyu_stack",
        tool_description_override="技术选型与架构设计：根据PRD选择最优技术栈、设计系统架构、搭建项目骨架与开发环境"
    )

    create_handoff(
        target_worker="songyu.hook",
        target_worker_name="墨钩·钩子工具",
        tool_name_override="transfer_to_songyu_hook",
        tool_description_override="钩子工具开发：设计并开发免费引流产品（小工具/计算器/模板），用工具换注册，积累种子用户"
    )

    create_handoff(
        target_worker="songyu.appeal",
        target_worker_name="墨对·用户诉求",
        tool_name_override="transfer_to_songyu_appeal",
        tool_description_override="用户诉求与价值主张：提炼产品一句话定位，撰写落地页文案与用户沟通话术，让用户秒懂产品价值"
    )

    create_handoff(
        target_worker="songyu.cold",
        target_worker_name="墨冷·冷启动",
        tool_name_override="transfer_to_songyu_cold",
        tool_description_override="冷启动策略：种子用户获取、社区冷启动运营、初始增长黑客方案设计、早期用户反馈收集"
    )

    create_handoff(
        target_worker="songyu.pricing",
        target_worker_name="墨价·定价策略",
        tool_name_override="transfer_to_songyu_pricing",
        tool_description_override="定价策略设计：竞品定价对标、付费模型设计（订阅/一次性/分层）、价格弹性测试、A/B定价实验"
    )

    create_handoff(
        target_worker="songyu.freelance",
        target_worker_name="墨单·威客接单",
        tool_name_override="transfer_to_songyu_freelance",
        tool_description_override="威客接单运营：猪八戒平台半自动化运营，每日巡检新项目、智能匹配投标、GMV统计与接单优化"
    )

    create_handoff(
        target_worker="songyu.launch",
        target_worker_name="墨开·产品发布",
        tool_name_override="transfer_to_songyu_launch",
        tool_description_override="产品发布执行：Product Hunt首发策划、渠道分发协调、发布日作战室、T+7发版复盘与数据回收"
    )

    # ═══════════════════════════════════════════
    # 玄骨 · 系统中枢公司 (8条)
    # ═══════════════════════════════════════════

    create_handoff(
        target_worker="xuanhu.developer",
        target_worker_name="墨码·全栈研发",
        tool_name_override="transfer_to_xuanhu_developer",
        tool_description_override="全栈代码研发：Python/Next.js全栈开发、API设计、数据库建模、代码审查"
    )

    create_handoff(
        target_worker="xuanhu.ops",
        target_worker_name="墨维·运维灾备",
        tool_name_override="transfer_to_xuanhu_ops",
        tool_description_override="运维灾备守护：服务器监控、自动备份、灾备演练、SSL证书管理、Cron健康检查"
    )

    create_handoff(
        target_worker="xuanhu.security",
        target_worker_name="墨安·安全审计",
        tool_name_override="transfer_to_xuanhu_security",
        tool_description_override="安全红队审计：漏洞扫描、渗透测试、依赖安全审计、API密钥泄露检测"
    )

    create_handoff(
        target_worker="xuanhu.autodream",
        target_worker_name="墨梦·自进化",
        tool_name_override="transfer_to_xuanhu_autodream",
        tool_description_override="自进化引擎：记忆蒸馏、技能自动优化、Prompt自我改进、架构自修复"
    )

    create_handoff(
        target_worker="xuanhu.finance",
        target_worker_name="墨算·财务管控",
        tool_name_override="transfer_to_xuanhu_finance",
        tool_description_override="财务总监CFO：API成本追踪、Token消耗统计、月度财报生成、预算预警"
    )

    create_handoff(
        target_worker="xuanhu.legal",
        target_worker_name="墨律·法务合规",
        tool_name_override="transfer_to_xuanhu_legal",
        tool_description_override="法务合规过滤：合同条款审查、知识产权风险评估、隐私政策生成、NDA模板"
    )

    create_handoff(
        target_worker="xuanhu.hr",
        target_worker_name="墨人·调度管理",
        tool_name_override="transfer_to_xuanhu_hr",
        tool_description_override="算力与任务调度：Worker负载均衡、任务优先级排序、资源分配、SLA监控"
    )

    create_handoff(
        target_worker="xuanhu.router",
        target_worker_name="墨路·成本路由",
        tool_name_override="transfer_to_xuanhu_router",
        tool_description_override="模型成本路由：根据任务复杂度自动选择DeepSeek/百炼/本地模型，优化API成本"
    )

    print(f"[Handoff v8.0] 已注册 {len(HandoffManager._handoffs)} 条路由 — 六司四十一将架构")


if __name__ == "__main__":
    register_all_handoffs()
    from molib.agencies.handoff import HandoffManager
    manifest = HandoffManager.get_manifest()
    print(f"\n注册清单 ({len(manifest)} 条路由):")
    # 按六司分组显示
    domains = {
        "紫灵·情报雷达": ["ziling.scanner", "ziling.spy", "ziling.seo", "ziling.analyst", "ziling.researcher", "ziling.validator", "ziling.invest"],
        "元瑶·知识变现": ["yuanyao.growth", "yuanyao.closer", "yuanyao.tutor", "yuanyao.curriculum", "yuanyao.pm", "yuanyao.community", "yuanyao.order", "yuanyao.abtest"],
        "银月·内容获客": ["yinyue.writer", "yinyue.designer", "yinyue.editor", "yinyue.seowriter", "yinyue.streamer", "yinyue.pr", "yinyue.scheduler"],
        "梅凝·出海收汇": ["meining.translator", "meining.growth", "meining.webmaster", "meining.payment", "meining.compliance", "meining.distribution"],
        "宋玉·B2B企业服务": ["songyu.bd", "songyu.proposal", "songyu.gov", "songyu.events", "songyu.procurement"],
        "玄骨·系统中枢": ["xuanhu.developer", "xuanhu.ops", "xuanhu.security", "xuanhu.autodream", "xuanhu.finance", "xuanhu.legal", "xuanhu.hr", "xuanhu.router"],
    }
    for domain, workers in domains.items():
        print(f"\n  ▸ {domain} ({len(workers)}将):")
        for m in manifest:
            if m['target_worker'] in workers:
                print(f"    {m['tool_name']:<35s} → {m['target_worker_name']:<12s} [{'✅' if m['enabled'] else '❌'}]")
