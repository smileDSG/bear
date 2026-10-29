from copy import deepcopy
from pathlib import Path

from docx import Document


SOURCE = Path("剧情册/历史修订稿/十二个月剧情流程_逻辑修订稿.docx")
OUTPUT = Path("剧情册/剧情册.docx")
doc = Document(SOURCE)


def replace_prefix(prefix, value, occurrence=0):
    matches = [p for p in doc.paragraphs if p.text.startswith(prefix)]
    if len(matches) <= occurrence:
        raise RuntimeError(f"Paragraph not found: {prefix}")
    matches[occurrence].text = value
    return matches[occurrence]


def insert_after(anchor, lines):
    previous = anchor._p
    for line in lines:
        new_p = deepcopy(anchor._p)
        for child in list(new_p):
            if child.tag.endswith("}r") or child.tag.endswith("}hyperlink"):
                new_p.remove(child)
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        run = OxmlElement("w:r")
        text = OxmlElement("w:t")
        text.text = line
        run.append(text)
        new_p.append(run)
        previous.addnext(new_p)
        previous = new_p
    return previous


def update_cells(old, new):
    changed = 0
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if old in cell.text:
                    cell.text = cell.text.replace(old, new)
                    changed += 1
    return changed


# Keep the supplied flow's structure while carrying forward the later story revisions.
replace_prefix("职场小镇十二个月剧情流程逻辑修订稿", "职场小镇十二个月剧情流程融合稿")
replace_prefix(
    "完整稿涵盖十二个月",
    "完整稿涵盖十二个月的玩家可见剧情、逐句对白、选项后果、属性变化、手机时机、解锁条件与埋点。以基础剧情流程为主线，结合分月设计、剧情修订、报告算法与开发口径统一关键节点。版本日期：2026年10月29日。",
)
replace_prefix(
    "评估：第六月是转正评估",
    "评估：第六月是转正评估，结论为通过、延期复核或未转正；延期者在第七月完成一次补充复核，未转正者完成交接后结束在岗主线。第十二月是年度晋升评估。S/O/N/D用于汇总可核验证据，但不以隐藏总分机械决定提名；提名和晋升结合岗位要求、材料和现场答辩。行动点、H及身体负担不计入晋升分。",
)

# M2: all E04 routes lead to the required archive visit and a concrete return task.
replace_prefix(
    "王哥：编排层有个小模块要选实现方式。",
    "王哥：编排层有个小模块要选实现方式。自研做一份，开源改一份，先把依赖和退路画清楚。两年前同类事故只写了“加监控”，没留下可执行的回滚办法。这周要查清当年的记录，再把这次方案的退路补完整。",
)
replace_prefix(
    "王哥：周三上午，A 区评审室。",
    "王哥：周三上午，A 区评审室。先把两条路线带过去。评审后去树影书院二楼核对旧事故单，再回工位补方案。",
)
replace_prefix(
    "B E04 技术选型",
    "B E04 技术选型 自研还是开源；评审后必须完成 M02_LIBRARY，之后才能结束本月。书院任务不消耗自由活动行动点。",
)
replace_prefix(
    "陈工：别说哪条听起来高级。",
    "陈工：别说哪条听起来高级。告诉我，哪条出了问题更好收拾。两年前那次事故单只写了“加监控”，没有写清怎么退回上一版。评审后去树影书院二楼查原始回滚记录，再把查到的结论补进方案。",
)
replace_prefix(
    "旁白：笔在你手里。你要用哪种方式把这件事做完？",
    "旁白：先选一条验证路线。散会后还要去树影书院二楼核对旧事故的回滚记录，回 B 区工位把退路补进方案。你要怎么开始？",
)
replace_prefix(
    "C 先问王哥以前踩过哪些坑",
    "C 先问王哥以前踩过哪些坑，再自己做判断  把王哥的口述当线索，不当作旧事故单的替代；之后仍要去书院核对原记录。",
)
e04_result = next(p for p in doc.paragraphs if p.text.startswith("属性变化：A：S +2"))
insert_after(
    e04_result,
    [
        "B1 M02_LIBRARY 翻查旧事故单（必玩剧情节点，树影书院二楼；不占 AP）",
        "旁白：你照陈工给的线索来到树影书院二楼。来这里是要查清两年前那次故障有没有可执行的回滚步骤。旧事故单的处理方式只有“加监控”，回滚记录和当班负责人一栏都是空的。",
        "旁白：你把原记录拍下来，圈出缺少的回滚步骤。口述、当前验证和旧记录分开记，不能把旧事故的结论直接套到这次方案上。",
        "旁白：管理员提醒闭馆。你带着记录回 B 区工位，把适用的回滚步骤、触发条件和负责人补进方案；没有证据的部分标成待确认。",
        "【结果】E04 A/B/C 均进入本节点。完成 M02_LIBRARY 并回到 B 区提交修订方案后，才开放 E03 与月末收尾。记录 m02_library_rollback_checked；不因未访问书院给负面评价。",
    ],
)
replace_prefix(
    "第七天 十一点 旁白：你手上有能带去评审的东西了。",
    "第七天 十一点 旁白：你已把书院查到的旧记录与本周验证分开，方案里补上了能执行的回滚步骤。你手上有能带去评审的东西了。",
)
replace_prefix(
    "【界面】 第三张卡末尾出现“打开提交页面”；",
    "【界面】 第三张卡末尾出现“打开提交页面”；",
)
replace_prefix(
    "F 月末王哥消息与跨月",
    "F 月末王哥消息与跨月  完成 E04、M02_LIBRARY 与 E03 后出现“结束这个月”；消息阅读不设为门槛。",
)

# M3: add the mandatory post-meeting handoff choice as an independent N evidence point.
replace_prefix("D 散会 王哥交代手册与会后清单", "D E10b 会后清单（强制三选一，不占 AP、不改 S/O/N/D）")
replace_prefix("王哥：会后把三样东西写出来发我：", "王哥：会后把三样东西写出来发我：哪些还没定，谁负责，什么时候再确认。")
replace_prefix("王哥：周四之前发我。", "王哥：周四之前发我。这个清单不是替你补会议结论，是让大家知道下一步由谁接。")
handoff_prompt = next(p for p in doc.paragraphs if p.text.startswith("王哥：周四之前发我。"))
insert_after(
    handoff_prompt,
    [
        "玩家选择：必须选择一项，提交后本月不重选；只生成一条 N 协作证据，不改变数值属性。",
        "A｜发到组内记录：逐项写清待定项、责任人和下次确认时间；历史问题次数若未查实，明确标为待核。N 证据锚点 4，旗标 m03_e10_handoff_complete。",
        "B｜只私发王哥：写出待定项和负责人，但没有把下次确认时间同步到组内。N 证据锚点 2，旗标 m03_e10_handoff_partial。",
        "C｜先不整理：清单留空，等有人追问再补。N 证据锚点 1，旗标 m03_e10_handoff_blank。",
        "【记录】E10b 为必玩观察点；记录 choice_id、清单是否覆盖三项、artifact_id、N 锚点和旗标。不得把该证据重复计入同一维度。",
    ],
)
replace_prefix(
    "F 桥段 回到工位补会后记录",
    "F 桥段 回到工位核对历史问题记录  自由安排后无条件触发；不检查好感度，不要求碰到任何人。",
)
replace_prefix(
    "旁白：回到工位。王哥要的三样东西里，",
    "旁白：回到工位。无论你刚才如何整理清单，“这类问题以前出过几次”都还没有来源可核。",
)
replace_prefix(
    "旁白：你把会后清单里的那一格空着，",
    "旁白：你把“历史问题次数”标成待核，打开组里的《常见问题》文档，准备补上来源。",
)
update_cells(
    "E10结束后解锁手册第二章",
    "E10结束后解锁手册第二章；E10b强制三选一并产出一条N证据；开放2个自由活动格。",
)

# M6: make the confirmed / deferred / not-confirmed bands explicit, including the approved near-miss band.
m6_rules = next(p for p in doc.paragraphs if p.text.startswith("属性口径：正式维度统一为 S/O/N/D"))
m6_rules.text = (
    "判定口径（不向玩家展示隐藏总分）：直接通过需四维证据均充分、每维≥3、总分≥14/16，覆盖一次受阻/风险情境及后续，且没有未纠正的重大隐瞒；状态记为 confirmed，职级不变。延期复核适用于总分11–13且至少三维≥3、其余≥2且无未纠正重大隐瞒；或总分≥14、恰好一维=2且其余三维≥3；或有维度证据不足但没有任何维度<2。延期状态记为 deferred，进入第七月一次新样例复核。未转正适用于任一维<2、两维及以上<3且不符合延期条件，或总分<11；状态记为 not_confirmed，第七月完成交接后结束在岗主线。证据不足不等于0；答辩中的个人目标、困难披露、便签选择不直接加减转正分。"
)

# M7: reveal each M6 state, run the deferred review in month 7, and close the employment arc after handoff when needed.
replace_prefix("A 月初｜答辩结果落地（通过 / 延期两版", "A 月初｜答辩结果落地（三态，约 1 分钟）")
replace_prefix("王哥：这次先延期。不是让你把整半年重来，HR 说下个月补一次复核。", "王哥：这次先延期。不是让你把整半年重来，HR 通知这月补一次复核。")
replace_prefix(
    "【3.2 时间】本局第六月是转正评估",
    "【3.2 时间】本局第六月是转正评估，第七月是延期后的补充复核，第十二月是年度晋升评估；具体时间以 HR 通知为准。",
)
replace_prefix("【延期版状态】probation_status=deferred", "【延期复核版状态】probation_status=deferred")
replace_prefix(
    "【延期版】旁白：系统状态更新了：“延期转正”。",
    "【延期版】旁白：系统状态更新为“延期复核”。下面附了需要补充的两项材料和复核时间。",
)
deferred_state = next(p for p in doc.paragraphs if p.text.startswith("【延期复核版状态】probation_status=deferred"))
insert_after(
    deferred_state,
    [
        "【未转正版】旁白：系统状态更新为“未转正”。HR 把一份交接清单放在桌上，没有出现处分、开除或人格评价。",
        "王哥：先把你手上的模块交清楚。哪些已经完成、哪些还没确认、下一步谁接，都写在这张表里。",
        "旁白：你和接手同事逐项对过文档、待办和访问权限。交接完成后，转正主线在这里结束；不再进入 E19、E23 或后续在岗剧情。年度记录只总结已发生的事，并给出发展建议。",
        "【未转正版状态】probation_status=not_confirmed；完成交接后写入 employment_arc=ended；不开放第八至第十二月在岗主线。",
    ],
)
replace_prefix("B 延期分支｜王哥的反馈纸", "B 延期分支｜王哥的反馈纸与复核准备（通过版不出现）")
feedback_heading = next(p for p in doc.paragraphs if p.text.startswith("B 延期分支｜王哥的反馈纸与复核准备"))
feedback_index = next(i for i, p in enumerate(doc.paragraphs) if p.text.startswith("B 延期分支｜王哥的反馈纸与复核准备"))
feedback_choice = next(
    p for p in doc.paragraphs[feedback_index + 1:]
    if p.text.strip() == "玩家选择："
)
feedback_choice.text = "玩家选择：现在打开反馈纸 / 先收起来稍后再看；不改判定结果。"
insert_after(
    feedback_choice,
    [
        "B1 第七月补充复核（只对 M6 deferred 开放一次）",
        "【界面】按反馈纸列出的短板或证据不足维度加载一项新的岗位样例，不重播原题、不重复刷分：S 为不完整日志的根因判断；O 为范围变化中的限期交付；N 为模块交接并写清待定项、负责人和确认时间；D 为发现不实记录后用可核验材料纠正。",
        "【判定】短板维度≥3、总分≥13/16且没有任何维度<2，复核通过并更新 probation_status=confirmed；职级不变。否则记 not_confirmed，先完成交接，再结束在岗主线。",
    ],
)
replace_prefix(
    "【触发】客户 Demo 后，相关生产规则已按流程回滚",
    "【触发】仅 probation_status=confirmed 或第七月复核通过后进入 E19；M6 未转正或第七月复核未通过者已完成交接并结束在岗主线。客户 Demo 后，相关生产规则已按流程回滚",
)

# M8 no longer owns the M7 checkpoint.
replace_prefix(
    "【条件节点｜仅第七个月结果为“延期转正”】日程里另有按 HR 通知日期触发的“本月补充复核”。",
    "【流程边界】转正延期者已在第七月完成一次补充复核；通过者按正常主线进入本月。未通过者已完成交接并结束在岗主线，不会进入本月。",
)
replace_prefix(
    "【可点动作】“提交现有材料”或“暂不提交”。",
    "【复核边界】第八月不重复开放转正复核，不重播 M7 样例，也不改写已经确认的转正状态。",
)

# Keep overview and cross-month references aligned with the story.
update_cells("技术选型E04与AI代码署名E03", "技术选型E04、必玩书院旧事故核查M02_LIBRARY与AI代码署名E03")
update_cells("客户承诺E10与团队知识回响E12", "客户承诺E10、强制会后清单E10b与团队知识回响E12")
update_cells("第七月月初读取通过或延期状态", "第七月月初读取通过、延期或未转正状态；延期者当月复核，未转正者交接后结束在岗主线")
update_cells("E10结束后解锁手册第二章；E10b强制三选一并产出一条N证据；开放2个自由活动格。；开放2个自由活动格。", "E10结束后解锁手册第二章；E10b强制三选一并产出一条N证据；开放2个自由活动格。")
update_cells("延期转正者可按HR通知提交补充材料；本月无自由活动。", "M6直接通过或第七月复核通过者进入本月在岗主线；未转正者已交接结案；本月无自由活动。")
update_cells("第6月 → 第7月", "第6月 → 第7月")
update_cells("转正结果与三张便签进入第七月；延期只触发本月补充复核，不改变职级。", "转正三态与三张便签进入第七月；延期者当月复核且不改变职级，未转正者完成交接后结束在岗主线。")

# Add E10b to the scoring and telemetry tables.
for table in doc.tables:
    table_text = " ".join(cell.text for row in table.rows for cell in row.cells)
    if "E10" in table_text and "truth_with_fallback" in table_text and len(table.columns) >= 4:
        row = table.add_row()
        values = [
            "E10b 会后清单",
            "A 完整组内清单 / B 私发部分清单 / C 留空",
            "强制选择；不耗 AP，不改 S/O/N/D",
            "m03_e10_handoff_complete / partial / blank；N 锚点 4 / 2 / 1",
        ]
        for i, value in enumerate(values[:len(row.cells)]):
            row.cells[i].text = value
        break

for table in doc.tables:
    table_text = " ".join(cell.text for row in table.rows for cell in row.cells)
    if "m02_e04_choice" in table_text and "m02_library_rollback_checked" not in table_text:
        row = table.add_row()
        values = [
            "M02_LIBRARY 书院旧档核查",
            "必玩节点；核对回滚记录并返回 B 区补方案，不耗 AP。",
            "m02_library_rollback_checked：完成状态、artifact_id；不记录档案正文。",
        ]
        for i, value in enumerate(values[:len(row.cells)]):
            row.cells[i].text = value
        break

for table in doc.tables:
    table_text = " ".join(cell.text for row in table.rows for cell in row.cells)
    if "m03_e10_choice" in table_text and "m03_e10b_handoff_choice" not in table_text:
        row = table.add_row()
        values = [
            "E10b 会后清单",
            "强制三选一；记录完整度与证据锚点，不采集清单正文。",
            "m03_e10b_handoff_choice：choice_id、artifact_id、N_anchor、handoff_flag。",
        ]
        for i, value in enumerate(values[:len(row.cells)]):
            row.cells[i].text = value
        break

doc.core_properties.title = "职场小镇十二个月剧情流程融合稿"
doc.core_properties.subject = "十二个月剧情流程与后续设计整合"
doc.save(OUTPUT)
print(OUTPUT.resolve())
