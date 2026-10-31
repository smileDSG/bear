# AGENTS.md

写给在本目录工作的 AI 编码代理（Codex / Qoder / Claude Code 等）。先读这一页，再按它指到的册子查细节。

## 项目

**熊心壮职（职场小镇）**：2D 像素风职业测评叙事游戏。玩家以实习开发师的身份走完十二个月职场主线，选择与自由活动生成能力证据，第 6 / 7 / 12 月做判定，最后出报告。当前主玩法是 `12m_v1`；旧 48 个月引擎与旧存档只读保留，不在本期改动范围。

## 两个仓库

- 本目录 `E:\03_Projects\bear` 是**文档仓**：三册、素材、归档、`_bak_*` 手工备份。根 `.gitignore` 把 `workplace_town/` 整体忽略。
- `workplace_town/` 是**游戏仓**（有自己的 `.git`）：Godot 工程、剧情数据、Python 后端、测试都在这里。改代码、跑测试先 `cd workplace_town`。
- `workplace_town/AGENTS.md` 是游戏仓侧的说明；代码工作以它为准，本文件负责两仓关系和三册口径。
- 两仓分开提交，不要把根仓和游戏仓混进同一个提交。

## 三册是地基

| 册 | 位置 | 管什么 |
|---|---|---|
| 剧情册 | `剧情册.docx` | 玩家看到什么、说什么、选什么；原话与分支的唯一来源 |
| 算法册 | `十二个月报告算法册_V1.md` | 数值、阈值、证据、M6/M7/M12 判定、报告口径 |
| 开发册 | `十二个月开发文档_V1.md` | 怎么落地：数据放哪、状态、接口、客户端文件、验收 |

- 三册不能分开读。玩家可见内容以剧情册为准，数值与判定以算法册为准，落地细节以开发册为准。
- 发现冲突：先改开发册，并在开发册第 15 节验收里记一条；不要只在聊天里定一个新口径。
- 改剧情的顺序：剧情册 → 算法册的选项打分卡 → 开发册 §4 数据契约。不要另造对白、选项、字段或旗标。
- `workplace_town/README.md` 管环境、启动和旧壳层说明；十二个月流程以开发册为准。`web/` 只是开场版式原型，不是游戏本体。`docs/legacy/` 只读。

## 任务与设计文档（强约束）

以下路径相对游戏仓 `workplace_town/`，从下一个任务开始执行：

- 每个任务必须对应一份 `docs/tasks/任务名.md`；开工时建，收工时补全。
- 任务文件必须包含五段：**目标、输入文档、关键决策、问题、待同步项**。
- 任务完成后，必须把结论同步回 `docs/design/` 中对应的那一份设计文档。
- 新增文档前先搜索 `docs/`；同一个功能只允许一份设计文档。
- 不允许创建 `docs/design/v1`、`docs/design/old`、`docs/design/backup` 这类目录；设计更新写在原文档里。
- 设计文档必须包含接口定义和数据结构。
- 生成代码前先确认设计完整；设计缺接口定义，先补设计，不要直接生成实现代码。
- 三册仍是内容地基；`docs/design/` 只写这个功能怎么实现，不复制三册原文。与三册冲突时以三册为准，并回改对应册。

## 当前实现（2026-10 末）

- 剧情数据：`data/story/v12m/` 下的 `manifest.json`、`events.json`、`activities.json`、`hints.json`、`rubrics.json`、`terms.json`。运行时直接读 JSON，字段见开发册 §4。
- 客户端：`scripts/WorkplaceTown.gd` 是主控制器（约 6400 行）；`scripts/v12m/` 放月份流程、手机、月末卡、解锁卡和过场；`StoryEventPanel.gd` 播剧情 beat。
- 十二个月流程目前在客户端推进。`backend/api/server.py`（`127.0.0.1:8077`）负责本地会话、埋点、NPC 记忆与报告；`backend/engine_core/` 是旧引擎内核。
- 开发册 §3 写的 `backend/engine_core/app/v12m/` 是计划目录，目前不存在，别照它找文件。
- `entry/` 是鸿蒙 ArkTS 外壳，只装 Godot Web 导出包，不写游戏规则。API 23 模拟器可跑，API 26 因 WebGL2 不可用（见 `HARMONY_RUN.md`）。

## 运行与验收

Windows 双击 `Start-Game.cmd`。需要 Python 3.10+ 和 Godot 4.7.x；本机 Godot 在 `D:\Apps\Godot\Godot_v4.7.2-stable_win64_console.exe`（换了机器就设 `GODOT_EXE`）。启动前必须有 `backend/local_llm_config.json`（从 `local_llm_config.example.json` 复制；密钥不入库）。

- 调试跳月：游戏内 `F8`，或命令行 `--v12m-month=N`。这两个入口只用于调试，玩家包里撞不到。
- 换分支或长时间没开后，先跑一次 `--headless --import`，避免资源导入未完成造成缺图误报。
- 启动前先看有没有旧后端占着 8077，或已有 Godot 实例在跑；探针用独立的 `--user-data-dir`，不要批量结束本机其他 Godot 进程。

改完必跑（在 `workplace_town/` 下）：

```powershell
python tools/v12m_validate.py                 # 数据校验；--months 1 只查首月，--full 要求全年齐全
python tools/audit_v12m.py                    # 只读体检：节点 / 地点 / 手册 / 旗标消费者交叉引用
python backend/api/selftest.py                # 本地 API 自测

$godot = 'D:\Apps\Godot\Godot_v4.7.2-stable_win64_console.exe'
& $godot --headless --path . res://tests/V12CoreFlowTest.tscn
& $godot --headless --path . res://tests/V12MilestonesTest.tscn
```

校验器当前是 0 个错误、26 个警告，已知三类：群演缺占位图、旗标还没消费者、`report_templates.json` 未建。WARN 不等于坏；新增 WARN 先判断是不是本次改动引入。`audit_v12m.py` 报的是待核对项，退出码仍为 0，逐条看，别当成全部失败。

## 改剧情和数据必须守的规矩

- 严格 JSON：UTF-8、无注释、无尾逗号、无重复键。改完至少过一遍 `python -m json.tool` 或校验器。
- 每个节点、选项、旗标用稳定 ID；显示文案与 ID 分离；玩家可见文字全中文。
- **不预告主线**：提示、目标卡、月历卡不得出现任何月份的剧情标题，事件名只在事件面板当场揭示（校验器会拦）。
- **剧情必须走到才开**：除首月 `E01` 入职说明会外，所有 `main_story` 只在玩家走到 `location` 后开场。不瞬移、不直接弹面板、不自动开场，也不提供“直接开始 / 按 E 直接过去 / 60 秒自动”。只有可选或过场（月末回宿舍睡觉、带巡）保留 30/60 秒兜底。
- **屏末交代**：每屏最后一句写清谁安排的、去哪儿、去做什么。跨区自动补“按 X 的安排，去 Y 吧”；同区换时段补“什么时候接着来”；作者写了 `departNote` 以它为准。同一地点、同一时段的一问一答不补。
- **新道具、新地点先有人递**：必须由场上人物当面交到玩家手里或带过去，再弹解锁卡，不要凭空弹出。
- **手机是通知面板**，不做通用私聊：没有输入框、没有自由文本，唯一“发出去”的是多人活动邀请。`compose` / `input` / `chat` / `freeText` 等字段被校验器禁。
- 选项只来自剧情册与算法册打分卡，不临时加选项、不另造事实。
- 阈值、系数、活动成本、文案变体进 JSON，不写死在 Python 或 GDScript 里；运行时不用大模型算分、选分支或生成未登记事实。

## 代码与提交

- Godot 4.7.x + GDScript；玩家可见文案和注释用中文。
- 不手改 `.uid`、`.import`；保留场景仍引用的 `.import` 元数据。
- 游戏仓当前有大量未提交的 `.import` 本地改动。只 `git add` 自己动过的文件，禁止 `git add -A` / `git add .`；格式化改动和逻辑改动分开提交。
- 结构性改动（搬目录、改数据契约、动 `WorkplaceTown.gd` 主流程）先给方案再动手；破坏性操作先确认，并沿用现有备份惯例（根目录 `_bak_YYYYMMDD_主题/`，已有备份不删不改）。
- 未经明确要求不要 `git commit` / `push`。提交信息沿用现有风格：`feat:` / `fix:` / `docs:` + 一句中文。
- 不提交密钥、数据库、`.godot/`、`artifacts/`、测试截图、构建包或备份目录。

## 已知边界

- 旧 48 个月主线、旧存档、旧报告保持只读；不要顺手重构旧 `promotion.py`，也不要把旧加权口径带进十二个月。
- 开发册 §18 是代码级设计参考；与当前代码不一致时，以代码和校验器为准，并把差异记回开发册，不要两边各留一套。
- 报告模板数据（`report_templates.json`）和部分跨月旗标消费者尚未落地；做报告或结算前先查开发册与校验器，不要假设已完成。
