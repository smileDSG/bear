extends Node

## 册子与游戏数据的双向对账：
## 正向——《剧情册》里每一句旁白 / 台词，游戏数据里有没有同一件事；
## 反向——游戏数据里的文本，册子有没有跟上。
## 判据：把一句话按标点拆成小段，取最长那一段（去掉标点和空格后 >=6 字），
##       这一段在对面找不到，就算「对面没有这句话」。
## 用法：<godot> --headless --path . res://tools/book_data_diff.tscn -- --book <册子纯文本> [-- --out <报告目录>]
## 册子要先导成纯文本（运行时装不了 docx）：
##   python -c "import docx;io=open('C:/tmp/jgc.txt','w',encoding='utf-8');[io.write(p.text+'\n') for p in docx.Document('剧情册.docx').paragraphs]"

const SEP := "。！？；：，、「」『』（）()《》…—-\t\r\n ·\"'　"
const SPEAKERS := ["旁白", "王哥", "陈工", "老周", "小赵", "小林", "客户", "方经理", "许棠",
	"大领导", "记录评委", "HRBP", "孙哥", "跨部门评委", "组长", "管理员", "阿姨", "主管",
	"技术委员会负责人"]
# 这些键不是玩家会看见的话
const SKIP_KEYS := ["id", "flags", "when", "speaker", "type", "nodeType", "locationId", "timeBand",
	"phase", "reportUse", "zone", "pos", "card", "at", "zoneId", "landmark", "shots", "expression",
	"stateDelta", "riskDelta", "apCost", "setsFlags", "unlock", "month", "order", "required",
	"durationMinutes", "situation", "autoComplete", "name", "style", "node", "title", "location"]

var _book_raw := ""
var _book_norm := ""
var _game_lines: Array = []
var _out_dir := "user://book_data_diff"


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var book_path := "C:/tmp/jgc.txt"
	for i in args.size():
		if args[i] == "--book" and i + 1 < args.size():
			book_path = args[i + 1]
		if args[i] == "--out" and i + 1 < args.size():
			_out_dir = args[i + 1]
	_book_raw = FileAccess.get_file_as_string(book_path)
	if _book_raw.is_empty():
		print("[错] 读不到册子文本：", book_path)
		print("BOOK_DIFF_ERROR")
		get_tree().quit(2)
		return
	_book_norm = _norm(_book_raw)
	var parsed = JSON.parse_string(FileAccess.get_file_as_string("res://data/story/v12m/events.json"))
	for node in ((parsed as Dictionary).get("nodes", []) as Array):
		_collect(Dictionary(node), String(Dictionary(node).get("id", "?")), int(Dictionary(node).get("month", 0)))
	var game_blob := ""
	for row in _game_lines:
		game_blob += _norm(String(Dictionary(row).get("text", ""))) + "|"
	var forward := _book_missing(game_blob)
	var backward := _game_missing()
	var report_text := _render(forward, backward)
	DirAccess.make_dir_recursive_absolute(_out_dir)
	var handle := FileAccess.open(_out_dir + "/report.txt", FileAccess.WRITE)
	if handle == null:
		print("[警] 报告写不出去：", _out_dir, " 错误码=", FileAccess.get_open_error())
	elif handle.store_string(report_text) != OK:
		print("[警] 报告写入失败，错误码=", FileAccess.get_open_error())
	handle.close()
	var check := FileAccess.get_file_as_string(_out_dir + "/report.txt")
	print("[写] 报告 %d 字，回读 %d 字" % [report_text.length(), check.length()])
	print("[料] 册子标点后 %d 字 · 游戏文本 %d 条" % [_book_norm.length(), _game_lines.size()])
	print("[正向] 册子里有、游戏里查不到同一件事的说话行：%d 句" % forward.size())
	print("[反向] 游戏里有、册子里查不到的文本：%d 条" % backward.size())
	print("[报告] %s/report.txt" % _out_dir)
	print("BOOK_DIFF_DONE")
	get_tree().quit(0)


func _collect(obj: Variant, node_id: String, mon: int) -> void:
	if typeof(obj) == TYPE_DICTIONARY:
		for key in (obj as Dictionary).keys():
			if key in SKIP_KEYS:
				continue
			_collect((obj as Dictionary)[key], node_id, mon)
	elif typeof(obj) == TYPE_ARRAY:
		for item in (obj as Array):
			_collect(item, node_id, mon)
	elif typeof(obj) == TYPE_STRING:
		if _norm(String(obj)).length() < 6:
			return
		if not _has_cjk(String(obj)):
			return
		_game_lines.append({"node": node_id, "month": mon, "text": String(obj)})


func _has_cjk(text: String) -> bool:
	for i in text.length():
		var v := text.unicode_at(i)
		if v >= 0x4E00 and v <= 0x9FFF:
			return true
	return false


## 去掉标点与空白，只留汉字、数字、字母
func _norm(text: String) -> String:
	var parts: PackedStringArray = []
	for c in text:
		var v := c.unicode_at(0)
		var keep_char := (v >= 0x4E00 and v <= 0x9FFF) or (v >= 48 and v <= 57) or (v >= 65 and v <= 90) or (v >= 97 and v <= 122)
		if keep_char:
			parts.append(c)
	return "".join(parts)


## 按标点切成小段，只留去掉标点后 >=6 字的段
func _pieces(text: String) -> Array:
	var chunks: PackedStringArray = []
	var buf := ""
	for c in text:
		if SEP.contains(c):
			if not buf.is_empty():
				chunks.append(buf)
				buf = ""
			continue
		buf += c
	if not buf.is_empty():
		chunks.append(buf)
	var pieces: Array = []
	for raw in chunks:
		var n := _norm(String(raw))
		if n.length() >= 6:
			pieces.append(n)
	return pieces


func _longest(text: String) -> String:
	var best := ""
	for p in _pieces(text):
		if String(p).length() > best.length():
			best = String(p)
	return best


func _speaker_of(line: String) -> bool:
	var i := line.find("：")
	if i < 0:
		i = line.find(":")
	if i <= 0 or i > 12:
		return false
	return line.substr(0, i) in SPEAKERS


func _strip_speaker(s: String) -> String:
	var i := s.find("：")
	if i < 0:
		i = s.find(":")
	return s.substr(i + 1) if i >= 0 else s


func _book_missing(game_blob: String) -> Array:
	var missing: Array = []
	for line in _book_raw.split("\n"):
		var s := line.strip_edges()
		if s.is_empty() or not _speaker_of(s):
			continue
		var longest := _longest(_strip_speaker(s))
		if longest.is_empty():
			continue
		if not game_blob.contains(longest):
			missing.append(s)
	return missing


func _game_missing() -> Array:
	var out: Array = []
	for row in _game_lines:
		var longest := _longest(String(Dictionary(row).get("text", "")))
		if longest.is_empty():
			continue
		if not _book_norm.contains(longest):
			out.append(row)
	return out


func _render(forward: Array, backward: Array) -> String:
	var lines: Array[String] = []
	lines.append("《剧情册》↔ 游戏数据 双向对账（判据：最长小段能不能在对面找到）")
	lines.append("")
	lines.append("== 一、册子里有、游戏里查不到的说话行（%d 句）==" % forward.size())
	var idx := 0
	for s in forward:
		idx += 1
		lines.append("%02d  %s" % [idx, s])
	lines.append("")
	lines.append("== 二、游戏里有、册子里查不到的文本（%d 条）==" % backward.size())
	idx = 0
	for row in backward:
		idx += 1
		lines.append("%02d  [%s 第%s月] %s" % [idx, String(Dictionary(row).get("node", "")),
			String(Dictionary(row).get("month", "?")), String(Dictionary(row).get("text", ""))])
	return "\n".join(lines) + "\n"
