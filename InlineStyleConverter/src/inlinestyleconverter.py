# -*- coding: utf-8 -*-
import re
import html
import sys
from xml.etree import ElementTree
from itertools import permutations, product
def inlinestyleconverter(htmlfile, pattern=r".*"):  # 正規表現が与えられていない時はすべてのノードについて実行する。
	style_xpath = './/*[@style]'  # sytleのあるノードを取得するXPath。
	with open(htmlfile, encoding="utf-8") as f:
		s = f.read()  # ファイルから文字列を取得する。
		subhtml = re.findall(pattern, s, flags=re.DOTALL)  # XMLに変換するhtmlを取得する。
		if not subhtml:
			print("There is no html matching r'{}'.".format(pattern), file=sys.stderr)
			sys.exit()	
		x = "<root>{}</root>".format(html2xml(subhtml[0])) # 最初にマッチングしたノードのみxmlにする処理をする。抜き出したhtmlにルート付ける。一つのノードにまとまっていないとjunk after document elementがでる。
		try:
			root = ElementTree.XML(x)  # ElementTreeのElementにする。HTMLをXMLに変換して渡さないといけない。
		except ElementTree.ParseError as e:  # XMLとしてパースできなかったとき。
			errorLines(e, x)  # エラー部分の出力。
		parent_map = {c:p for p in root.iter() for c in p if c.tag!="br"}  # 木の、子:親の辞書を作成。brタグはstyle属性のノードとは全く関係ないので除く。
		getElementXPathIter = xpathiterCreator(parent_map)
		styles = set(i.get("style") for i in root.iterfind(style_xpath))  # style属性をもつノードのすべてからstyle属性をすべて取得する。iterfind()は直下以外の子ノードも返る。
		stylenodedic = {i:root.iterfind('.//*[@style="{}"]'.format(i)) for i in styles}  # キー：sytle属性、値: ノードを返すジェネレーター、の辞書。
		css = dict()  # キー: sytle属性の値、値: CSSセレクタ
		for style, nodeiter in stylenodedic.items():  # 各style属性について。
			nodes = list(nodeiter)  # このstyle属性のあるノードのリストを取得。
			if len(nodes)==1:  # ノードの数が1個の時。
				n = nodes[0]  # このstyle属性のあるノードを取得。
				for paths in getElementXPathIter(n):  # このノードを選択するロケーションパスのリストを取得。
					path = "/".join(paths)  # XPathのロケーションパスを取得。
					idsep = "*[@id="
					if idsep in path:  # idのパスがあるときはidパス以降のみを使用。
						paths = "{}{}".format(idsep, path.rsplit(idsep, 1)[-1]).split("/")  # id属性のあるノードの子のロケーションパスのリストを取得。
						xpath = ".//{}".format("/".join(paths))  # XPathにする。
						xpathnodes = root.findall(xpath)  # 作成したXPathで該当するノードを取得してみる。XPathでは孫要素以降も取得される。
						if n in xpathnodes:  # 目的のノードを取得できたとき。
							xpathnodes.remove(n)  # 目的のノードを除外。
							if xpathnodes:  # まだノードが残っている時。目的のノードと同じ階層かを調べる。
								if parent_map[n] in [parent_map[i] for i in xpathnodes]:  # 各ノードの親ノードが一致するときは同じ階層に他のノードがあるので不適格。(これはありえないはず)
									print("Could not create the CSS selector to select only one node having\nstyle='{}'".format(style), file=sys.stderr)
							# CSSパスが短く出来ないか真ん中を削ってみる。
									
									
							
							css[style] = paths2CSSOneNode(paths)  # 動作確認したXPathをCSSパスとして採用。		
							break  # ループをでる。
						else:  # XPathで元のノードが取得できなかったとき(これはありえないはず)。
							print("Could not create the CSS selector to select one node having\nstyle='{}'".format(style), file=sys.stderr)		
					else:  # idのパスがないとき。
						print("This script does not create a CSS selector as it can not find a node with id attribute up to the root.", file=sys.stderr)
			else:  # 同じstyleを持つノードが複数ある時。
				pass
		
		
		
		
		
# 		stylenodes = root.findall(style_xpath)  # style属性をもつノードをすべて取得。iterfind()は直下以外の子ノードも返る。
# 		for n in stylenodes:  # style属性をもつ各ノードについて。
# 			xpathiter = getElementXPathIter(n)  # このノードで取りうるXPathのロケーションパスのリストを返すイテレーターを取得。
# 			for xpath in xpathiter:
# 				print("/".join(xpath))
# 				".//{}".format("/".join(xpath))
			
			
			
def paths2CSSOneNode(paths):  # paths: ロケーションパスのリスト。
	csspath = []
	for path in paths:
		if "*[@id=" in path:
			csspath.append(path.replace('*[@id="', "#").split('"')[0])
		elif "[@class=" in path:
			csspath.append(".".join(path.split('[@class="')).split('"')[0])
		else:
			csspath.append(path)	
	return " ".join(csspath)  # 1つのノードしか選択しないCSSセレクターを返す。		
	
	
# 	path =[i.replace('*[@id="{', "#").replace('*[@class="{', ".").split("}")[0] for i in paths if "{" in i]
# 	csspath = ">".join([i.replace('*[@id="', "#").replace('*[@class="', ".").split('"')[0] if "@" in i else i for i in paths])
			
		
	
			

	
def xpathiterCreator(parent_map):	
	pathdic = {}  # 作成したロケーションパスのキャッシュ。	
	def _getPath(p, n):  # p: 親ノード。n: ノード、からnが取りうるロケーションパスのリストを返す。
		path = []  # この階層での可能性のあるロケーションパスを入れるリスト。
		tag = n.tag  # ノードのタグ。
		idattr = n.get("id")  # id属性の取得。
		if idattr:  # id属性がある時。
			path.append('*[@id="{}"]'.format(idattr))  # idのパス。idの場合はタグは影響しないので*にする。
		classattr = n.get("class")  # クラス属性の取得。
		if classattr:  # クラス属性がある時。
			classes = classattr.split(" ")  # クラスをリストにする。
			for i in range(1, len(classes)+1):  # 順列の長さ。
				for c in permutations(classes, i):  # 各順列について。
					cls = '[@class="{}"]'.format(" ".join(c))  # クラスのあらゆる組み合わせのパス。
					path.append('{}{}'.format(tag, cls))  # タグを特定する。
					path.append('*{}'.format(cls))  # タグを特定しない。
		children = [i for i in list(p) if i.tag==tag]  # 親ノードの子ノードの階層にあるノードのうち同じタグのノードのリストを取得。p.iter()だとすべての階層の要素が返ってしまう。
		if len(children)>1:  # 同じタグのノードが同じ階層に複数ある時。
			pathindex = "[{}]".format(children.index(n)+1)  # ノードの順位を取得。1から始まる。
			path.append("{}{}".format(tag, pathindex))  # タグに順位をつけたパス。		
		path.append(tag)  # タグのみのパス。			
		return path	 # id、タグ+class、class、タグ[番号]、タグ、の順にする。
	def getElementXPathIter(n, r=None):  # ノードのすべてのXPathパターンを返すイテレーターを返す。ロケーションパスのタプルが返る。rは遡る階層数。
		paths = []  # ロケーションパスのリストを入れるリスト。
		c = 1  # 階層。1段階から始まる。
		while n in parent_map:  # 親ノードがあるときのみ実行。
			p = parent_map[n]  # 親ノードの取得。
			path = pathdic.setdefault(n, _getPath(p, n))  # nが取りうるロケーションパスのリストを辞書に取得。
			paths.append(path)  # この階層のロケーションパスのリストを取得。
			n = p  # 上の階層について調べる。
			if r is not None:
				c += 1
				if c==r:  # 階層番号に達したらwhile文を出る。
					break
# 		paths.append(["./"])  # XPathの先頭のロケーションパスをリストで追加。
		paths.reverse()  # 右に子が来るように逆順にする。
		return product(*paths)  # pathsの要素のリストのすべての組み合わせを返すイテレーターを返す。
	return getElementXPathIter

	
	
	
# 	paths.append(["root"])
# 	paths.reverse()  # 右に子が来るように逆順にする。
# 	children = []
# 	p = None
# 	while paths:
# 		parents = paths.pop()
# 		for p in parents:
# 			p.extend(children)
# 		children = parents
# 	root = p
	

	
	
	
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
	