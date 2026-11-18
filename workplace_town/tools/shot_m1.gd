extends Control
## 出四张实拍：第一个月说明会两句新台词 / 周会王哥两句 / 周会选择页。
## 用法：<godot> --path . --resolution 1600x900 --audio-driver Dummy res://tools/shot_m1.tscn -- --dir <out>

var _dir := "user://m1shot"
var _town: Node
var _panel
var _by := {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var args := OS.get_cmdline_user_args()
	for i in args.size():
		if args[i] == "--dir" and i + 1 < args.size():
			_dir = args[i + 1]
	DirAccess.make_dir_recursive_absolute(_dir)
	var raw = JSON.parse_string(FileAccess.get_file_as_string("res://data/story/v12m/events.json"))
	for value in ((raw as Dictionary).get("nodes", []) as Array):
		_by[String((value as Dictionary).get("id", ""))] = value
	_town = load("res://Main.tscn").instantiate()
	add_child(_town)
	# 兜底：任何一步等不到就自己退，别把窗口挂在那儿。
	get_tree().create_timer(60.0).timeout.connect(func(): get_tree().quit())
	await get_tree().create_timer(2.8).timeout
	_panel = _town.get("_story_event_panel")
	_panel.reduced_motion = true
	var start = _town.get("_month12_start_panel")
	if start != null and bool(start.call("is_open")):
		_town.call("_on_month_start_continued")
		await get_tree().create_timer(1.0).timeout
	if bool(_panel.call("is_open")):
		_panel.call("dismiss")
	_panel.visible = false
	var card = _town.get("_hud_button_tutorial")
	if card != null and bool(card.call("is_open")):
		card.call("_on_open_pressed")
		await get_tree().create_timer(0.3).timeout
	# 探针误开的档案页顺手关掉
	var ui = _town.get("_town_ui_v2")
	if ui != null and bool(ui.call("is_open")):
		ui.call("close_view")
		await get_tree().create_timer(0.3).timeout
	await _show("E01", "两次评估", "01_说明会_两次评估")
	await _show("E01", "会看你们的", "02_说明会_看什么")
	await _show("E01", "转正过了也不代表", "03_说明会_转正不等于晋升")
	await _show("E02", "你整理的吧", "04_周会_王哥提醒")
	await _show("E02", "纪要我看过了", "05_周会_王哥点破")
	print("[m1] 完成 -> ", _dir)
	get_tree().quit()


func _show(node_id: String, needle: String, name: String) -> void:
	_panel.visible = true
	_panel.call("present", _town.call("_runner_story_data", _by.get(node_id, {})))
	await get_tree().create_timer(1.6).timeout
	for i in 12:
		var stage := String(_panel.get("_stage"))
		if needle == "__choice__":
			if stage == "choice" or stage == "choices":
				break
		else:
			var beats: Array = _panel.get("_beats")
			var idx := int(_panel.get("_beat_index"))
			if idx >= 0 and idx < beats.size() and needle in String((beats[idx] as Dictionary).get("text", "")):
				break
		_panel.call("_advance")
		await get_tree().create_timer(0.4).timeout
	await get_tree().create_timer(0.5).timeout
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [_dir, name])
	print("[m1] ", name)
	if bool(_panel.call("is_open")):
		_panel.call("dismiss")
	_panel.visible = false
	await get_tree().create_timer(0.4).timeout
