#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
from xml.etree import ElementTree
def elem2html(elem):  # ElementオブジェクトをHTMLにして返す。
	html = ElementTree.tostring(elem, encoding="unicode", method="html")
	emptytags = "source", "track", "wbr", "embed"  # 終了タグがついてくる空要素。
	regex = re.compile("</{}>".format("|".join(emptytags)))
	return regex("", html)
if __name__ == "__main__":	
	xml = """\
<html>
  <head>
    <meta charset="utf-8">
    <title>My test page</title>
  </head>
  <body>
    <img src="images/firefox-icon.png" alt="My test image">
  </body>
</html>	"""

	elem2html(elem)