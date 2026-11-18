# -*- coding: utf-8 -*-
"""
单元测试。只测通用内核，不涉及任何业务。

运行：python test_lint.py
"""

import lint


def test_collect():
    data = {"a": [{"b": ["x", "y"]}, {"b": ["z"]}]}
    assert lint.collect(data, "a.*.b.*") == ["x", "y", "z"]


def test_collect_missing_path():
    data = {"a": [{"b": ["x"]}]}
    assert lint.collect(data, "a.*.c.*") == []


def test_subset_pass():
    spec = {
        "id": "t",
        "kind": "subset",
        "subset": {"path": "a.*"},
        "superset": {"path": "b.*"}
    }
    data = {"a": ["x", "y"], "b": ["x", "y", "z"]}
    issues = lint.check_subset(spec, "", data, {})
    assert issues == []


def test_subset_fail():
    spec = {
        "id": "t",
        "kind": "subset",
        "subset": {"path": "a.*"},
        "superset": {"path": "b.*"}
    }
    data = {"a": ["x", "q"], "b": ["x", "y"]}
    issues = lint.check_subset(spec, "", data, {})
    assert len(issues) == 1
    assert "q" in issues[0].message


def test_no_orphan():
    spec = {
        "id": "t",
        "kind": "no_orphan",
        "source": {"path": "a.*"},
        "target": {"path": "b.*"}
    }
    data = {"a": ["x", "ghost"], "b": ["x"]}
    issues = lint.check_no_orphan(spec, "", data, {})
    assert len(issues) == 1
    assert "ghost" in issues[0].message
    assert issues[0].level == "warn"


def test_unique():
    spec = {"id": "t", "kind": "unique", "items": {"path": "a.*"}}
    data = {"a": ["x", "x", "y"]}
    issues = lint.check_unique(spec, "", data, {})
    assert len(issues) == 1
    assert "x" in issues[0].message


def test_min_count():
    spec = {
        "id": "t",
        "kind": "min_count",
        "items": {"path": "a.*.dim"},
        "min_each": 2
    }
    data = {"a": [{"dim": "O"}, {"dim": "O"}, {"dim": "C"}]}
    issues = lint.check_min_count(spec, "", data, {})
    assert len(issues) == 1
    assert "C" in issues[0].message


def test_to_key_bool():
    assert lint.to_key(True) == "true"
    assert lint.to_key(None) == ""


def run_all():
    test_collect()
    test_collect_missing_path()
    test_subset_pass()
    test_subset_fail()
    test_no_orphan()
    test_unique()
    test_min_count()
    test_to_key_bool()
    print("8/8 测试通过")


run_all()
