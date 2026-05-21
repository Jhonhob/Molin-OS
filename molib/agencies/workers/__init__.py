"""墨麟OS v2.0 — 五域一枢 Worker注册表 (2026-05-21)"""

from .base import SubsidiaryWorker, WorkerRegistry, Task, WorkerResult

# ─── 墨育 · 教育增长域 ───
from .edu_acquisition_worker import EduAcquisitionWorker
from .edu_conversion_worker import EduConversionWorker
from .edu_retention_worker import EduRetentionWorker
from .edu_prediction_worker import EduPredictionWorker
from .edu_content_worker import EduContentWorker

# ─── 墨研 · AI情报域 ───
from .github_radar_worker import GithubRadarWorker
from .intel_brief_worker import IntelBriefWorker
from .ai_review_worker import AiReviewWorker
from .knowledge_base_worker import KnowledgeBaseWorker

# ─── 墨媒 · IP变现域 ───
from .content_matrix_worker import ContentMatrixWorker
from .knowledge_product_worker import KnowledgeProductWorker
from .ip_commerce_worker import IpCommerceWorker
from .live_ops_worker import LiveOpsWorker

# ─── 墨海 · 出海域 ───
from .taiwan_ops_worker import TaiwanOpsWorker
from .localization_worker import LocalizationWorker
from .sea_market_worker import SeaMarketWorker

# ─── 墨创 · 一人公司域 ───
from .solo_finance_worker import SoloFinanceWorker
from .solo_legal_worker import SoloLegalWorker
from .solo_data_worker import SoloDataWorker
from .solo_strategy_worker import SoloStrategyWorker

# ─── 墨枢 · 基础设施 ───
from .dev_infra_worker import DevInfraWorker
from .tech_security_worker import TechSecurityWorker
from .auto_dream import AutoDream
from .scrapling_worker import ScraplingWorker
from .cocoindex_sync import CocoIndexSync


def register_all():
    """注册全部25个Worker — 五域一枢架构"""
    # 墨育 (5)
    WorkerRegistry.register(EduAcquisitionWorker)
    WorkerRegistry.register(EduConversionWorker)
    WorkerRegistry.register(EduRetentionWorker)
    WorkerRegistry.register(EduPredictionWorker)
    WorkerRegistry.register(EduContentWorker)

    # 墨研 (4)
    WorkerRegistry.register(GithubRadarWorker)
    WorkerRegistry.register(IntelBriefWorker)
    WorkerRegistry.register(AiReviewWorker)
    WorkerRegistry.register(KnowledgeBaseWorker)

    # 墨媒 (4)
    WorkerRegistry.register(ContentMatrixWorker)
    WorkerRegistry.register(KnowledgeProductWorker)
    WorkerRegistry.register(IpCommerceWorker)
    WorkerRegistry.register(LiveOpsWorker)

    # 墨海 (3)
    WorkerRegistry.register(TaiwanOpsWorker)
    WorkerRegistry.register(LocalizationWorker)
    WorkerRegistry.register(SeaMarketWorker)

    # 墨创 (5 incl cocoindex)
    WorkerRegistry.register(SoloFinanceWorker)
    WorkerRegistry.register(SoloLegalWorker)
    WorkerRegistry.register(SoloDataWorker)
    WorkerRegistry.register(SoloStrategyWorker)
    WorkerRegistry.register(CocoIndexSync)

    # 墨枢 (4)
    WorkerRegistry.register(DevInfraWorker)
    WorkerRegistry.register(TechSecurityWorker)
    WorkerRegistry.register(AutoDream)
    WorkerRegistry.register(ScraplingWorker)


def get_worker(name: str) -> SubsidiaryWorker | None:
    cls = WorkerRegistry.get(name)
    if cls:
        return cls()
    for wid, wcls in WorkerRegistry._workers.items():
        if name in wid or name in wcls.worker_name:
            return wcls()
    return None


def list_workers() -> list[dict]:
    return [
        {"id": wid, "name": wcls.worker_name, "desc": wcls.description,
         "line": getattr(wcls, "oneliner", "")}
        for wid, wcls in WorkerRegistry._workers.items()
    ]
