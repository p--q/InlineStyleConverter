#!/usr/bin/python3
# -*- coding: utf-8 -*-
from xml.etree import ElementTree
def elem2html(elem):  # ElementオブジェクトをHTMLにして返す。
	doctypetxt = ""
	doctype = root.find(".//doctype")  # ドキュメントタイプ宣言を入れたノードを取得。
	if doctype is not None:
		doctypetxt = doctype.text
		elem.find(".//doctype/..").remove(doctype) 
	h = ElementTree.tostring(elem, encoding="unicode", method="html")
	emptytags = "source", "track", "wbr", "embed", "root"  # 終了タグがついてくる空要素などの終了タグを削除。
	for tag in emptytags:
		h = h.replace("".join(["</", tag, ">"]), "")
	h = h.replace("<root>", "")
	return "".join([doctypetxt, h])
if __name__ == "__main__":	
	from html2elem import html2elem
	xml = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"><html>
  <head>
    <meta charset="utf-8">
    <title>My test<wbr> page</title>
  </head>
  <body>
    <img src="images/firefox-icon.png" alt="My test image">
  </body>
</html>	"""
# 	xml = xml.replace("\n", "")
	root = html2elem(xml)  # ElementTreeのルートを取得。
	print("\nElementTree\n")
	print(ElementTree.tostring(root, encoding="unicode"))
	h = elem2html(root)  # ルートの子孫をHTMLの文字列に変換。	
	print("\nElementTree to HTML\n")
# 	print(h) 
	from formathtml import  formatHTML
	import re
	regex = re.compile(r'')
	h = h.replace(" ", "").replace()
	print(formatHTML(h))