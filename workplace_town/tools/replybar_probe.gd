extends Node

## 收件箱回完一句之后，回复栏该只剩一颗"收起手机"，不再留一颗点不动的旧回复。
## 数据用第 1 月陈工那批真消息（走流程自然投递，不手写）。
## 用法：<godot> --path <proj> --resolution 1920x1080 res://tools/replybar_probe.tscn

const SHOT_DIR := "res://test_artifacts/replybar"

var _town: Node


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(SHOT_DIR))
	_town = load("res://Main.tscn").instantiate()
	add_child(_town)
	await _wait(3.6)
	_town.call("debug_jump_to_month", 1, "A")
	await _wait(2.6)
	var start_panel = _town.get("_month12_start_panel")
	if start_panel != null and is_instance_valid(start_panel) and bool(start_panel.call("is_open")):
		start_panel.emit_signal("continued")
	await _wait(2.4)
	# 把这批真消息按正式投递口送进去（M01_PHONE_1 带着"收到，我先装环境"这颗回复）
	var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/story/v12m/events.json"))
	for value in ((raw as Dictionary).get("nodes", []) if raw is Dictionary else []):
		if String(Dictionary(value).get("id", "")) == "M01_PHONE_1":
			_town.call("runner_deliver_phone", Dictionary(value))
			break
	await _wait(0.8)
	# 面板是懒建的；会话列表用城镇自己那份（真消息），不在这里手写。
	var panel = _town.call("_ensure_month_phone_panel")
	if panel == null:
		print("REPLY 没有手机面板")
		get_tree().quit(1)
		return
	panel.set("conversations", _town.call("_build_phone_conversations"))
	panel.call("open_phone", true)
	await _wait(0.9)
	# 进第一条会话
	var convs: Array = panel.get("conversations")
	if convs.is_empty():
		print("REPLY 收件箱是空的（这批消息还没投递）")
		get_tree().quit(1)
		return
	var first := Dictionary(convs[0])
	print("REPLY 会话：", String(first.get("name", "")), " 回复项=", (first.get("reply_options", []) as Array).size())
	panel.call("_open_conversation", String(first.get("id", "")))
	await _wait(0.7)
	await _shot("01_还没回")
	var bar: Control = panel.get("_reply_bar")
	var before := _bar_texts(bar)
	print("REPLY 回之前按钮：", before)
	# 按第一颗回复
	for child in bar.get_children():
		if child is Button and String((child as Button).name).begins_with("Reply_"):
			(child as Button).emit_signal("pressed")
			break
	await _wait(1.2)
	await _shot("02_回完之后")
	print("REPLY 回之后按钮：", _bar_texts(bar))
	print("REPLY_DONE")
	get_tree().quit(0)


func _bar_texts(bar: Control) -> String:
	if bar == null or not is_instance_valid(bar):
		return "无回复栏"
	var out: Array = []
	for child in bar.get_children():
		if child is Button:
			out.append("%s%s" % [String((child as Button).text), "（灰）" if (child as Button).disabled else ""])
	return " / ".join(out) if not out.is_empty() else "空的"


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _shot(shot_name: String) -> void:
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	print("SHOT ", shot_name, " saved=", image.save_png(ProjectSettings.globalize_path(SHOT_DIR + "/" + shot_name + ".png")))
