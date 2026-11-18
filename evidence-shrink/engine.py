# -*- coding: utf-8 -*-
"""
证据收缩引擎：把「先验分 + 加权行为证据」合成一个后验分。

解决的问题：
    只有少量行为证据时，直接给分不可信；完全不信证据、只听自评也不对。
    这个引擎用一个随证据量增长的系数把两者平滑合并——证据越多，越信行为。

通用接口：任意维度名都能用。不认识大五，不认识游戏状态。

核心公式：
    K       = n / (n + k_denom)          n 是有效证据量
    行为分  = mid + dev_max × mean(dir × coef × weight) × loading
    后验    = prior + K × (行为分 - prior)
    矛盾度  = |prior - 后验|，超过阈值判显著

四个通用机制：
    1. 收缩：证据少时后验靠近先验，证据多时靠近行为
    2. 证据地板：有效证据不足时，行为分和后验都不给（不硬编结论）
    3. 跨情境一致性：按 coef 分两组，方向同号=稳定，异号=看场合，样本不足=无法判定
    4. 矛盾度：自评和行为差距过大时标记出来

这个模式可用于任何"先验 + 观测 → 更新后验"的场景，比如评分校准：
人类初评当先验，多个观测信号当证据，证据不足时不要输出武断的分数。
"""


def default_config():
    """默认参数。与原实现的口径一致，都可覆盖。"""
    return {
        "mid": 5.0,                  # 量表中点
        "dev_max": 5.0,              # 行为分最大偏离幅度
        "k_denom": 5,                # 收缩系数分母：K = n / (n + 5)
        "min_evidence": 3,           # 证据地板：有效证据 < 3 不出行为分
        "conflict_threshold": 1.5,   # 矛盾度超过此值判显著
        "display_mid": 50,           # 展示分中性起点
        "display_scale": 10.0,       # 行为分→展示分的放大系数
        "display_denom": 3.0,        # 展示分收缩分母
        "alone_coef_min": 0.9,       # coef >= 此值算"没人看着"组
        "watched_coef_max": 0.6,     # coef <= 此值算"有人盯着"组
        "consistency_min": 3,        # 每组至少几条才判一致性
    }


def effective_n(evidence):
    """有效证据量 = 每条证据 strength 之和（缺省按 1 条算）。"""
    total = 0.0
    for item in evidence:
        total += float(item.get("strength", 1.0))
    return total


def behavior_score(evidence, config, loading=1.0):
    """加权行为分。strength 作权重，dir×coef 做方向×情境系数。"""
    if not evidence:
        return None
    weights = []
    weighted_sum = 0.0
    for item in evidence:
        weight = float(item.get("strength", 1.0))
        direction = float(item.get("dir", 1))
        coef = float(item.get("coef", 0.75))
        weights.append(weight)
        weighted_sum = weighted_sum + direction * coef * weight
    total_weight = sum(weights)
    if total_weight == 0:
        return None
    mean_ratio = weighted_sum / total_weight
    mid = config["mid"]
    dev = config["dev_max"]
    return round(mid + dev * mean_ratio * loading, 2)


def behavior_std(evidence, config):
    """行为证据的样本标准差。不足 2 条返回 None。"""
    vals = []
    for item in evidence:
        vals.append(float(item.get("weighted", 0.0)))
    if len(vals) < 2:
        return None
    mean = sum(vals) / len(vals)
    var = 0.0
    for value in vals:
        var = var + (value - mean) ** 2
    var = var / (len(vals) - 1)
    return round(var ** 0.5, 3)


def consistency(evidence, config):
    """跨情境一致性。返回 consistent / situational / None(无法判定)。

    只看 strength >= 1 的强证据；按 coef 分两组，各自按 dir 取均值判方向。
    任一组不足 consistency_min 条，或某组均值为 0，都返回 None。
    """
    groups = {"alone": [], "watched": []}
    for item in evidence:
        if float(item.get("strength", 1.0)) < 1.0:
            continue
        coef = float(item.get("coef", 0.75))
        if coef >= config["alone_coef_min"]:
            groups["alone"].append(int(item.get("dir", 1)))
        elif coef <= config["watched_coef_max"]:
            groups["watched"].append(int(item.get("dir", 1)))

    means = {}
    for name in ("alone", "watched"):
        dirs = groups[name]
        if len(dirs) < config["consistency_min"]:
            return None
        means[name] = sum(dirs) / len(dirs)

    a = means["alone"]
    b = means["watched"]
    if a == 0 or b == 0:
        return None
    if (a > 0) == (b > 0):
        return "consistent"
    return "situational"


def display_score(evidence, config, loading=1.0):
    """展示分：向 display_mid 收缩的 0-100 分，仅用于展示，不参与判定。"""
    raw = behavior_score(evidence, config, loading)
    if raw is None:
        return config["display_mid"]
    n = effective_n(evidence)
    value = config["display_mid"] + (raw - config["mid"]) * config["display_scale"] * n / (n + config["display_denom"])
    value = int(round(value))
    return max(0, min(100, value))


def shrink(prior, evidence, config, loading=1.0):
    """主入口：先验 + 证据 → 完整结果字典。

    prior: 先验分（0-10 制，缺省 None 表示没有自评）
    evidence: 证据列表，每条形如 {"dir": 1, "coef": 0.75, "strength": 1.0, "weighted": 0.75}
    config: default_config() 的返回值，可覆盖部分字段
    loading: 该维度的载荷系数，缺省 1.0
    """
    n = effective_n(evidence)
    count = len(evidence)
    enough = n >= config["min_evidence"]

    behavior = behavior_score(evidence, config, loading) if enough else None
    raw_behavior = behavior_score(evidence, config, loading)
    std = behavior_std(evidence, config) if enough else None
    consist = consistency(evidence, config) if enough else None
    shown = display_score(evidence, config, loading)

    posterior = None
    conflict = None
    conflict_significant = False

    if prior is not None and behavior is not None:
        k = n / (n + config["k_denom"])
        posterior = round(prior + k * (behavior - prior), 2)
        conflict = round(abs(prior - posterior), 2)
        conflict_significant = conflict > config["conflict_threshold"]

    if enough:
        status = "established"
    elif n > 0:
        status = "limited"
    else:
        status = "none"

    return {
        "prior": prior,
        "behavior": behavior,
        "posterior": posterior,
        "conflict": conflict,
        "conflict_significant": conflict_significant,
        "display_score": shown,
        "status": status,
        "evidence_count": count,
        "effective_n": round(n, 4),
        "behavior_std": std,
        "consistency": consist,
        "behavior_available": behavior is not None,
    }


def shrink_many(priors, evidence_by_dim, configs=None, loadings=None):
    """批量：对多个维度各跑一次 shrink。

    priors: {"O": 7.0, "C": 6.0, ...}  值可以为 None
    evidence_by_dim: {"O": [...], "C": [...], ...}
    configs: {"O": {...}, ...}  可选，某维度专属参数
    loadings: {"O": 0.6, ...}  可选，某维度载荷
    """
    configs = configs or {}
    loadings = loadings or {}
    results = {}
    for dim in priors:
        base = default_config()
        if dim in configs:
            for key in configs[dim]:
                base[key] = configs[dim][key]
        dim_evidence = evidence_by_dim.get(dim, [])
        results[dim] = shrink(
            priors[dim], dim_evidence, base, loadings.get(dim, 1.0)
        )
    return results
