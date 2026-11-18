extends Node

## 报告页实拍：把后端真跑出来的那份报告（test_artifacts/report_dump.json，
## 由自测同一条路径生成：建会话→走完全程→出片）喂给报告页，看它长什么样。
## 用法：<godot> --path <proj> --resolution 1920x1080 res://tools/report_shot.tscn

const SHOT_DIR := "res://test_artifacts/report_shot"
const DUMP := "res://test_artifacts/report_dump.json"
const PANEL := preload("res://scripts/ReportPanel.gd")

var _panel


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(SHOT_DIR))
	var bg := ColorRect.new()
	bg.color = Color("241d16")
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DUMP))
	if not (parsed is Dictionary):
		print("REPORT 读不到报告数据")
		get_tree().quit(1)
		return
	_panel = PANEL.new()
	add_child(_panel)
	await get_tree().process_frame
	_panel.visible = true
	_panel.call("render", parsed as Dictionary)
	await _wait(0.8)
	await _shot("01_top")
	var scroll: Variant = _find_scroll(_panel)
	if scroll != null:
		scroll.scroll_vertical = int(scroll.get_v_scroll_bar().max_value)
		await _wait(0.4)
		await _shot("02_bottom")
	print("REPORT_DONE 决策数=", int((parsed as Dictionary).get("decisionCount", 0)))
	get_tree().quit(0)


func _find_scroll(node: Node) -> Variant:
	if node is ScrollContainer:
		return node
	for child in node.get_children():
		var hit: Variant = _find_scroll(child)
		if hit != null:
			return hit
	return null


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _shot(shot_name: String) -> void:
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	print("SHOT ", shot_name, " saved=", image.save_png(ProjectSettings.globalize_path(SHOT_DIR + "/" + shot_name + ".png")))
