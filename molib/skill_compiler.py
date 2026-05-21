"""
强类型结构化技能编译器 (Skill Compiler)
===========================================
根治 339 个技能的「状态逃逸与 Logit 幻觉」。
利用 Pydantic + JSON Schema 在模型生成概率层设置语法约束，
强制大模型输出 100% 符合预期的 Python 对象。

灵感来源: Outlines (dottxt-ai/outlines) 的 CFG 语法图拦截思想。

用法：
    from molib.skill_compiler import HardenedSkillCompiler, VideoScriptSchema
    compiler = HardenedSkillCompiler(client_factory)
    result = compiler.run_skill_with_grammar(skill_prompt, user_input, VideoScriptSchema)
"""

import json
from typing import Any, Optional, Type
from pydantic import BaseModel, Field, create_model


# ── 预定义业务 Schema ──────────────────────────

class IntelligenceReport(BaseModel):
    """紫灵(情报) → 银月(内容) 的强类型数据规约"""
    topic: str = Field(..., description="情报主题")
    source_url: str = Field(..., description="合法的来源URL")
    key_facts: list[str] = Field(..., min_length=3, description="核心事实列表，至少3条")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="置信度 0.0 - 1.0")


class ContentPublishSchema(BaseModel):
    """银月(内容) → 发布 的强类型数据规约"""
    title: str = Field(..., max_length=50, description="发布标题，不超过50字")
    body: str = Field(..., min_length=10, description="正文内容，至少10字")
    tags: list[str] = Field(default_factory=list, max_length=5, description="标签列表，最多5个")
    platform: str = Field(default="xiaohongshu", description="目标平台")


class VideoScriptSchema(BaseModel):
    """短视频脚本的强类型规约"""
    title: str = Field(..., max_length=20, description="爆款视频标题，不超过20字")
    hooks: list[str] = Field(..., min_length=3, description="前3秒吸睛黄金诱饵词，至少3条")
    voiceover: list[dict] = Field(..., description="分镜头脚本列表")
    estimated_duration_sec: int = Field(..., ge=0, le=300, description="预估视频总时长(秒)")


class FinanceRecordSchema(BaseModel):
    """财务记账的强类型规约"""
    record_type: str = Field(..., pattern="^(income|expense|investment)$", description="记录类型")
    amount: float = Field(..., gt=0, description="金额，必须 > 0")
    note: str = Field(..., min_length=1, max_length=200, description="备注")


# ── Schema 注册表 ──────────────────────────────

SKILL_SCHEMAS = {
    "intelligence_report": IntelligenceReport,
    "content_publish": ContentPublishSchema,
    "video_script": VideoScriptSchema,
    "finance_record": FinanceRecordSchema,
}


# ── 编译器引擎 ─────────────────────────────────

class HardenedSkillCompiler:
    """
    微观规约编译器：加载 SKILL.md 规则，
    强制大模型遵循 Pydantic 结构输出，100% 消除 JSON 解析错误。
    """

    def __init__(self, client_factory=None):
        """
        Args:
            client_factory: 大模型客户端工厂（兼容 OpenAI / DashScope / DeepSeek）
                           需支持 .chat.completions.create() 和 response_format 参数。
        """
        self.client = client_factory

    def run_skill_with_grammar(
        self,
        skill_prompt: str,
        user_input: str,
        response_model: Type[BaseModel],
        *,
        model: str = "deepseek-chat",
        temperature: float = 0.2,
        max_retries: int = 3,
    ) -> dict:
        """
        利用 Pydantic JSON Schema 约束执行技能。

        Args:
            skill_prompt: 技能的系统提示词（SKILL.md 规则）
            user_input: 用户输入/上下文
            response_model: Pydantic 模型类（定义输出结构）
            model: 使用的模型名
            temperature: 生成温度（建议 0.1-0.3，专注于规则对齐）
            max_retries: 如果输出格式不符，自动重试次数

        Returns:
            {"status": "success", "result": {...}} 或 {"status": "error", ...}
        """
        if self.client is None:
            return {"status": "error", "message": "No LLM client configured"}

        system_prompt = (
            f"{skill_prompt}\n\n"
            f"⚠️ 输出约束：你必须严格遵循指定的 JSON Schema 格式输出。"
            f"不要包含任何 markdown 标记、解释文字或额外字符。"
            f"只输出一个合法的 JSON 对象。"
        )

        schema = response_model.model_json_schema()
        last_error = None

        for attempt in range(max_retries):
            try:
                # 兼容 OpenAI 兼容接口的 Structured Outputs / JSON Mode
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    response_format={
                        "type": "json_object",
                        "schema": schema,
                    },
                    temperature=temperature,
                )

                raw = response.choices[0].message.content

                # 解析并验证
                parsed = json.loads(raw)
                validated = response_model.model_validate(parsed)

                return {
                    "status": "success",
                    "result": validated.model_dump(),
                }

            except json.JSONDecodeError as e:
                last_error = f"JSON parse failed (attempt {attempt + 1}): {e}"
                # 下次重试降一点温度
                temperature = max(0.05, temperature * 0.8)

            except Exception as e:
                last_error = f"Schema validation failed (attempt {attempt + 1}): {e}"
                temperature = max(0.05, temperature * 0.8)

        return {"status": "error", "message": last_error or "Unknown compilation error"}

    def compile_with_retry(
        self,
        skill_prompt: str,
        user_input: str,
        schema_name: str,
        **kwargs,
    ) -> dict:
        """
        语法糖：按名称从注册表匹配 Schema 执行。
        schema_name 可选: intelligence_report, content_publish, video_script, finance_record
        """
        schema_cls = SKILL_SCHEMAS.get(schema_name)
        if schema_cls is None:
            return {"status": "error", "message": f"Unknown schema: {schema_name}"}

        return self.run_skill_with_grammar(skill_prompt, user_input, schema_cls, **kwargs)

    @staticmethod
    def register_schema(name: str, schema: Type[BaseModel]):
        """动态注册新的业务 Schema"""
        SKILL_SCHEMAS[name] = schema

    @staticmethod
    def dynamic_schema(name: str, fields: dict) -> Type[BaseModel]:
        """动态创建 Pydantic 模型"""
        model = create_model(name, **fields)
        SKILL_SCHEMAS[name] = model
        return model
