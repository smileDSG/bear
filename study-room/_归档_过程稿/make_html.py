# -*- coding: utf-8 -*-
"""把两份 md 定稿转成手机浏览器能直接打开的单文件 HTML，图片内嵌。"""
import os
import base64
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))

CSS = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body{font-family:"Microsoft YaHei",-apple-system,"PingFang SC",sans-serif;
       max-width:820px;margin:0 auto;padding:22px 18px;color:#111;
       line-height:1.75;font-size:16px;background:#fff;}
  h1{font-size:24px;border-bottom:2px solid #333;padding-bottom:10px;margin-top:8px;}
  h2{font-size:20px;margin-top:30px;border-bottom:1px solid #ddd;padding-bottom:6px;}
  h3{font-size:17px;margin-top:22px;}
  table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px;}
  th,td{border:1px solid #bbb;padding:7px 9px;text-align:left;vertical-align:top;}
  th{background:#f2f2f2;}
  blockquote{border-left:4px solid #999;margin:14px 0;padding:6px 14px;color:#444;background:#fafafa;}
  img{max-width:100%;height:auto;display:block;margin:18px auto;border:1px solid #ddd;}
  code{background:#f4f4f4;padding:1px 5px;border-radius:3px;font-size:14px;}
  pre{background:#f6f6f6;padding:12px;overflow-x:auto;border:1px solid #ddd;border-radius:5px;}
  pre code{background:none;padding:0;}
  hr{border:none;border-top:1px solid #ddd;margin:26px 0;}
  li{margin:5px 0;}
</style>
"""


def md_to_html(name):
    with open(os.path.join(HERE, name + ".md"), "r", encoding="utf-8") as fp:
        text = fp.read()
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])

    # 内嵌所有本地 png（主视角图 + 俯视图）
    import re as _re
    for img_name in set(_re.findall(r"src=\"([^\"]+\.png)\"", body)):
        img_path = os.path.join(HERE, img_name)
        if os.path.exists(img_path):
            with open(img_path, "rb") as fp:
                data = base64.b64encode(fp.read()).decode()
            body = body.replace(img_name, "data:image/png;base64," + data)

    html = ("<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
            + CSS + "<title>" + name + "</title></head><body>" + body
            + "</body></html>")
    out = os.path.join(HERE, name + ".html")
    with open(out, "w", encoding="utf-8") as fp:
        fp.write(html)
    print("HTML saved:", out, len(html), "chars")
    return out


if __name__ == "__main__":
    md_to_html("小熊镇自习室-场景与体验设计")
    print("ALL DONE")
