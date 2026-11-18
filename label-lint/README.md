# label-lint：结构化数据契约质检器

一份数据 + 一份规则，查出四类常见的质量问题。**不认识任何业务字段**——你定义字段，它只负责检查集合关系。

## 它解决什么问题

标注数据、事件数据、配置表在交付前常犯四类错，而且都能用集合关系描述：

| 问题 | 人话 | 本工具里的检查 |
|---|---|---|
| 悬空引用 | 引用了一个不存在的东西 | `subset`：用到的值必须在允许集合里 |
| 没人消费 | 造了数据但没进训练/没被读 | `no_orphan`：造出来的东西必须有人用 |
| 重复标识 | 两条数据用了同一个 id | `unique`：一组值里不能有重复 |
| 证据不足 | 某个类别样本太少，结论不可信 | `min_count`：每组至少 N 条 |

这四类检查来自一个评分系统的构建期校验实践——那里管这叫"旗标完整性"和"证据地板"。剥掉业务外壳后，它们就是通用的数据质检模式。

## 用法

```bash
python check.py demo/data.json --rules demo/rules.json
```

退出码：`0` = 没有 error；`1` = 有 error；`2` = 文件读不了或 JSON 格式错。可以直接接 CI。

跑一遍示例，会报出：重复的样本 id、未注册的标签、没人用的标签、没在报告里兑现的标签、证据不足的维度——一次覆盖上面全部四类。

严格 JSON 加载：重复键、注释、尾逗号都会报错（默认 `json.loads` 会吞掉重复键）。

## 规则怎么写

规则是一个 JSON，五个字段描述一条检查：

```json
{
  "id": "label_registered",
  "kind": "subset",
  "desc": "样本用的标签必须都在注册表里",
  "subset": {"path": "samples.*.label"},
  "superset": {"path": "labels.*.id"},
  "severity": "error"
}
```

- `id`：这条检查的名字，出现在报告里
- `kind`：四种之一，见下表
- `desc`：给人看的说明
- `severity`：`error` 或 `warn`（默认 `error`），只有 `error` 影响退出码
- 其余字段按 `kind` 不同，见下表

### 路径语法

用点号往下走，`*` 表示展开当前的列表或字典所有元素：

```
samples.*.label        →  取每个样本的 label
samples.*.used_in.*    →  取每个样本 used_in 列表里的每个值
```

### 四种检查

| kind | 需要的字段 | 含义 |
|---|---|---|
| `subset` | `subset`, `superset` | 左边每个值都要在右边集合里 |
| `no_orphan` | `source`, `target` | source 每个值都要在 target 里出现 |
| `unique` | `items` | items 里不能有重复值 |
| `min_count` | `items`, `min_each`, `min_total`(可选) | items 按值分组，每组至少 `min_each` 条；总数至少 `min_total` |

每一边（`subset` / `superset` / `source` / `target` / `items`）都是一个对象：

```json
{"path": "samples.*.label"}
{"file": "other.json", "path": "labels.*.id"}
```

带 `file` 时从规则文件所在目录加载另一个 JSON；不带就用命令行传入的主数据文件。这样可以跨文件对比。

## 结构

```
lint.py          通用内核：加载、路径取值、四种检查、报告
check.py         命令行入口
test_lint.py     单元测试（python test_lint.py）
demo/
  data.json      故意有问题的示例数据
  rules.json     对应的规则
```

## 设计取舍

- **只做集合关系，不做语义判断。** "这个标签该不该存在"是业务问题，交给规则作者；工具只保证规则被严格执行。
- **warn 不等于失败。** 很多质量问题（比如没人用的标签）是提示不是错误，退出码不受影响，适合渐进接入。
- **无第三方依赖。** 只用 Python 标准库，Python 3.7+ 可跑。

## 来源说明

这套检查模式提炼自一个带评分卡的剧情评估系统：那里需要保证每条旗标都有埋设端和消费端、每个维度都有足够证据。把具体的旗标名和维度名去掉后，剩下的就是通用的集合关系检查，于是有了这个工具。
