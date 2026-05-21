"""
Instructor 风格强类型校验器 (Validators)
===========================================
借鉴 jxnl/instructor 的「Pydantic + 自动修正」思想。
定义严格的业务数据规约，强制 LLM 返回 100% 符合结构的 Python 实体对象。
输出格式不对时自动将报错丢回 LLM 让其自我修正。

用法：
    from molib.validators import SecureInstructor, IntelligenceReport
    instructor = SecureInstructor(client)
    report = instructor.extract_intelligence(raw_llm_text)
    print(report.confidence_score)  # 直接点出属性
"""

import json
from typing import Any, Optional, Type
from pydantic import BaseModel, ValidationError

# 复用 skill_compiler 的 Schema
from molib.skill_compiler import (
    IntelligenceReport,
    ContentPublishSchema,
    VideoScriptSchema,
    FinanceRecordSchema,
)


class SecureInstructor:
    """
    强制类型输出校验器 — 大模型的「语法警察」。
    """

    def __init__(self, client: Any = None):
        """
        Args:
            client: LLM 客户端（兼容 OpenAI 接口）
        """
        self.client = client

    def extract_structured(
        self,
        raw_llm_text: str,
        response_model: Type[BaseModel],
        *,
        auto_fix: bool = True,
        max_fix_attempts: int = 3,
    ) -> Optional[BaseModel]:
        """
        从 LLM 原始输出中提取结构化实体。

        Args:
            raw_llm_text: LLM 原始输出文本
            response_model: 目标 Pydantic 模型
            auto_fix: 是否在格式错误时让 LLM 自我修正
            max_fix_attempts: 最大修正次数

        Returns:
            验证通过的 Pydantic 实体对象，或 None
        """
        # 尝试 1: 直接 JSON 解析
        last_error = ""
        try:
            parsed = self._extract_json(raw_llm_text)
            return response_model.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)
            if not auto_fix or self.client is None:
                print(f"❌ 结构化提取失败: {last_error}")
                return None

        # 尝试 2-N: 让 LLM 自我修正
        for attempt in range(max_fix_attempts):
            try:
                fixed_text = self._ask_llm_to_fix(raw_llm_text, response_model, last_error)
                parsed = json.loads(fixed_text)
                return response_model.model_validate(parsed)
            except (json.JSONDecodeError, ValidationError) as e2:
                print(f"   🔄 自我修正尝试 {attempt + 1}/{max_fix_attempts}: {e2}")
                continue

        print(f"❌ 经过 {max_fix_attempts} 次自我修正后仍然失败")
        return None

    def _extract_json(self, text: str) -> dict:
        """从 LLM 输出中提取 JSON（处理常见的格式问题）"""
        text = text.strip()

        # 移除 markdown 代码块
        if text.startswith("```"):
            lines = text.split("\n")
            # 去掉首行 ```json 和末行 ```
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        # 尝试找到第一个 { ... }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]

        return json.loads(text)

    def _ask_llm_to_fix(self, bad_output: str, model: Type[BaseModel], error_msg: str) -> str:
        """让 LLM 自我修正输出"""
        schema = model.model_json_schema()
        schema_str = json.dumps(schema, ensure_ascii=False, indent=2)

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是输出格式修正引擎。"
                        "将用户提供的文本转换为其内容相符的合法 JSON。"
                        "只输出 JSON，不要 markdown 标记。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"以下是被拒绝的输出：\n```\n{bad_output[:2000]}\n```\n\n"
                        f"错误原因：{error_msg}\n\n"
                        f"要求的 Schema：\n```json\n{schema_str}\n```\n\n"
                        f"请输出修复后的合法 JSON："
                    ),
                },
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content

    # ── 专项提取器 ──────────────────────────

    def extract_intelligence(self, raw_text: str) -> Optional[IntelligenceReport]:
        """提取情报研报"""
        return self.extract_structured(raw_text, IntelligenceReport)

    def extract_content_publish(self, raw_text: str) -> Optional[ContentPublishSchema]:
        """提取发布内容"""
        return self.extract_structured(raw_text, ContentPublishSchema)

    def extract_video_script(self, raw_text: str) -> Optional[VideoScriptSchema]:
        """提取视频脚本"""
        return self.extract_structured(raw_text, VideoScriptSchema)

    def extract_finance_record(self, raw_text: str) -> Optional[FinanceRecordSchema]:
        """提取财务记录"""
        return self.extract_structured(raw_text, FinanceRecordSchema)

    # ── 批量提取 ────────────────────────────

    def extract_batch(
        self,
        raw_texts: list[str],
        response_model: Type[BaseModel],
        **kwargs,
    ) -> list[Optional[BaseModel]]:
        """批量结构化提取"""
        return [self.extract_structured(t, response_model, **kwargs) for t in raw_texts]
