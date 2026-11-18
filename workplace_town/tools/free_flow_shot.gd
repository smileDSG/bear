extends Node

## 自由活动这一套的界面实拍：镇上的门 → 进屋那一叠卡 → 到访确认 → 结果卡。
## 每一步调的都是游戏自己那些函数（不是另画一套），只是由探针驱动、不是手点的。
## 用法：<godot> --path . --resolution 1600x900 res://tools/free_flow_shot.tscn

const OUT_DIR := "res://test_artifacts/free_flow"

var _town: Node
var _done := false


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	_watchdog()
	_town = load("res://Main.tscn").instantiate()
	add_child(_town)
	await get_tree().create_timer(3.0).timeout
	_town.call("debug_jump_to_month", 7)
	await get_tree().create_timer(1.8).timeout
	await _clear_popups()
	var node := _node_by_id("M07_FREE")
	if node.is_empty():
		print("找不到 M07_FREE")
		_finish(1)
		return
	_town.call("runner_open_activity", node)
	await get_tree().create_timer(1.6).timeout
	print("窗口开了：格子=", int(_town.get("_month12_slots_left")),
		" 门=", (_town.get("_month12_place_portals") as Dictionary).size())
	await _shot("01_镇上的门.png")
	# 进 E 区（这一区三条：湖边散步、松风训练谷、草坪运动）
	var zones: Array = _town.get("ZONES")
	var zone_e: Dictionary = {}
	for value in zones:
		if String(Dictionary(value).get("code", "")) == "E":
			zone_e = Dictionary(value)
	_town.call("_enter_month12_interior", zone_e, "")
	await get_tree().create_timer(1.2).timeout
	_town.call("_show_month12_place_list", "E")
	await get_tree().create_timer(1.0).timeout
	await _shot("02_屋里那一叠.png")
	# 点其中一条 → 到访确认页
	var lawn := _place_by_id("m7_lawn")
	var panel: CanvasLayer = _town.get("_month12_place_panel")
	if panel != null and is_instance_valid(panel):
		panel.call("show_confirm", lawn, int(_town.get("_mood")), int(_town.get("_month12_slots_left")))
		await get_tree().create_timer(1.0).timeout
		await _shot("03_到访确认.png")
	# 结这一格 → 结果卡
	_town.call("_settle_month12_activity", lawn)
	await get_tree().create_timer(1.6).timeout
	await _shot("04_结果卡.png")
	print("格子剩=", int(_town.get("_month12_slots_left")),
		" 台账=", JSON.stringify(_town.get("_month_ledger")))
	print("FREE_FLOW_DONE")
	_finish(0)


func _clear_popups() -> void:
	for i in 20:
		var start: Variant = _town.get("_month12_start_panel")
		if start != null and is_instance_valid(start) and bool(start.call("is_open")):
			_town.call("_on_month_start_continued")
			await get_tree().create_timer(0.6).timeout
			break
		await get_tree().create_timer(0.3).timeout
	var story: CanvasLayer = _town.get("_story_event_panel")
	if story != null and is_instance_valid(story) and bool(story.call("is_open")):
		story.call("dismiss")
		await get_tree().create_timer(0.6).timeout


func _node_by_id(id: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/story/v12m/events.json"))
	for value in ((parsed as Dictionary).get("nodes", []) as Array):
		if String(Dictionary(value).get("id", "")) == id:
			return Dictionary(value)
	return {}


func _place_by_id(id: String) -> Dictionary:
	for value in (_town.get("_month12_places") as Array):
		if String(Dictionary(value).get("id", "")) == id:
			return Dictionary(value)
	return {}


func _shot(file_name: String) -> void:
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(OUT_DIR + "/" + file_name)


func _finish(code: int) -> void:
	_done = true
	get_tree().quit(code)


func _watchdog() -> void:
	await get_tree().create_timer(300.0).timeout
	if _done:
		return
	print("WATCHDOG forced quit")
	get_tree().quit(1)
