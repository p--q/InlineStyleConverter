# -*- coding: utf-8 -*-
import re
import html
import sys
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from itertools import permutations
def inlinestyleconverter(htmlfile, pattern=r".*"):  # 正規表現が与えられていない時はすべてのノードについて実行する。
	style_xpath = './/*[@style]'  # sytleのあるノードを取得するXPath。
	with open(htmlfile, encoding="utf-8") as f:
		s = f.read()  # ファイルから文字列を取得する。
		subhtml = re.findall(pattern, s, flags=re.DOTALL)  # XMLに変換するhtmlを取得する。
		if not subhtml:
			print("There is no html matching r'{}'.".format(pattern), file=sys.stderr)
			sys.exit()	
		x = html2xml(subhtml[0])  # 最初にマッチングしたノードのみxmlにする処理をする
		x = "".join(["<root>", x, "</root>"]) # 抜き出したhtmlにルート付ける。一つのノードにまとまっていないとjunk after document elementがでる。
		try:
			root = ElementTree.XML(x)  # ElementTreeのElementにする。HTMLをXMLに変換して渡さないといけない。
		except ElementTree.ParseError as e:  # XMLとしてパースできなかったとき。
			errorLines(e, x)  # エラー部分の出力。
		parent_map = {c:p for p in root.iter() for c in p if c.tag!="br"}  # 木の、子:親の辞書を作成。brタグはstyle属性のノードとは全く関係ないので除く。
# 		element2CSSPath = csspathCreator(parent_map)

		stylenodes = root.findall(style_xpath)  # style属性をもつノードをすべて取得。
		for n in stylenodes:
			getElementXPath(parent_map, n)
		
# 		while stacks:
# 			n = stacks.pop()
# 			csspath = element2CSSPath(n)
			
def getElementXPath(parent_map, n):  # ノードのXPathパターンの作成。
# 	xpaths = []
	paths = []
	while n in parent_map:  # 親ノードがあるときのみ実行。
		tags = []
		p = parent_map[n]  # 親ノードの取得。
		tag = n.tag
		tags.append(tag)
		children = [i for i in list(p) if i.tag==tag]  # 親ノードの子ノードのうち同じタグのノードのリストを取得。p.iter()だとすべての要素が返ってしまう。
		if len(children)>1:
			pathindex = "[{}]".format(children.index(n)+1)  # 同じタグが複数あるときのみインデックスを表示。インデックスは1から始まる。
			tags.append("{}{}".format(tag, pathindex))
		idattr = n.get("id")
		if idattr:
			tags.append('[@id="{}"]'.format(idattr))
		classattr = n.get("class")
		if classattr:
			classes = classattr.split(" ")
			for i in range(1, len(classes)+1):
				for c in permutations(classes, i):
					tags.append('[@class="{}"]'.format(" ".join(c)))
		paths.append(tags)
		n = p
# 	paths.append(["root"])
	paths.reverse()  # 右に子が来るように逆順にする。
	children = []
	p = None
	while paths:
		parents = paths.pop()
		for p in parents:
			p.extend(children)
		children = parents
	root = p
	

	
	
	
# 	idxpath = idElementXPath(n)
# 	if idxpath:
# 		return idxpath
# 	else:
# 		paths = []
# 		while n is not None:
# 			if n in parent_map:  # 親ノードがあるとき。
# 				p = parent_map[n]  # 親ノードを取得。
# 				idxpath = idElementXPath(p)
# 				if idxpath:  # idがあるノードのときはそれ以上の親は追求しない。
# 					paths.append(idxpath)
# 					break
# 				else:
# 					children = [i for i in list(p) if i.tag==n.tag]  # 親ノードの子ノードのうち同じタグのノードのリストを取得。p.iter()だとすべての要素が返ってしまう。
# 					pathindex = "[{}]".format(children.index(n)+1) if len(children)>1 else ""  # 同じタグが複数あるときのみインデックスを表示。インデックスは1から始まる。
# 					paths.append("".join((n.tag, pathindex)))
# 			else:  # 親ノードがないときはnがrootのとき。
# 				paths.append(n.tag)
# 				break
# 			n = p  # 親の親を調べに行く。
# 		return "/{}".format("/".join(reversed(paths))) if paths else None
# def idElementXPath(n):
# 	idprop = n.get("id")
# 	return '//*[@id="{}"]'.format(idprop) if idprop else None		
		
		
# def csspath2XPath(csspath):  # CSSパスをXPathに変換。
# 	newpaths = ["./"]
# 	paths = csspath.split(" ")
# 	for path in paths:
# 		if "#" in path:
# 			newpaths = ['.//*[@id="{}"]'.format(path.split("#")[-1].split(".")[0])]
# 		elif "." in path:
# 			tag, *classnames = path.split(".")
# 			newpaths.append('{}[@class="{}"]'.format(tag, " ".join(classnames)))
# 		else:
# 			newpaths.append(path)	
# 	return "/".join(newpaths)				
# def csspathCreator(parent_map):	 # getParentNodeに渡したルートからのCSSパスを取得。	
# 	def element2CSSPath(n):  # ノードのCSSパスを作成。
# 		paths = []  # パスのリスト。
# 		while n in parent_map:  # 親ノードがある間。
# 			label = n.tag.split(":")[-1].lower()  # localName、つまりタブ名を小文字で取得。コロンがあればその前は無視する。
# 			idprop = n.get("id")  # id属性があれば取得。
# 			if idprop:  # id属性があれば#でつなげる。。
# 				label = "".join((label, "#{}".format(idprop)))
# 			classes = n.get("class")  # クラス属性があれば取得。
# 			if classes:  # クラス属性があるときはドットでつなげる。
# 				label = "".join((label, *[".{}".format(i) for i in classes.split(" ")]))		
# 			paths.append(label)  # パスのリストに追加。
# 			if "#" in label:  # id属性のあるノードまできたら終わる。
# 				break
# 			else:
# 				n = parent_map[n]  # 親ノードを取得。
# 		return " ".join(reversed(paths))  # 逆順にスペースでつなげてCSSパスにして返す。
# 	return element2CSSPath
def errorLines(e, txt):  # エラー部分の出力。e: ElementTree.ParseError, txt: XML	
	print(e, file=sys.stderr)
	outputs = []
	r, c = e.position  # エラー行と列の取得。行は1から始まる。
	lines = txt.split("\n")  # 行のリストにする。
	errorline = lines[r-1]  # エラー行を取得。
	lastcolumn = len(errorline) - 1  # エラー行の最終列を取得。			
	if lastcolumn>400:   # エラー行が400列より大きいときはエラー列の前後200列を2行に分けて出力する。
		firstcolumn = c - 200
		firstcolumn = 0 if firstcolumn<0 else firstcolumn
		endcolumn = c + 200
		endcolumn = lastcolumn if endcolumn>lastcolumn else endcolumn			
		outputs.append("{}c{}to{}:  {}".format(r, firstcolumn, c-1, errorline[firstcolumn:c]))
		outputs.append("{}c{}to{}:  {}".format(r, c, endcolumn, errorline[c:endcolumn]))
	else:   # エラー行が400列以下のときは上下2行も出力。
		lastrow = len(lines) - 1
		firstrow = r - 2
		firstrow = 0 if firstrow<0 else firstrow
		endrow = r + 2
		endrow = lastrow if endrow>lastrow else endrow
		if endrow-firstrow<5:  # 5行以下のときは5行表示する。
			firstrow = endrow - 5
			firstrow = 0 if firstrow<0 else firstrow
		for i in range(firstrow, endrow+1):
			outputs.append("{}:  {}".format(i+1, lines[i]))
	print("\n".join(outputs))
	sys.exit()			
def html2xml(s):  # HTML文字参照をUnicodeに変換する。閉じられていないタグを閉じる。
	txt = html.unescape(s)  # HTML文字参照をUnicodeに変換する。 
	noendtags = "br", "img", "hr", "meta", "input", "embed", "area", "base", "col", "keygen", "link", "param", "source"  # ウェブブラウザで保存すると閉じられなくなるタグ。
	noend_regex = re.compile("|".join([r"(?<=<)\s*?{}.*?(?=>)".format(i) for i in noendtags]))  # 各タグについて正規表現オブジェクトの作成。各タグの<>内のみを抽出する。
	txt = noend_regex.sub(repl, txt)  # マッチングオブジェクトをreplに渡して処理。
	return txt
def repl(m):  # マッチングオブジェクトの処理。
	e = m.group(0).rstrip()
	return e if e.endswith("/") else "".join([e, "/"])  # 要素が/で終わっていない時は/で閉じる。
if __name__ == "__main__": 
	inlinestyleconverter("source.html", r'<div id="tcuheader".*<\/div>' )  # htmlファイルと、sytle属性のあるノードを抽出する正規表現を渡す。なるべく<script>や<style>要素が入らないようにする。
	