# -*- coding: utf-8 -*-
"""
单元测试。

第一组测机制边界，第二组用原 bayes.py 的数值口径做一致性核对。
运行：python test_engine.py
"""

import engine


def test_defaults():
    config = engine.default_config()
    assert config["mid"] == 5.0
    assert config["k_denom"] == 5
    assert config["min_evidence"] == 3


def test_effective_n():
    evidence = [
        {"strength": 1.0},
        {"strength": 0.5},
        {"strength": 1.0},
    ]
    assert engine.effective_n(evidence) == 2.5


def test_evidence_floor_blocks_posterior():
    # 1 条证据 < 地板 3 → 行为分、后验都不给
    evidence = [{"dir": 1, "coef": 0.75, "strength": 1.0}]
    result = engine.shrink(8.0, evidence, engine.default_config())
    assert result["behavior"] is None
    assert result["posterior"] is None
    assert result["status"] == "limited"
    # 展示分不受证据地板影响：给一个向中性收缩的分，但不下结论。
    # 1 条证据 dir=1/coef=0.75 → 行为分 8.75 → 展示分 round(50+3.75*10*1/4)=59
    assert result["display_score"] == 59


def test_shrink_toward_behavior():
    # 自评 10，行为分 0，3 条证据 → K = 3/8 = 0.375，后验 = 10 + 0.375*(0-10) = 6.25
    evidence = [
        {"dir": -1, "coef": 1.0, "strength": 1.0},
        {"dir": -1, "coef": 1.0, "strength": 1.0},
        {"dir": -1, "coef": 1.0, "strength": 1.0},
    ]
    result = engine.shrink(10.0, evidence, engine.default_config())
    assert result["posterior"] == 6.25
    assert result["conflict"] == 3.75
    assert result["conflict_significant"] is True


def test_consistency_stable():
    evidence = [
        {"dir": 1, "coef": 1.0, "strength": 1.0},
        {"dir": 1, "coef": 1.0, "strength": 1.0},
        {"dir": 1, "coef": 1.0, "strength": 1.0},
        {"dir": 1, "coef": 0.5, "strength": 1.0},
        {"dir": 1, "coef": 0.5, "strength": 1.0},
        {"dir": 1, "coef": 0.5, "strength": 1.0},
    ]
    assert engine.consistency(evidence, engine.default_config()) == "consistent"


def test_consistency_situational():
    evidence = [
        {"dir": 1, "coef": 1.0, "strength": 1.0},
        {"dir": 1, "coef": 1.0, "strength": 1.0},
        {"dir": 1, "coef": 1.0, "strength": 1.0},
        {"dir": -1, "coef": 0.5, "strength": 1.0},
        {"dir": -1, "coef": 0.5, "strength": 1.0},
        {"dir": -1, "coef": 0.5, "strength": 1.0},
    ]
    assert engine.consistency(evidence, engine.default_config()) == "situational"


def test_consistency_not_enough():
    evidence = [
        {"dir": 1, "coef": 1.0, "strength": 1.0},
        {"dir": 1, "coef": 0.5, "strength": 1.0},
    ]
    assert engine.consistency(evidence, engine.default_config()) is None


def test_behavior_std():
    evidence = [
        {"weighted": 1.0},
        {"weighted": 2.0},
        {"weighted": 3.0},
    ]
    assert engine.behavior_std(evidence, engine.default_config()) == 1.0


def test_matches_original_numbers():
    """用原 bayes.py 的公式口径核对：behavior=mid+dev*mean(dir*coef*w)/sum(w)*loading。"""
    config = engine.default_config()
    evidence = [
        {"dir": 1, "coef": 0.75, "strength": 1.0, "weighted": 0.75},
        {"dir": -1, "coef": 0.5, "strength": 1.0, "weighted": -0.5},
        {"dir": 1, "coef": 1.0, "strength": 1.0, "weighted": 1.0},
    ]
    loading = 0.6
    result = engine.shrink(7.0, evidence, config, loading)

    # 原实现手算：mean_ratio = (0.75 - 0.5 + 1.0) / 3 = 0.416666...
    mean_ratio = (0.75 - 0.5 + 1.0) / 3
    expected_behavior = round(5.0 + 5.0 * mean_ratio * loading, 2)
    assert result["behavior"] == expected_behavior

    # K = 3/(3+5) = 0.375，后验 = 7 + 0.375*(behavior - 7)
    k = 3 / 8
    expected_posterior = round(7.0 + k * (expected_behavior - 7.0), 2)
    assert result["posterior"] == expected_posterior


def test_batch():
    priors = {"O": 7.0, "C": None}
    evidence = {
        "O": [
            {"dir": 1, "coef": 1.0, "strength": 1.0},
            {"dir": 1, "coef": 1.0, "strength": 1.0},
            {"dir": 1, "coef": 1.0, "strength": 1.0},
        ],
        "C": [],
    }
    results = engine.shrink_many(priors, evidence)
    assert results["O"]["status"] == "established"
    assert results["C"]["posterior"] is None


def run_all():
    test_defaults()
    test_effective_n()
    test_evidence_floor_blocks_posterior()
    test_shrink_toward_behavior()
    test_consistency_stable()
    test_consistency_situational()
    test_consistency_not_enough()
    test_behavior_std()
    test_matches_original_numbers()
    test_batch()
    print("10/10 测试通过")


run_all()
