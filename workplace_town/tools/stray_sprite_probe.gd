extends Node

## 手机一开，镇子上空飘着个 512 的大熊。这里把"谁能画出它"找出来：
## 遍历全场景，凡是贴图路径里带 chen_gong 的节点，打印它的祖先链和屏幕位置。
## 用法：<godot> --path <proj> --resolution 1920x1080 res://tools/stray_sprite_probe.tscn

var _town: Node


func _ready() -> void:
	_town = load("res://Main.tscn").instantiate()
	add_child(_town)
	await _wait(3.6)
	var panel = _town.call("_ensure_month_phone_panel")
	panel.set("conversations", _town.call("_build_phone_conversations"))
	panel.call("open_phone", true)
	await _wait(1.0)
	_dump(get_tree().root, 0)
	print("STRAY_DONE")
	get_tree().quit(0)


func _dump(node: Node, depth: int) -> void:
	if depth > 24:
		return
	var tex: Texture2D = null
	if node is TextureRect:
		tex = (node as TextureRect).texture
	elif node is Sprite2D:
		tex = (node as Sprite2D).texture
	elif node is Button:
		return
	if tex != null:
		var path := ""
		if tex is AtlasTexture:
			path = String(((tex as AtlasTexture).atlas.resource_path if (tex as AtlasTexture).atlas != null else ""))
		else:
			path = String(tex.resource_path)
		if tex != null and (tex.get_width() >= 200 or path.contains("chen_gong")):
			if node is Sprite2D:
				var sp := node as Sprite2D
				if sp is PaperDoll64Sprite:
					print("STRAY 纸娃娃 loadout=%s direct=%s row=%d frame=%d" % [
						String(sp.get("_current_loadout_id")), bool(sp.get("_direct_frame_mode")),
						int(sp.get("_direction_row")), int(sp.get("_frame_sequence_index"))])
				print("STRAY Sprite2D %s | 全局=%s 缩放=%s 贴图=%s | 父类型=%s | 祖先=%s" % [
					sp.get_path(), str(sp.global_position), str(sp.scale),
					str(tex.get_size()) if tex != null else "-",
					sp.get_parent().get_class(), _chain(sp)])
			else:
				var control := node as Control
				print("STRAY Control %s | 屏幕=%s 屏幕尺寸=%s | 祖先=%s" % [
					node.get_path(), str(control.get_global_rect()), str(control.size), _chain(node)])
	for child in node.get_children():
		_dump(child, depth + 1)


func _chain(node: Node) -> String:
	var parts: Array = []
	var cur := node.get_parent()
	var guard := 0
	while cur != null and guard < 6:
		parts.append(String(cur.name))
		cur = cur.get_parent()
		guard += 1
	return " < ".join(parts)


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout
