#!/opt/homebrew/bin/python3.11
"""
墨麟 · IRT自适应出题引擎 v1.0
基于项目反应理论(Item Response Theory) 2PL/3PL模型
适用于逻辑思维课程章节末尾的动态难度评估

吸收来源: lextures (StudyDrift/lextures, 57★) — IRT 2PL/3PL实时自适应
设计思路: 
  - IRT负责"测"：实时估计学员能力值(theta)，选择最优难度题目
  - BKT负责"学"：追踪知识点掌握概率，驱动干预策略
  - 两者联动：IRT输出能力估计 → BKT更新掌握概率
"""
import json
import math
import sys
from datetime import datetime
from typing import Optional

EDU_HOME = "/Users/laomo/.hermes/profiles/edu"
IRT_CONFIG = f"{EDU_HOME}/curriculum/irt_model_config.json"


# ================================================================
# 核心IRT模型
# ================================================================

def irt_2pl(theta: float, a: float, b: float) -> float:
    """IRT 2PL模型: P(正确|theta) = 1 / (1 + exp(-a(theta-b)))
    
    theta: 学员能力值 (-3 ~ 3)
    a: 题目区分度 (0.5 ~ 2.5, 越高越能区分高低能力学员)
    b: 题目难度 (-3 ~ 3, 越高越难)
    """
    return 1.0 / (1.0 + math.exp(-a * (theta - b)))


def irt_3pl(theta: float, a: float, b: float, c: float) -> float:
    """IRT 3PL模型: 增加了猜测参数c
    
    c: 猜测参数 (0 ~ 0.5, 纯蒙对的概率, 选择题常用0.25)
    """
    return c + (1.0 - c) / (1.0 + math.exp(-a * (theta - b)))


def item_info(theta: float, a: float, b: float, c: float = 0.0) -> float:
    """题目信息函数: 衡量一道题在某个能力值处的测量精度
    
    信息量越高 → 这道题对这个能力值的学员最有区分度
    自适应选题时选信息量最大的题
    """
    p = irt_3pl(theta, a, b, c) if c > 0 else irt_2pl(theta, a, b)
    q = 1.0 - p
    if p * q < 1e-10:
        return 0.0
    if c > 0:
        # 3PL信息函数
        info = (a * a) * (q / p) * ((p - c) / (1 - c)) ** 2
    else:
        # 2PL信息函数
        info = (a * a) * p * q
    return info


def expected_score(theta: float, items: list[dict]) -> float:
    """期望得分: 给定能力值theta，在一组题目上的期望正确数"""
    expected = 0.0
    for item in items:
        if item.get("model", "2pl") == "3pl":
            expected += irt_3pl(theta, item["a"], item["b"], item.get("c", 0.0))
        else:
            expected += irt_2pl(theta, item["a"], item["b"])
    return expected


# ================================================================
# 能力估计
# ================================================================

def estimate_theta_mle(responses: list[dict], 
                       items: list[dict],
                       guess_c: float = 0.0) -> dict:
    """最大似然估计(MLE)学员能力值theta
    
    输入:
        responses: [{"item_id": str, "correct": bool}, ...]
        items: [{"id": str, "a": float, "b": float, "c": float}, ...]
    
    返回:
        {"theta": float, "se": float, "responses_count": int}
    """
    # 建立item索引
    item_map = {item["id"]: item for item in items}
    
    # 用Newton-Raphson迭代求MLE
    theta = 0.0  # 初始值
    for iteration in range(50):
        # 一阶导数 (score function)
        first_deriv = 0.0
        # 二阶导数 (information)
        second_deriv = 0.0
        
        for resp in responses:
            item = item_map.get(resp["item_id"])
            if not item:
                continue
            
            a = item["a"]
            b = item["b"]
            c = item.get("c", guess_c)
            correct = resp["correct"]
            
            p = irt_3pl(theta, a, b, c) if c > 0 else irt_2pl(theta, a, b)
            q = 1.0 - p
            
            if p * q < 1e-10:
                continue
            
            # 一阶导
            w = a * (p - c) / (p * (1 - c)) if c > 0 else a
            first_deriv += w * (int(correct) - p)
            
            # 二阶导 (Fisher Information)
            info = item_info(theta, a, b, c)
            second_deriv -= info
        
        if second_deriv == 0:
            break
        
        # Newton-Raphson更新
        delta = first_deriv / second_deriv
        theta -= delta
        
        if abs(delta) < 1e-4:
            break
    
    # 标准误
    total_info = sum(item_info(theta, item["a"], item["b"], item.get("c", guess_c))
                     for item in items if item["id"] in {r["item_id"] for r in responses})
    se = 1.0 / math.sqrt(max(total_info, 1e-10))
    
    # 截断到合理范围
    theta = max(-3.0, min(3.0, theta))
    
    return {
        "theta": round(theta, 3),
        "se": round(se, 3),
        "responses_count": len(responses),
    }


def estimate_theta_eap(responses: list[dict],
                       items: list[dict],
                       guess_c: float = 0.0,
                       prior_mean: float = 0.0,
                       prior_sd: float = 1.0) -> dict:
    """EAP贝叶斯估计（更适合少量答题的场景）
    
    使用高斯先验 N(prior_mean, prior_sd^2)，比MLE在小样本时更稳定
    """
    item_map = {item["id"]: item for item in items}
    
    # 在[-3, 3]区间用高斯求积
    n_quad = 30  # 求积节点数
    quad_points = [(-3.0 + i * 6.0 / (n_quad - 1)) for i in range(n_quad)]
    quad_weights = [1.0 / math.sqrt(2 * math.pi * prior_sd**2) * 
                    math.exp(-0.5 * ((t - prior_mean) / prior_sd)**2) 
                    for t in quad_points]
    
    # 归一化权重
    sum_w = sum(quad_weights)
    quad_weights = [w / sum_w for w in quad_weights]
    
    # 计算每个求积点的似然
    def likelihood(theta):
        ll = 0.0
        for resp in responses:
            item = item_map.get(resp["item_id"])
            if not item:
                continue
            p = irt_3pl(theta, item["a"], item["b"], item.get("c", guess_c))
            p = max(1e-10, min(p, 1 - 1e-10))
            if resp["correct"]:
                ll += math.log(p)
            else:
                ll += math.log(1 - p)
        return math.exp(ll)
    
    # EAP: 后验均值
    posterior = [likelihood(t) * w for t, w in zip(quad_points, quad_weights)]
    sum_post = sum(posterior)
    if sum_post == 0:
        return {"theta": 0.0, "se": 1.0, "responses_count": len(responses)}
    
    posterior = [p / sum_post for p in posterior]
    
    theta_eap = sum(t * p for t, p in zip(quad_points, posterior))
    var_eap = sum((t - theta_eap)**2 * p for t, p in zip(quad_points, posterior))
    se_eap = math.sqrt(max(var_eap, 1e-10))
    
    return {
        "theta": round(theta_eap, 3),
        "se": round(se_eap, 3),
        "responses_count": len(responses),
    }


# ================================================================
# 自适应选题
# ================================================================

def select_next_item(theta: float, 
                     available_items: list[dict],
                     n_select: int = 1,
                     excluded_ids: set = None) -> list[dict]:
    """自适应选题: 从可用题目中选择信息量最大的n道题
    
    输入:
        theta: 当前能力估计值
        available_items: 可用题库
        n_select: 选几道
        excluded_ids: 已答题的ID集合
    
    返回:
        选中题目的列表（按信息量降序）
    """
    if excluded_ids is None:
        excluded_ids = set()
    
    candidates = [item for item in available_items 
                  if item["id"] not in excluded_ids]
    
    # 计算每道题在当前theta处的信息量
    scored = []
    for item in candidates:
        c = item.get("c", 0.0)
        info = item_info(theta, item["a"], item["b"], c)
        scored.append((info, item))
    
    # 选信息量最大的
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [item for _, item in scored[:n_select]]
    
    return selected


def select_items_for_level(theta: float,
                           item_pool: list[dict],
                           n_easy: int = 2,
                           n_adaptive: int = 3,
                           excluded_ids: set = None) -> list[dict]:
    """为章节测试选题: 前n_easy道热身 + 后n_adaptive道自适应
    
    热身题选难度接近 theta-0.5 的，建立信心
    自适应题选信息量最大的
    
    返回格式:
        [{"item": item, "phase": "warmup"|"adaptive", "expected_p": float}, ...]
    """
    if excluded_ids is None:
        excluded_ids = set()
    
    available = [item for item in item_pool if item["id"] not in excluded_ids]
    
    result = []
    used_ids = set(excluded_ids)
    
    # 热身阶段: 选比当前能力略简单的题（theta-0.5附近）
    warmup_target = theta - 0.5
    warmup_candidates = sorted(available, 
                                key=lambda x: abs(x["b"] - warmup_target))
    for item in warmup_candidates[:n_easy]:
        if item["id"] not in used_ids:
            p = irt_2pl(theta, item["a"], item["b"])
            result.append({
                "item": item,
                "phase": "warmup",
                "expected_p": round(p, 3),
            })
            used_ids.add(item["id"])
    
    # 自适应阶段: 选信息量最大的
    remaining = [item for item in available if item["id"] not in used_ids]
    adaptive = select_next_item(theta, remaining, n_adaptive)
    for item in adaptive:
        p = irt_2pl(theta, item["a"], item["b"])
        result.append({
            "item": item,
            "phase": "adaptive",
            "expected_p": round(p, 3),
        })
    
    return result


# ================================================================
# IRT与BKT的联动
# ================================================================

def irt_to_bkt_mapping(theta: float) -> dict:
    """将IRT能力值映射到BKT掌握概率参考
    
    用于两个引擎之间的状态同步
    BKT: 0-1 知识点掌握概率
    IRT: -3~3 综合能力值
    
    映射关系（经验公式，需实际数据校准）:
      theta=-3 -> BKT~0.10 (完全不会)
      theta=-1 -> BKT~0.30 (入门)
      theta=0  -> BKT~0.50 (基本掌握)
      theta=1  -> BKT~0.70 (良好)
      theta=2  -> BKT~0.85 (熟练)
      theta=3  -> BKT~0.95 (精通)
    """
    bkt_approx = 0.5 + 0.15 * theta  # 线性近似，中等相关
    bkt_approx = max(0.05, min(0.98, bkt_approx))
    
    return {
        "theta": theta,
        "bkt_approx": round(bkt_approx, 3),
        "confidence": "low" if abs(theta) < 0.5 else ("medium" if abs(theta) < 1.5 else "high"),
        "level_label": (
            "未掌握" if theta < -1.0 else
            "入门" if theta < -0.3 else
            "基本掌握" if theta < 0.5 else
            "良好" if theta < 1.5 else
            "熟练" if theta < 2.5 else
            "精通"
        ),
    }


# ================================================================
# 题库管理
# ================================================================

class IRTItemBank:
    """IRT题库管理器"""
    
    def __init__(self, config_path: str = IRT_CONFIG):
        with open(config_path) as f:
            self.config = json.load(f)
        self.items = self.config["items"]
        self.item_index = {item["id"]: item for item in self.items}
    
    def get_by_level(self, level: str) -> list[dict]:
        """获取某个级别的所有题目"""
        return [item for item in self.items if item.get("level") == level]
    
    def get_by_kp(self, kp_id: str) -> list[dict]:
        """获取某个知识点的所有题目"""
        return [item for item in self.items if item.get("kp_id") == kp_id]
    
    def select_test(self, theta: float, level: str = None,
                    kp_id: str = None, n_total: int = 5) -> list[dict]:
        """为某个学员生成一次自适应测试
        
        返回:
            [{"item": item, "phase": "warmup"|"adaptive", "expected_p": float}, ...]
        """
        pool = self.items
        if level:
            pool = self.get_by_level(level)
        if kp_id:
            pool = self.get_by_kp(kp_id)
        
        if not pool:
            return []
        
        # 2热身+3自适应
        return select_items_for_level(theta, pool, n_easy=2, n_adaptive=n_total-2)
    
    def simulate_test(self, theta_true: float, items: list[dict]) -> list[dict]:
        """模拟一次IRT测试（用于验证算法）
        
        根据真实能力theta_true生成答题结果
        """
        responses = []
        for entry in items:
            item = entry["item"]
            p = irt_3pl(theta_true, item["a"], item["b"], item.get("c", 0.0))
            correct = random.random() < p
            responses.append({
                "item_id": item["id"],
                "correct": correct,
                "expected_p": round(p, 3),
            })
        return responses


# ================================================================
# 快速测试
# ================================================================
if __name__ == "__main__":
    import random
    
    print("=== IRT自适应出题引擎 v1.0 测试 ===\n")
    
    # 测试1: IRT 2PL模型曲线
    print("--- 测试1: IRT 2PL模型 ---")
    for theta in [-2, -1, 0, 1, 2]:
        p = irt_2pl(theta, a=1.0, b=0.0)
        print(f"  theta={theta:+.0f}, a=1.0, b=0.0 -> P={p:.3f}")
    print()
    
    # 测试2: 题目信息函数
    print("--- 测试2: 信息函数 ---")
    for theta in [-1, 0, 1]:
        info = item_info(theta, a=1.5, b=0.5, c=0.0)
        print(f"  theta={theta:+.0f}, a=1.5, b=0.5 -> I={info:.3f}")
    print()
    
    # 测试3: 能力估计（模拟5次答题）
    print("--- 测试3: MLE能力估计 ---")
    items = [
        {"id": "IRT_L1_01", "a": 1.0, "b": -1.0, "c": 0.0},
        {"id": "IRT_L1_02", "a": 1.2, "b": -0.5, "c": 0.0},
        {"id": "IRT_L2_01", "a": 1.0, "b": 0.0, "c": 0.0},
        {"id": "IRT_L2_02", "a": 1.5, "b": 0.5, "c": 0.0},
        {"id": "IRT_L3_01", "a": 1.0, "b": 1.0, "c": 0.0},
    ]
    # 模拟一个能力中等偏上的学员(真实theta=1.0)
    responses = []
    for item in items:
        p = irt_2pl(1.0, item["a"], item["b"])
        correct = random.random() < p
        responses.append({"item_id": item["id"], "correct": correct})
        print(f"  {item['id']} b={item['b']:+.1f} P={p:.3f} -> {'正确' if correct else '错误'}")
    
    mle = estimate_theta_mle(responses, items)
    eap = estimate_theta_eap(responses, items)
    print(f"  MLE估计: theta={mle['theta']}, se={mle['se']}")
    print(f"  EAP估计: theta={eap['theta']}, se={eap['se']}")
    print()
    
    # 测试4: 自适应选题
    print("--- 测试4: 自适应选题 ---")
    pool = [
        {"id": f"IRT_L{i}_j{j}", "a": 1.0 + j*0.2, "b": -2.0 + i*0.8, "c": 0.0}
        for i in range(6) for j in range(3)
    ]
    
    for test_theta in [-1.0, 0.0, 1.5]:
        selected = select_items_for_level(test_theta, pool)
        print(f"  theta={test_theta:+.1f} 选5题:")
        for s in selected:
            print(f"    [{s['phase']}] ID={s['item']['id']} "
                  f"b={s['item']['b']:+.1f} a={s['item']['a']:.1f} "
                  f"期望正确率={s['expected_p']:.2f}")
    print()
    
    # 测试5: IRT-BKT映射
    print("--- 测试5: IRT-BKT映射 ---")
    for theta in [-2, -1, 0, 1, 2, 3]:
        mapping = irt_to_bkt_mapping(theta)
        print(f"  theta={theta:+.0f} -> BKT≈{mapping['bkt_approx']} [{mapping['level_label']}]")
    
    print(f"\n{'='*50}")
    print(f"吸收来源: lextures (StudyDrift/lextures) IRT 2PL/3PL")
    print(f"{'='*50}")
