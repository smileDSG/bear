# -*- coding: utf-8 -*-
"""
命令行入口。

用法：
    python check.py demo/data.json --rules demo/rules.json

退出码：
    0 = 没有 error（可能有 warn）
    1 = 有 error
    2 = 文件读不了或 JSON 格式错
"""

import sys
import os
import json
import lint


def parse_args(args):
    """把命令行参数拆成数据路径和规则路径。"""
    data_path = None
    rules_path = None
    index = 0
    while index < len(args):
        if args[index] == "--rules":
            if index + 1 < len(args):
                rules_path = args[index + 1]
            index = index + 2
        else:
            data_path = args[index]
            index = index + 1
    return data_path, rules_path


def main():
    data_path, rules_path = parse_args(sys.argv[1:])
    if not data_path or not rules_path:
        print("用法: python check.py <数据.json> --rules <规则.json>")
        return 2

    base_dir = os.path.dirname(os.path.abspath(rules_path))
    try:
        data = lint.load_json_strict(data_path)
        rules = lint.load_json_strict(rules_path)
    except lint.DuplicateKeyError as exc:
        print("[ERROR] 重复键: " + exc.key)
        return 2
    except json.JSONDecodeError as exc:
        print("[ERROR] JSON 格式错误: " + str(exc))
        return 2
    except OSError as exc:
        print("[ERROR] 读文件失败: " + str(exc))
        return 2

    issues = lint.run_rules(data, rules, base_dir)
    for issue in issues:
        print(issue.render())

    error_count = 0
    for issue in issues:
        if issue.level == "error":
            error_count = error_count + 1
    print("---")
    print("共 " + str(len(issues)) + " 条问题，其中 error " + str(error_count) + " 条")

    if error_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
