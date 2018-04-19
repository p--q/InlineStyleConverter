#!/usr/bin/python3
# -*- coding: utf-8 -*-
from xml.etree import ElementTree
def elem2html(elem):  # ElementオブジェクトをHTMLにして返す。
	doctypetxt = ""
	doctype = elem.find(".//doctype")  # ドキュメントタイプ宣言を入れたノードを取得。
	if doctype is not None:  # ドキュメントタイプ宣言を入れたノードが取得出来た時。
		doctypetxt = doctype.text  # ドキュメントタイプ宣言を取得。
		elem.find(".//doctype/..").remove(doctype)  # doctypeノードを削除。
	h = ElementTree.tostring(elem, encoding="unicode", method="html")
	emptytags = "source", "track", "wbr", "embed", "root"  # 終了タグがついてくる空要素などの終了タグを削除。
	for tag in emptytags:
		h = h.replace("".join(["</", tag, ">"]), "")
	h = h.replace("<root>", "")
	return "".join([doctypetxt, h])
if __name__ == "__main__":	
	from html2elem import html2elem
	from formathtml import formatHTML
	s = """\
<!DOCTYPE html><html>
  <head>
    <meta charset="utf-8">
    <title>My test<br> page</title>
  </head>
  <body>
    <img src="images/firefox-icon.png" alt="My test image">
  </body>
</html>	"""
	root = html2elem(s)  # ElementTreeのルートを取得。
	print("\nElementTree\n")
	print(ElementTree.tostring(root, encoding="unicode"))
	h = elem2html(root)  # ルートの子孫をHTMLの文字列に変換。	
	print("\nElementTree to HTML\n")
	print(formatHTML(h, reset=True))
