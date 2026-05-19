#!/opt/homebrew/bin/python3.11
"""
墨麟 · BKT（贝叶斯知识追踪）引擎 v1.1
追踪180个知识点在学员侧的掌握概率
基于知识图谱 + 答题结果实时更新

吸收来源:
  - RetainCraft (kaixiad/RetainCraft): 烧脑检测 + 五方法学习协议 (Donoghue & Hattie 2021)
  - Student Knowledge Modeling (kirana-23): Q矩阵优化思路
"""
import json
import math
import sys
from datetime import datetime
from copy import deepcopy

EDU_HOME = "/Users/laomo/.hermes/profiles/edu"
BKT_CONFIG = f"{EDU_HOME}/curriculum/bkt_model_config.json"
STUDENTS_DIR = f"{EDU_HOME}/memories/students"


class BKTTracker:
    """BKT贝叶斯知识追踪器"""
    
    def __init__(self, config_path=BKT_CONFIG):
        with open(config_path) as f:
            self.config = json.load(f)
        self.params = self.config["bkt_parameters"]
        self.kps = self.config["knowledge_points"]
        # 知识点索引
        self.kp_index = {kp["id"]: kp for kp in self.kps}
    
    def get_prior_p(self, kp_id: str) -> float:
        """获取某个知识点的初始掌握概率"""
        return self.kp_index.get(kp_id, {}).get("prior_p", self.params["prior_p"])
    
    def update(self, kp_id: str, correct: bool, current_p: float = None) -> dict:
        """
        根据答题结果更新某个知识点的掌握概率
        
        输入:
            kp_id: 知识点ID (如 "L1_分类思维")
            correct: 是否答对
            current_p: 当前掌握概率（None=从先验开始）
        
        返回:
            {"kp_id": str, "new_p": float, "delta": float}
        """
        if current_p is None:
            current_p = self.get_prior_p(kp_id)
        
        p_learn = self.params["learn_rate"]
        p_slip = self.params["slip_rate"]
        p_guess = self.params["guess_rate"]
        
        # BKT核心公式
        # 1. 先验：当前掌握概率 + 学习一次后新掌握的概率
        p_prior = current_p + (1 - current_p) * p_learn
        
        # 2. 似然：看到当前答题结果的概率
        if correct:
            p_evidence = p_prior * (1 - p_slip) + (1 - p_prior) * p_guess
        else:
            p_evidence = p_prior * p_slip + (1 - p_prior) * (1 - p_guess)
        
        # 3. 后验：贝叶斯更新
        if correct:
            p_posterior = p_prior * (1 - p_slip) / p_evidence
        else:
            p_posterior = p_prior * p_slip / p_evidence
        
        return {
            "kp_id": kp_id,
            "prior_p": round(current_p, 4),
            "new_p": round(p_posterior, 4),
            "delta": round(p_posterior - current_p, 4),
        }
    
    def batch_update(self, answers: list, current_states: dict = None) -> dict:
        """
        批量更新多个知识点
        
        输入:
            answers: [{"kp_id": "L1_分类思维", "correct": True}, ...]
            current_states: {kp_id: 当前掌握概率}
        
        返回:
            {kp_id: {"new_p": ..., "delta": ...}}
        """
        if current_states is None:
            current_states = {}
        
        results = {}
        for ans in answers:
            kp_id = ans["kp_id"]
            current_p = current_states.get(kp_id)
            result = self.update(kp_id, ans["correct"], current_p)
            results[kp_id] = result
        return results
    
    def get_weak_points(self, states: dict, threshold: float = 0.6) -> list:
        """
        从当前所有知识点状态中，找出薄弱点（掌握概率低于阈值）
        按薄弱程度排序
        """
        weak = [(kp_id, p) for kp_id, p in states.items() if p < threshold]
        weak.sort(key=lambda x: x[1])  # 从最弱开始
        return weak
    
    def get_signature(self, states: dict) -> dict:
        """
        生成学员的思维能力概览（20种方法的平均掌握度）
        """
        # 按方法归类
        method_scores = {tm["name"]: [] for tm in self.config["thinking_methods"]}
        
        for kp_id, p in states.items():
            # kp_id格式: "L1_分类思维"
            parts = kp_id.split("_", 1)
            if len(parts) == 2:
                method = parts[1]
                if method in method_scores:
                    method_scores[method].append(p)
        
        # 取平均
        method_avg = {
            m: round(sum(scores)/len(scores), 3) if scores else 0
            for m, scores in method_scores.items()
        }
        
        # 按类别分组
        categories = {}
        for tm in self.config["thinking_methods"]:
            cat = tm["category"]
            if cat not in categories:
                categories[cat] = {}
            categories[cat][tm["name"]] = method_avg.get(tm["name"], 0)
        
        return {
            "method_averages": method_avg,
            "categories": categories,
            "overall": round(sum(method_avg.values()) / len(method_avg), 3) if method_avg else 0,
        }


class StruggleDetector:
    """烧脑检测器 — 追踪连续错误，3次触发降级信号
    吸收来源: RetainCraft (kaixiad/RetainCraft) 证据驱动自适应协议
    
    原理: 当学员在同一知识点连续3次错误时，认定为"烧脑"状态，
    BKT引擎降级到低一阶知识点，Coach Agent切换为情感鼓励+苏格拉底追问模式
    """
    
    def __init__(self, consecutive_threshold: int = 3):
        self.threshold = consecutive_threshold
        # 每个知识点的连续错误计数
        self._consecutive_errors: dict[str, int] = {}
        # 每个知识点的总尝试次数
        self._total_attempts: dict[str, int] = {}
        # 每个知识点的总错误次数
        self._total_errors: dict[str, int] = {}
        # 烧脑历史记录
        self._struggle_history: dict[str, list[dict]] = {}
    
    def record_answer(self, kp_id: str, correct: bool, timestamp: str = None) -> dict:
        """记录一次答题结果，更新烧脑状态
        
        返回:
            {
                "kp_id": str,
                "consecutive_errors": int,
                "struggle_level": 0|1|2|3,
                "total_accuracy": float
            }
        """
        if kp_id not in self._total_attempts:
            self._total_attempts[kp_id] = 0
            self._total_errors[kp_id] = 0
            self._consecutive_errors[kp_id] = 0
        
        self._total_attempts[kp_id] += 1
        
        if correct:
            self._consecutive_errors[kp_id] = 0
        else:
            self._total_errors[kp_id] += 1
            self._consecutive_errors[kp_id] += 1
        
        struggle_level = self._get_struggle_level(kp_id)
        
        # 触发烧脑事件时记录
        if struggle_level >= 2 and correct is False:
            if kp_id not in self._struggle_history:
                self._struggle_history[kp_id] = []
            self._struggle_history[kp_id].append({
                "timestamp": timestamp or datetime.now().isoformat(),
                "consecutive_errors": self._consecutive_errors[kp_id],
                "struggle_level": struggle_level,
            })
        
        return {
            "kp_id": kp_id,
            "consecutive_errors": self._consecutive_errors[kp_id],
            "struggle_level": struggle_level,
            "total_attempts": self._total_attempts[kp_id],
            "total_errors": self._total_errors[kp_id],
            "total_accuracy": round(
                (self._total_attempts[kp_id] - self._total_errors[kp_id]) / self._total_attempts[kp_id],
                3
            ) if self._total_attempts[kp_id] > 0 else 0,
        }
    
    def _get_struggle_level(self, kp_id: str) -> int:
        """烧脑级别:
        0 = 正常
        1 = 轻微 (连续2次错误)
        2 = 中度 (连续3次错误 = 触发阈值)
        3 = 严重 (连续5+次错误)
        """
        ce = self._consecutive_errors.get(kp_id, 0)
        if ce >= 5:
            return 3
        if ce >= self.threshold:
            return 2
        if ce >= 2:
            return 1
        return 0
    
    def get_struggle_status(self, kp_id: str) -> dict:
        """获取某个知识点的完整烧脑状态"""
        return {
            "kp_id": kp_id,
            "consecutive_errors": self._consecutive_errors.get(kp_id, 0),
            "struggle_level": self._get_struggle_level(kp_id),
            "is_struggling": self._get_struggle_level(kp_id) >= 2,
            "total_attempts": self._total_attempts.get(kp_id, 0),
            "total_accuracy": round(
                (self._total_attempts.get(kp_id, 0) - self._total_errors.get(kp_id, 0))
                / self._total_attempts.get(kp_id, 1),
                3
            ) if self._total_attempts.get(kp_id, 0) > 0 else 0,
        }
    
    def get_all_struggling(self) -> list[dict]:
        """获取所有正在烧脑的知识点"""
        struggling = []
        for kp_id in self._consecutive_errors:
            status = self.get_struggle_status(kp_id)
            if status["is_struggling"]:
                struggling.append(status)
        struggling.sort(key=lambda x: x["struggle_level"], reverse=True)
        return struggling
    
    def get_struggle_history(self, kp_id: str = None) -> dict:
        """获取烧脑历史（按知识点或全部）"""
        if kp_id:
            return {kp_id: self._struggle_history.get(kp_id, [])}
        return dict(self._struggle_history)


class InterventionAdvisor:
    """干预建议器 — 根据BKT状态+烧脑状态生成干预策略
    
    五方法协议（Donoghue & Hattie 2021 元分析），吸收自 RetainCraft:
    - 分布式练习 (d=0.85) -> SRS复习排期
    - 练习测试 (d=0.74) -> 错题自动入待复习池
    - 自我解释 (d=0.54) -> 费曼学习法/讲题
    - 交错练习 (d=0.47) -> 混合知识点出题
    - 精细探究 (d=0.56) -> 苏格拉底追问
    """
    
    METHODS = {
        "distributed_practice": {
            "name": "分布式练习",
            "effect_size": 0.85,
            "desc": "间隔重复推送，SRS最优排期",
            "trigger": "any",
        },
        "practice_testing": {
            "name": "练习测试",
            "effect_size": 0.74,
            "desc": "同知识点换题型再测，确认掌握或slip",
            "trigger": "bkt_high_struggle",
        },
        "self_explanation": {
            "name": "自我解释",
            "effect_size": 0.54,
            "desc": "让学员讲出解题思路，费曼学习法",
            "trigger": "bkt_mid_struggle",
        },
        "interleaved_practice": {
            "name": "交错练习",
            "effect_size": 0.47,
            "desc": "混入已掌握的知识点，打破块状记忆",
            "trigger": "bkt_high_no_struggle",
        },
        "elaborative_interrogation": {
            "name": "精细探究",
            "effect_size": 0.56,
            "desc": "为什么式追问，引导深度思考",
            "trigger": "bkt_mid_struggle",
        },
    }
    
    def advise(self, kp_id: str, bkt_p: float, struggle_status: dict) -> dict:
        """根据当前状态生成干预建议
        
        输入:
            kp_id: 知识点ID
            bkt_p: BKT掌握概率 (0-1)
            struggle_status: StruggleDetector.get_struggle_status() 返回
        
        返回:
            {
                "kp_id": str,
                "bkt_p": float,
                "struggle_level": int,
                "intervention_level": str,
                "suggested_methods": [...],
                "action": str,
            }
        """
        struggle_level = struggle_status.get("struggle_level", 0)
        is_struggling = struggle_status.get("is_struggling", False)
        
        # 干预分级
        if is_struggling and bkt_p < 0.4:
            intervention_level = "heavy"
            suggested = ["self_explanation"]
            action = (
                f"学员在知识点【{kp_id}】连续错误，当前BKT掌握度{bkt_p:.2f}。"
                "建议执行降级干预：\n"
                "1. 情感鼓励：这个知识点确实有难度，我们换一种方式试试\n"
                "2. 降级到低一阶知识点重新巩固前置基础\n"
                "3. 让学员用自我解释法讲出当前理解\n"
                "4. 如果连续2次降级后仍卡壳，建议休息后再试"
            )
        
        elif is_struggling and bkt_p < 0.6:
            intervention_level = "medium"
            suggested = ["self_explanation", "elaborative_interrogation"]
            action = (
                f"学员在知识点【{kp_id}】卡壳，掌握度{bkt_p:.2f}处于临界区。"
                "建议执行分步引导：\n"
                "1. 精细探究：你能说说为什么选这个答案吗？\n"
                "2. 自我解释：如果换一种思路，你觉得会怎样？\n"
                "3. 给一半的提示，让学员自己推导后半段\n"
                "4. 答对后立即正反馈强化"
            )
        
        elif is_struggling:
            intervention_level = "light"
            suggested = ["practice_testing"]
            action = (
                f"学员在知识点【{kp_id}】答错但BKT掌握度{bkt_p:.2f}较高，可能是一时失误。"
                "建议换题型再测：\n"
                "1. 同知识点换题干重出1题\n"
                "2. 答对则跳过，答错则升级为中度干预\n"
                "3. 不要直接告诉正确答案"
            )
        
        else:
            intervention_level = "normal"
            suggested = []
            action = "学员状态正常，无需干预。继续按当前进度推进。"
        
        return {
            "kp_id": kp_id,
            "bkt_p": round(bkt_p, 4),
            "struggle_level": struggle_level,
            "intervention_level": intervention_level,
            "suggested_methods": suggested,
            "action": action,
        }
    
    def advise_schedule(self, weak_points: list, struggling_kps: list) -> list:
        """为待复习知识点排期（五方法中的分布式练习）
        
        输入:
            weak_points: [(kp_id, bkt_p), ...] from BKTTracker.get_weak_points()
            struggling_kps: [struggle_status, ...] from StruggleDetector.get_all_struggling()
        
        返回:
            [{"kp_id": str, "priority": int, "method": str, "reason": str}, ...]
        """
        struggling_ids = {s["kp_id"] for s in struggling_kps}
        
        schedule = []
        for kp_id, bkt_p in weak_points:
            if kp_id in struggling_ids:
                schedule.append({
                    "kp_id": kp_id,
                    "priority": 1,
                    "method": "自我解释 / 精细探究",
                    "reason": f"烧脑中+BKT={bkt_p:.2f}，需立即干预",
                })
            elif bkt_p < 0.4:
                schedule.append({
                    "kp_id": kp_id,
                    "priority": 2,
                    "method": "分布式练习（SRS排期）",
                    "reason": f"低掌握度BKT={bkt_p:.2f}，需间隔重复",
                })
            elif bkt_p < 0.7:
                schedule.append({
                    "kp_id": kp_id,
                    "priority": 3,
                    "method": "交错练习",
                    "reason": f"中等掌握BKT={bkt_p:.2f}，混入已掌握知识点巩固",
                })
        
        schedule.sort(key=lambda x: x["priority"])
        return schedule


# ============================================================
# 快速测试
# ============================================================
if __name__ == "__main__":
    tracker = BKTTracker()
    detector = StruggleDetector()
    advisor = InterventionAdvisor()
    
    # 原有BKT测试
    result = tracker.update("L1_分类思维", correct=True)
    print(f"BKT测试1 - 正确回答: {result['prior_p']} -> {result['new_p']} (delta {result['delta']})")
    
    result2 = tracker.update("L1_分类思维", correct=False)
    print(f"BKT测试2 - 错误回答: {result2['prior_p']} -> {result2['new_p']} (delta {result2['delta']})")
    
    # 烧脑检测测试：连续5次错误
    p = None
    print(f"\n--- 烧脑检测测试 ---")
    for i in range(5):
        r = tracker.update("L5_模型化思维", correct=False, current_p=p)
        p = r["new_p"]
        sr = detector.record_answer("L5_模型化思维", correct=False)
        print(f"  第{i+1}次错误 BKT={p:.4f} 连续错误={sr['consecutive_errors']} 级别={sr['struggle_level']}")
        
        if i >= 2:
            advice = advisor.advise("L5_模型化思维", p, detector.get_struggle_status("L5_模型化思维"))
            print(f"  干预建议: [{advice['intervention_level']}] {advice['action'][:60]}...")
    
    # 正常状态测试
    print(f"\n--- 正常状态测试 ---")
    p2 = None
    for i in range(5):
        r = tracker.update("L1_有序思维", correct=True, current_p=p2)
        p2 = r["new_p"]
        detector.record_answer("L1_有序思维", correct=True)
    print(f"连续5次正确 BKT={p2:.4f}")
    advice_normal = advisor.advise("L1_有序思维", p2, detector.get_struggle_status("L1_有序思维"))
    print(f"干预建议: [{advice_normal['intervention_level']}] {advice_normal['action'][:60]}")
    
    # 排期测试
    print(f"\n--- 排期测试 ---")
    weak = tracker.get_weak_points({"L5_模型化思维": p, "L1_分类思维": 0.3, "L3_对应思维": 0.55})
    struggling = detector.get_all_struggling()
    schedule = advisor.advise_schedule(weak, struggling)
    for item in schedule:
        print(f"  P{item['priority']} {item['kp_id']} -> {item['method']}: {item['reason'][:40]}")
    
    print(f"\n{'='*50}")
    print(f"吸收来源: RetainCraft(烧脑检测+五方法协议) | Student Knowledge Modeling(Q矩阵)")
    print(f"{'='*50}")
