# -*- coding: utf-8 -*-
"""
数据契约质检内核。

输入：一份结构化数据 + 一份声明式规则。
输出：问题清单（error / warn）。

这个模块不认识任何业务字段。它只会按路径从数据里取出一组值，
然后检查集合之间的关系：谁必须是谁的子集、谁不能没人用、谁不能重复、
某类东西至少要有几条。

路径语法（点号分段，* 表示展开）：
    nodes.*.choices.*.flags.*
    - 普通字段名：往下取一层
    - *：把当前的列表或字典全部展开
"""

import json


class DuplicateKeyError(Exception):
    """JSON 里出现了重复键。"""

    def __init__(self, key):
        self.key = key


def _no_dup(pairs):
    """给 json.loads 用的钩子：一发现重复键就抛异常。"""
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


def load_json_strict(path):
    """严格加载 JSON。重复键、注释、尾逗号都会报错。"""
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    return json.loads(text, object_pairs_hook=_no_dup)


def collect(data, path):
    """按点路径取值。返回所有命中的值，组成列表。"""
    parts = path.split(".")
    current = [data]
    for part in parts:
        nxt = []
        for item in current:
            if part == "*":
                if isinstance(item, list):
                    for sub in item:
                        nxt.append(sub)
                elif isinstance(item, dict):
                    for key in item:
                        nxt.append(item[key])
            else:
                if isinstance(item, dict) and part in item:
                    nxt.append(item[part])
        current = nxt
    return current


def to_key(value):
    """把任意值归一成可比较的字符串。"""
    if value is None:
        return ""
    if isinstance(value, bool):
        if value:
            return "true"
        return "false"
    return str(value)


class Issue:
    """一条问题。"""

    def __init__(self, level, check_id, message):
        self.level = level
        self.check_id = check_id
        self.message = message

    def render(self):
        return "[" + self.level.upper() + "] " + self.check_id + " - " + self.message


def resolve_values(side, base_dir, default_data, cache):
    """按规则里的一边取出值列表。

    side 形如 {"path": "nodes.*.id"}，可以带 "file": "other.json"。
    带 file 时从 base_dir 下加载那个文件；不带就用主数据文件。
    """
    file_name = side.get("file")
    if file_name:
        full = base_dir + "/" + file_name
        if full not in cache:
            cache[full] = load_json_strict(full)
        data = cache[full]
    else:
        data = default_data
    return collect(data, side["path"])


def _keys(values):
    """把值列表转成去重的字符串集合。"""
    result = set()
    for value in values:
        result.add(to_key(value))
    return result


def check_subset(spec, base_dir, data, cache):
    """subset：左边每个值都必须出现在右边集合里。"""
    left = resolve_values(spec["subset"], base_dir, data, cache)
    right = resolve_values(spec["superset"], base_dir, data, cache)
    right_keys = _keys(right)
    bad = set()
    for value in left:
        key = to_key(value)
        if key not in right_keys:
            bad.add(key)
    if bad:
        msg = "不在允许集合中的值: " + ", ".join(sorted(bad))
        return [Issue(spec.get("severity", "error"), spec["id"], msg)]
    return []


def check_no_orphan(spec, base_dir, data, cache):
    """no_orphan：source 里每个值都必须在 target 里被消费。"""
    source = resolve_values(spec["source"], base_dir, data, cache)
    target = resolve_values(spec["target"], base_dir, data, cache)
    target_keys = _keys(target)
    orphan = set()
    for value in source:
        key = to_key(value)
        if key not in target_keys:
            orphan.add(key)
    if orphan:
        msg = "没有被消费的值: " + ", ".join(sorted(orphan))
        return [Issue(spec.get("severity", "warn"), spec["id"], msg)]
    return []


def check_unique(spec, base_dir, data, cache):
    """unique：items 里不能有重复值。"""
    items = resolve_values(spec["items"], base_dir, data, cache)
    seen = set()
    dup = set()
    for value in items:
        key = to_key(value)
        if key in seen:
            dup.add(key)
        seen.add(key)
    if dup:
        msg = "重复的值: " + ", ".join(sorted(dup))
        return [Issue(spec.get("severity", "error"), spec["id"], msg)]
    return []


def check_min_count(spec, base_dir, data, cache):
    """min_count：items 按值分组，每组至少 min_each 条；总数至少 min_total。"""
    items = resolve_values(spec["items"], base_dir, data, cache)
    counts = {}
    for value in items:
        key = to_key(value)
        counts[key] = counts.get(key, 0) + 1
    min_each = int(spec.get("min_each", 1))
    issues = []
    for key in sorted(counts):
        if counts[key] < min_each:
            msg = key + " 只有 " + str(counts[key]) + " 条，少于 " + str(min_each)
            issues.append(Issue(spec.get("severity", "warn"), spec["id"], msg))
    min_total = spec.get("min_total")
    if min_total:
        if len(items) < int(min_total):
            msg = "总数 " + str(len(items)) + " 条，少于 " + str(min_total)
            issues.append(Issue(spec.get("severity", "warn"), spec["id"], msg))
    return issues


def run_rules(data, rules, base_dir):
    """跑完整个规则集，返回问题清单。"""
    issues = []
    cache = {}
    for spec in rules["checks"]:
        kind = spec["kind"]
        if kind == "subset":
            found = check_subset(spec, base_dir, data, cache)
        elif kind == "no_orphan":
            found = check_no_orphan(spec, base_dir, data, cache)
        elif kind == "unique":
            found = check_unique(spec, base_dir, data, cache)
        elif kind == "min_count":
            found = check_min_count(spec, base_dir, data, cache)
        else:
            found = [Issue("error", spec["id"], "未知的检查类型: " + kind)]
        for issue in found:
            issues.append(issue)
    return issues
