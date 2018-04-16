#!/usr/bin/python3
# -*- coding: utf-8 -*-
from xml.etree import ElementTree
def elem2html(elem):  # ElementオブジェクトをHTMLにして返す。
	html = ElementTree.tostring(elem, encoding="unicode", method="html")
	emptytags = "source", "track", "wbr", "embed"  # 終了タグがついてくる空要素。
	for tag in emptytags:
		html = html.replace("".join(["</", tag, ">"]), "")
	return html
if __name__ == "__main__":	
	from html2elem import html2elem
	xml = """\
<html>
  <head>
    <meta charset="utf-8">
    <title>My test<wbr> page</title>
  </head>
  <body>
    <img src="images/firefox-icon.png" alt="My test image">
  </body>
</html>	"""
	root = html2elem(xml)  # ElementTreeのルートを取得。
	print("\nElementTree\n")
	print(ElementTree.tostring(root, encoding="unicode"))
	html = elem2html(root)  # ルートの子孫をHTMLの文字列に変換。
	for tag in "<root>", "</root>":  # elem2html()でついてくるrootタグを削除。
		html = html.replace(tag, "")	
	print("\nElementTree to HTML\n")
	print(html)
	