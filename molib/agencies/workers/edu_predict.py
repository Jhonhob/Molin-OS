"""墨预 · 教育预测 Worker — 用户行为仿真与招生转化预测

子模块归属于 EduAgency，不是独立 Profile。
预测任务用 DeepSeek（结构化 JSON 输出稳定），报告生成可用 Qwen。
"""

from .base import SmartSubsidiaryWorker as _Base, Task, WorkerResult


class EduPredict(_Base):
    worker_id = "edu_predict"
    worker_name = "墨预教育"
    description = "教育用户行为仿真与招生转化预测 (DeepSeek 驱动严格 JSON 决策仿真)"
    oneliner = "画像仿真·漏斗转化·定价敏感度·话术A/B测试·竞品分流"

    # ── 模型路由 ────────────────────────────────────────────────
    DEFAULT_MODEL = "deepseek-v4-pro"       # 画像生成、决策仿真（JSON 严格输出）
    STRUCTURED_MODEL = "deepseek-v4-pro"    # 漏斗计算、结果聚合
    REPORT_MODEL = "qwen3.6-plus"           # 最终报告生成（长文本）

    # ── 配置 ────────────────────────────────────────────────────
    MAX_PERSONAS_PER_RUN = 50              # 单次仿真最多画像数
    DAILY_BUDGET = 10.0                    # 每日预算上限（元）

    @staticmethod
    def get_capabilities() -> list[str]:
        return [
            "画像仿真: 根据用户画像模拟真实决策路径",
            "转化漏斗: 曝光→点击→咨询→付费四级漏斗计算",
            "定价敏感度: 不同价格点下的转化率预测",
            "话术A/B测试: 对比两套文案的预期转化效果",
            "竞品分流: 竞品存在时的转化损失预估",
            "批量画像: 最多50个画像的批量仿真",
        ]

    @staticmethod
    def get_metadata() -> dict:
        return {
            "name": "墨预教育",
            "vp": "运营",
            "parent": "元瑶教育 (EduAgency)",
            "description": "教育预测仿真 (DeepSeek 驱动决策仿真)",
            "model_default": "deepseek-v4-pro",
            "model_report": "qwen3.6-plus",
        }

    # ── 提示词加载 ────────────────────────────────────────────────

    def _load_prompt(self) -> str:
        """加载预测系统提示词"""
        from pathlib import Path
        prompt_path = Path(__file__).parent.parent / "edu_predict" / "prompts" / "prediction_system.py"
        try:
            if prompt_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("prediction_system", prompt_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return getattr(mod, "PREDICTION_SYSTEM_PROMPT", "")
        except Exception:
            pass
        # fallback: 内联默认提示词
        return self._default_prompt()

    def _default_prompt(self) -> str:
        return """你是教育行业用户决策仿真引擎。

你的任务是：根据用户画像，模拟真实家长/学员看到课程信息后的决策过程。

核心规则：
1. 严格按照画像特征做决策，不要「好心」提高转化率
2. 价格敏感型用户：低于预期30%才会考虑
3. 焦虑型家长：被痛点触发，但容易被竞品分流
4. 必须输出严格 JSON，不允许任何额外文字

你不是内容创作者，不是招生顾问。你只做预测仿真。"""

    # ── 任务执行 ──────────────────────────────────────────────────

    async def execute(self, task: Task, context: dict | None = None) -> WorkerResult:
        try:
            action = task.payload.get("action", "simulate")

            if action in ("simulate", "persona_simulation"):
                output = await self._persona_simulation(task.payload)
            elif action in ("funnel", "conversion_funnel"):
                output = await self._conversion_funnel(task.payload)
            elif action in ("ab_test", "ab_testing"):
                output = await self._ab_test(task.payload)
            elif action in ("pricing", "pricing_sensitivity"):
                output = await self._pricing_sensitivity(task.payload)
            elif action in ("competitor_diversion", ""):
                output = await self._competitor_diversion(task.payload)
            elif action in ("batch", "batch_simulation"):
                output = await self._batch_simulation(task.payload)
            elif action in ("report", "generate_report"):
                output = await self._generate_report(task.payload)
            else:
                output = await self._persona_simulation(task.payload)

            return WorkerResult(
                task_id=task.task_id,
                worker_id=self.worker_id,
                status="success",
                output=output,
            )
        except Exception as e:
            return WorkerResult(
                task_id=task.task_id,
                worker_id=self.worker_id,
                status="failed",
                output={},
                error=str(e),
            )

    # ── 核心方法 ──────────────────────────────────────────────────

    async def _persona_simulation(self, payload: dict) -> dict:
        """单画像决策仿真"""
        system = self._load_prompt()
        persona = payload.get("persona", {})
        course_info = payload.get("course", {})
        prompt = f"""
根据以下用户画像和课程信息，模拟该用户的决策过程。

【用户画像】
{persona}

【课程信息】
{course_info}

请以 JSON 格式输出决策结果：
{{
  "decision": "convert" | "hesitate" | "reject",
  "conversion_probability": 0.0-1.0,
  "decision_path": ["步骤1", "步骤2", ...],
  "key_factors": {{
    "price_reaction": "价格感知描述",
    "pain_point_trigger": "是否触达痛点",
    "trust_level": "信任度 0-10"
  }},
  "objection": "主要拒绝原因（如果有）",
  "recommended_action": "建议的转化策略"
}}"""
        result = await self.llm_chat_json(prompt, system=system, model=self.STRUCTURED_MODEL)
        result.setdefault("source", "persona_simulation")
        return result

    async def _conversion_funnel(self, payload: dict) -> dict:
        """转化漏斗计算"""
        system = self._load_prompt()
        personas = payload.get("personas", [])
        course = payload.get("course", {})
        if len(personas) > self.MAX_PERSONAS_PER_RUN:
            personas = personas[:self.MAX_PERSONAS_PER_RUN]

        prompt = f"""
对以下 {len(personas)} 个用户画像，模拟他们在课程销售漏斗中各级的转化情况。
漏斗层级：曝光 → 点击 → 详情浏览 → 咨询 → 付费

【课程】
{course}

【用户画像列表】
{personas}

以 JSON 输出：
{{
  "funnel": {{
    "impressions": N,
    "clicks": N,
    "detail_views": N,
    "consultations": N,
    "purchases": N,
    "overall_conversion_rate": 0.xx
  }},
  "by_persona": [
    {{"persona_id": "xxx", "stage_reached": "purchase", "propensity": 0.xx}}
  ],
  "bottleneck": "最大流失环节",
  "insights": ["发现1", "发现2"]
}}"""
        return await self.llm_chat_json(prompt, system=system, model=self.STRUCTURED_MODEL)

    async def _ab_test(self, payload: dict) -> dict:
        """话术A/B测试"""
        system = self._load_prompt()
        personas = payload.get("personas", [])
        variant_a = payload.get("variant_a", {})
        variant_b = payload.get("variant_b", {})
        if len(personas) > self.MAX_PERSONAS_PER_RUN:
            personas = personas[:self.MAX_PERSONAS_PER_RUN]

        prompt = f"""
对 {len(personas)} 个画像，对比以下两套课程文案/话术的预期转化效果。

【方案 A】{variant_a}
【方案 B】{variant_b}
【画像列表】{personas}

以 JSON 输出：
{{
  "winner": "A" | "B" | "tie",
  "confidence": 0.0-1.0,
  "variant_a": {{"expected_conversion": 0.xx, "strengths": [...], "weaknesses": [...]}},
  "variant_b": {{"expected_conversion": 0.xx, "strengths": [...], "weaknesses": [...]}},
  "statistical_significance": "显著" | "不显著",
  "recommendation": "推荐理由"
}}"""
        return await self.llm_chat_json(prompt, system=system, model=self.STRUCTURED_MODEL)

    async def _pricing_sensitivity(self, payload: dict) -> dict:
        """定价敏感度分析"""
        system = self._load_prompt()
        personas = payload.get("personas", [])
        course = payload.get("course", {})
        price_points = payload.get("price_points", [99, 199, 299, 499, 999])
        if len(personas) > self.MAX_PERSONAS_PER_RUN:
            personas = personas[:self.MAX_PERSONAS_PER_RUN]

        prompt = f"""
对 {len(personas)} 个画像和 {len(price_points)} 个价格点，模拟各价格下的转化率。

【课程】{course}
【价格点（元）】{price_points}
【画像列表】{personas}

以 JSON 输出：
{{
  "price_sensitivity_curve": [
    {{"price": 99, "conversion_rate": 0.xx, "count": N}},
    ...
  ],
  "optimal_price": 299,
  "revenue_forecast": {{"99": N, "199": N, ...}},
  "price_elasticity": "高" | "中" | "低",
  "insights": ["发现1"]
}}"""
        return await self.llm_chat_json(prompt, system=system, model=self.STRUCTURED_MODEL)

    async def _competitor_diversion(self, payload: dict) -> dict:
        """竞品分流分析"""
        system = self._load_prompt()
        personas = payload.get("personas", [])
        course = payload.get("course", {})
        competitors = payload.get("competitors", [])
        if len(personas) > self.MAX_PERSONAS_PER_RUN:
            personas = personas[:self.MAX_PERSONAS_PER_RUN]

        prompt = f"""
对 {len(personas)} 个画像，模拟在 {len(competitors)} 个竞品存在时的转化损失。

【我方课程】{course}
【竞品列表】{competitors}
【画像列表】{personas}

以 JSON 输出：
{{
  "base_conversion": 0.xx,
  "with_competitors": 0.xx,
  "diversion_rate": 0.xx,
  "competitor_attribution": {{
    "竞品A": 0.xx,
    "竞品B": 0.xx
  }},
  "vulnerable_segments": ["容易流失的画像特征"],
  "defense_strategies": ["防守策略1", "防守策略2"]
}}"""
        return await self.llm_chat_json(prompt, system=system, model=self.STRUCTURED_MODEL)

    async def _batch_simulation(self, payload: dict) -> dict:
        """批量画像仿真（逐画像串行，控制预算）"""
        personas = payload.get("personas", [])
        course = payload.get("course", {})
        if len(personas) > self.MAX_PERSONAS_PER_RUN:
            personas = personas[:self.MAX_PERSONAS_PER_RUN]

        results = []
        for i, persona in enumerate(personas):
            output = await self._persona_simulation({
                "persona": persona,
                "course": course,
            })
            results.append(output)

        converted = sum(1 for r in results if r.get("decision") == "convert")
        total = len(results)

        return {
            "action": "batch_simulation",
            "total_personas": total,
            "converted": converted,
            "hesitated": sum(1 for r in results if r.get("decision") == "hesitate"),
            "rejected": sum(1 for r in results if r.get("decision") == "reject"),
            "conversion_rate": converted / total if total > 0 else 0,
            "individual_results": results,
        }

    async def _generate_report(self, payload: dict) -> dict:
        """生成仿真报告（用 Qwen 做长文本报告）"""
        system = """你是教育预测分析师。根据仿真数据撰写结构化的招生预测报告。
报告需包含：总览、关键发现、人群洞察、行动建议。用中文输出。"""
        data = payload.get("data", {})
        prompt = f"根据以下仿真数据，撰写一份招生转化预测报告：\n{data}"
        result = await self.llm_chat(prompt, system=system, model=self.REPORT_MODEL)
        return {"action": "generate_report", "report": result}
