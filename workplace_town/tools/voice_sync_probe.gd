extends Node

## 只问一件事：本轮改过的台词和选项，游戏里那块面板读出来的是不是新句子。
## 面板就是游戏播剧情用的那个类，数据就是游戏启动时读的那一份 JSON。
## 用法：<godot> --headless --path . res://tools/voice_sync_probe.tscn

const PANEL := preload("res://scripts/StoryEventPanel.gd")

# 节点, 选项号, 屏幕上必须出现的说法
const CHOICES := [
	["E40", "A", "这次先按旧的交，新规则等排期再说。"],
	["E40", "B", "先挑一段低风险的跑两天，把误报和人工时间记下来，再决定换不换。"],
	["M06_DEF1", "A", "方案和兜底那版是我写的，接口是王哥那边接的。"],
	["M12_FEEDBACK", "A", "这次差在哪儿？我下次补。"],
	["M12_FEEDBACK", "B", "我先把记录和交接材料补上，下次再报。"],
	["E50_ownership", "A", "路由和评测是我做的，接口是王哥搭的，口径是小林确认的。"],
	["E50_recovery", "A", "刚才说大了。这是团队的，我负责路由和评测。"],
	["E50_metric_l1", "B", "这个数我没独立核过，不能把估算当实测。"],
	["E50_metric_l3", "B", "我没做反事实验证。"],
	["E50_nextlevel", "A", "我想接跨三条线的活。没独立扛过，先从一条线开始。"],
	["E50_selfreview", "B", "我有时候急，代码也乱，最近拿清单盯着。"],
]

# 节点, 说话人, 屏幕上必须出现的说法（台词里的数字要说约数）
const SAYS := [
	["M06_DEF1", "陈工", "上线两周工单进来四十来张"],
	["E32", "老周", "你那百分之十八，是试点里四十来个人的数"],
	["E32", "老周", "你要写百分之十八"],
]

const KEEP := "把精确数留在材料和旁白里"
const EVIDENCE := [["M11_MATERIAL", "18% 是 40 人试点内的实测结果"], ["M11_MATERIAL", "整体提升 41%"]]


func _ready() -> void:
	var parsed = JSON.parse_string(FileAccess.get_file_as_string("res://data/story/v12m/events.json"))
	var by := {}
	for value in ((parsed as Dictionary).get("nodes", []) as Array):
		by[String((value as Dictionary).get("id", ""))] = value
	var bad := 0
	for row in CHOICES:
		var node: Dictionary = by.get(row[0], {})
		if node.is_empty():
			print("[选] ", row[0], " 这个节点不在表里")
			bad += 1
			continue
		var panel = PANEL.new()
		add_child(panel)
		panel.reduced_motion = true
		panel.present(node)
		var shown := String(panel.call("_choice_text", row[1]))
		var hit := shown.contains(row[2])
		if not hit:
			bad += 1
		print("[选] %-14s %s 屏上读到=%s ｜%s" % [row[0], row[1], _yes(hit), _clip(shown)])
		panel.dismiss()
		panel.queue_free()
	for row in SAYS:
		var node: Dictionary = by.get(row[0], {})
		var panel = PANEL.new()
		add_child(panel)
		panel.reduced_motion = true
		panel.present(node)
		var hit := false
		var shown := ""
		for _i in 40:
			var body = panel.get("_typewriter_rich")
			shown = String(body.text) if body != null else ""
			if shown.contains(row[2]):
				hit = true
				break
			panel.call("_advance")
		panel.dismiss()
		panel.queue_free()
		if not hit:
			bad += 1
		print("[台] %-14s %s 屏上读到=%s ｜%s" % [row[0], row[1], _yes(hit), _clip(shown)])
	for row in EVIDENCE:
		var keep := false
		for beat in (by.get(row[0], {}).get("beats", []) as Array):
			if String(Dictionary(beat).get("text", "")).contains(row[1]):
				keep = true
		if not keep:
			bad += 1
		print("[证] %-14s 精确数还在=%s ｜%s" % [row[0], _yes(keep), row[1]])
	print("[结] 共查 %d 项，不符 %d 项" % [CHOICES.size() + SAYS.size() + EVIDENCE.size(), bad])
	print("VOICE_SYNC_DONE")
	get_tree().quit(0 if bad == 0 else 1)


func _yes(v: bool) -> String:
	return "是" if v else "否"


func _clip(text: String) -> String:
	return text if text.length() <= 52 else text.substr(0, 52) + "…"
