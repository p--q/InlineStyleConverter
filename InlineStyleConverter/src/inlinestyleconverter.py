# -*- coding: utf-8 -*-
import re
import html
import sys
from xml.etree import ElementTree


def inlinestyleconverter(htmlfile, pattern=r".*"):  # 正規表現が与えられていない時はすべてのノードについて実行する。
# 	regex = re.compile(pattern, flags=re.DOTALL)  # XMLに変換するノードを取得する正規表現オブジェクト。
	style_xpath = './/*[@style]'  # sytleのあるノードを取得するXPath。
	with open(htmlfile, encoding="utf-8") as f:
		s = f.read()  # ファイルから文字列を取得する。
		subhtml = re.findall(pattern, s, flags=re.DOTALL)  # XMLに変換するhtmlを取得する。
		if not subhtml:
			print("There is no node matching r'{}'.".format(pattern), file=sys.stderr)
			sys.exit()	
# 		t = html.unescape(subhtml[0])  # HTML文字参照をUnicodeに変換する。最初に見つかったノードしか処理しない。

# 		x = re.sub(r"<\s*br\s*>", "<br/>", t)  # 閉じられていないタグを閉じて、XMLにする。
		x = html2xml(subhtml[0])
		x = x.replace("\n", "")  # デバッグ用。
		
		x = "<root>{}</root>".format(x)
		root = ElementTree.XML(x)  # ElementTreeのElementにする。
		parent_map = parent_map = {c:p for p in root.iter() for c in p if c.tag!="br"}  # 木の、子:親の辞書を作成。brタグは除く。
		style_nodes = root.findall(style_xpath)  # style属性をもつノードをすべて取得。
		pass
			
			
def html2xml(s):
	
# 	s = """\
# <ul>
# <li>スライム A
# <li>スライム B </li>
# <li>スライムC
# </ul>
# <br >
# """
	
	
	txt = html.unescape(s)  # HTML文字参照をUnicodeに変換する。 
	noendtags = "br", "img", "hr", "meta", "input", "embed", "area", "base", "col", "keygen", "link", "param", "source"
# 	optionalendtags = "li", "dt", "dd", "p", "tr", "td", "th", "rt", "rp", "optgroup", "option", "thread", "tfoot"
# 	optionaltags = "html", "head", "body", "tbody", "colgroup"
# 	noend_regex = re.compile("|".join([r"(?<=<)\s*?{}.*?[^\/]?(?=>)".format(i) for i in noendtags]))
# 	txt = noend_regex.sub(lambda m: "".join([m.group(0).strip(), " /"]), txt)
# 	optionalend_regex = re.compile("|".join([r"(?<=<)\s*?({0})(.*?>.*?)<(?!/{0})".format(i) for i in optionalendtags]), flags=re.DOTALL)
# 	txt = optionalend_regex.sub(repl, txt)
	
	noend_regex = re.compile("|".join([r"(?<=<)\s*?{}.*?(?=>)".format(i) for i in noendtags]))
	txt = noend_regex.sub(repl, txt)
	
	
# 	print(txt)
		
	return txt
# def repl(m):
# 	tag = m.group(1)
# 	txt = m.group(2).rstrip()
# 	if re.search(r"<\s*?\/\s*?{}".format(tag), txt):
# 		new = m.group(0)
# 	else:
# 		new = "{0}{1}</{0}><".format(tag, txt)
# 	return new
def repl(m):
	e = m.group(0).rstrip()
	if e.endswith("/"):
		return e
	else:
		return "".join([e, "/"])
	
	




if __name__ == "__main__": 
# 	inlinestyleconverter("source.html", r"<body>.*<\/body>" )  # htmlファイルと、sytle属性のあるノードを抽出する正規表現を渡す。
	inlinestyleconverter("source.html", r'<div id="tcuheader".*<\/div>' )  # htmlファイルと、sytle属性のあるノードを抽出する正規表現を渡す。rootがあるようにしないとjunk after document elementがでる。