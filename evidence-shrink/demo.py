# -*- coding: utf-8 -*-
"""演示：评分校准场景——人类初评当先验，多个观测信号当证据。"""

import engine


def show(title, result):
    print("=== " + title + " ===")
    print("  有效证据 n = " + str(result["effective_n"]) + "，状态 = " + result["status"])
    print("  行为分 = " + str(result["behavior"]) + "，后验 = " + str(result["posterior"]))
    print("  展示分 = " + str(result["display_score"]) + "，矛盾显著 = " + str(result["conflict_significant"]))
    print("  一致性 = " + str(result["consistency"]))


config = engine.default_config()

# 场景一：证据充足，方向一致。后验从自评 6.0 向行为分靠拢。
evidence_many = [
    {"dir": 1, "coef": 1.0, "strength": 1.0, "weighted": 1.0},
    {"dir": 1, "coef": 1.0, "strength": 1.0, "weighted": 1.0},
    {"dir": 1, "coef": 0.5, "strength": 1.0, "weighted": 0.5},
]
show("证据充足 + 方向一致", engine.shrink(6.0, evidence_many, config))

# 场景二：证据不足（只有 1 条）。行为分和后验都不给，只有展示分。
evidence_few = [
    {"dir": 1, "coef": 0.75, "strength": 1.0, "weighted": 0.75},
]
show("证据不足（不硬给结论）", engine.shrink(8.0, evidence_few, config))

# 场景三：自评很高、行为证据偏低，矛盾度超阈值。
evidence_low = [
    {"dir": -1, "coef": 1.0, "strength": 1.0, "weighted": -1.0},
    {"dir": -1, "coef": 1.0, "strength": 1.0, "weighted": -1.0},
    {"dir": -1, "coef": 1.0, "strength": 1.0, "weighted": -1.0},
]
show("自评与行为矛盾", engine.shrink(9.0, evidence_low, config))

# 场景四：没人看着时正向、有人盯着时负向 → 看场合，不是稳定特质。
evidence_split = [
    {"dir": 1, "coef": 1.0, "strength": 1.0, "weighted": 1.0},
    {"dir": 1, "coef": 1.0, "strength": 1.0, "weighted": 1.0},
    {"dir": 1, "coef": 1.0, "strength": 1.0, "weighted": 1.0},
    {"dir": -1, "coef": 0.5, "strength": 1.0, "weighted": -0.5},
    {"dir": -1, "coef": 0.5, "strength": 1.0, "weighted": -0.5},
    {"dir": -1, "coef": 0.5, "strength": 1.0, "weighted": -0.5},
]
show("跨情境方向相反", engine.shrink(5.0, evidence_split, config))
