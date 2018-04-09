# -*- coding: utf-8 -*-
import re
import html
import sys
from xml.etree import ElementTree
from itertools import permutations, product
def inlinestyleconverter(htmlfile, pattern=r".*"):  # 正規表現が与えられていない時はすべてのノードについて実行する。
	maxloc = 3  # 使用するロケーションステップの最大個数。
	with open(htmlfile, encoding="utf-8") as f:
		root = createXML(f, pattern)  # ファイルから正規表現で抽出したHTMLをXMLにしてそのルートを取得。
		parent_map = {c:p for p in root.iter() for c in p if c.tag!="br"}  # 木の、子:親の辞書を作成。brタグはstyle属性のノードとは全く関係ないので除く。
		pseudonames = "hover", "-moz-focus-inner" # 属性として使用している擬似クラス名と擬似要素名のタプル。
		attrnodesdic = createNodesDic(root, pseudonames)  # キー: ノードの属性、値: その属性を持つノードを返すジェネレーター、の辞書を取得。
		cssdic = dict()  # キー: 属性の値、値: CSSセレクタとなるXPath。
		for attrval, nodeiter in attrnodesdic.items():  # 各属性について。
			print("\n{}\n\tCreating XPath for nodes with this style attribute.".format(attrval))
			nodes = set(nodeiter)  # このstyle属性のあるノードの集合を取得。
			xpaths = getStyleXPaths(root, nodes, maxloc, parent_map)  # nodesを取得するXPathのリストを取得する。
			if xpaths:  # XPathsのリストが取得できたとき。
				cssdic[attrval] = xpaths  # style属性をキーとして辞書に取得。
				print("\tXPaths:\n\t\t{}".format("\n\t\t".join(xpaths)))
			else:  # XPathを取得できなかったstyle属性を出力する。
				print("\tCould not create XPath covering nodes with this style attribute within {} location steps.".format(attrval, maxloc), file=sys.stderr)	
		print("\n\nCreating CSS\n")
		for attrval, xpaths in cssdic.items():
			attrval = attrval.rstrip(";")  # 最後のセミコロンは除く。
			if attrval.startswith("pseudo:"):  # 擬似クラス名または擬似要素が属性値として挿入されている時。
				pseudo, *styles = attrval.split(";")  # 擬似クラスまたは擬似要素の設定を取得。
				sep = "::" if "::" in pseudo else ":"  # ::なら擬似要素名、:なら擬似クラス名。
				pseudoclass = pseudo.split(":")[-1]  # 擬似クラス名または擬似要素名を取得。
				selector = ", ".join(["{}{}{}".format(xpathToCSS(i), sep, pseudoclass) for i in xpaths])
			else:
				styles = attrval.split(";")
				selector = ", ".join([xpathToCSS(i) for i in xpaths])
			css = "{} {{\n\t{};\n}}\n".format(selector, ";\n\t".join(styles))  # CSSに整形。
			print(css)
			
			
			
			
def createNodesDic(root, pseudonames):	# 属性の値をキーとする辞書に、その属性を持つノードを返すジェネレーターを取得する。
	pseudoclasses = "active", "checked", "default", "defined", "disabled", "empty", "enabled", "first", "first-child", \
	"first-of-type", "focus", "focus-within", "hover", "indeterminate", "in-range", "invalid", "lang", "last-child", "last-of-type",\
	"left", "link", "only-child", "only-of-type", "optional" , "out-of-range", "read-only", "read-write", "required", "right",\
	"root", "scope", "target", "valid", "visited"  # 擬似クラス。引数のあるものを除く。
	pseudoelements = "after", "backdrop", "before", "first-letter", "first-line", "-moz-focus-inner"  # 擬似要素
	attrnodesdic = {}
	attrnodesdic.update(getAttrDic(root, "style"))
	for psuedoname in pseudonames:
		if psuedoname in pseudoclasses:
			sep = ":"
		elif psuedoname in pseudoelements: 
			sep = ""
		else:
			print("{} is neither pseudo-class nor pseudo-element.".format(psuedoname))
			continue
		attrnodesdic.update(getAttrDic(root, psuedoname, sep))
	return attrnodesdic
def getAttrDic(root, attrname, sep=""):
	attr_xpath = './/*[@{}]'.format(attrname)  # 属性のあるノードを取得するXPath。
	attrvals = set(i.get(attrname).strip() for i in root.iterfind(attr_xpath))  # 属性をもつノードのすべてから属性をすべて取得する。iterfind()だと直下以外の子ノードも返る。前後の空白を除いておく。
	pseudo = "" if attrname=="style" else "pseudo:{}{};".format(sep, attrname)  # style属性以外の属性名は値として先頭に追加する。
	return {"{}{}".format(pseudo, i):root.iterfind('.//*[@{}="{}"]'.format(attrname, i)) for i in attrvals}  # キー：属性の値、値: その属性のあるノードを返すジェネレーター、の辞書。				
def xpathToCSS(xpath):  # XPathをCSSセレクタに変換。
	prefix = ".//"
	if xpath.startswith(prefix):
		xpath = xpath.replace(prefix, "", 1)
	idw = '*[@id="'
	if idw in xpath:
		xpath = "#{}".format(xpath.split(idw)[-1])  # idより上階のXPathは削除する。
	xpath = xpath.replace('*[@class="', ".").replace('[@class="', ".").replace(" ", ".").replace('"]', "").replace("//", " ").replace("/", ">")  # classを変換、複数classを結合、閉じ角括弧を削除、子孫結合子を変換、子結合子を変換。
	return xpath.replace("[", ":nth-of-type(").replace("]", ")")
def getStyleXPaths(root, nodes, maxloc, parent_map):	# root: ルートノード、nodes: 同じstyle属性をもつノードの集合、maxloc: 使用するロケーションパスの最大値
	xpathnodesdic = {}  # キー: XPath, 値: XPathで取得できるノードの集合。キャッシュに使用。
	ori_nodes = nodes.copy()  # 変更せずに確保しておく値。
	def _getXPath(steplists, num):  # steplistsからnum+1個のロケーションステップを使ってXPathを作成する。
		if num:  # numが0のときはスキップ。
			for steplist in steplists[num:]:  # num個目のロケーションステップを順番に取得する。
				for steps in product(*steplists[:num], steplist): 
					xpath = ".//{}//{}".format(steps[-1], "/".join(steps[-2::-1]))  # XPathの作成。	
					xpathnodes = xpathnodesdic.setdefault(xpath, set(root.findall(xpath)))  # 作成したXPathで該当するノードの集合。				
					if xpathnodes<=ori_nodes:
						return xpath, xpathnodes	
		for steps in product(*steplists[:num+1]):
			xpath = ".//{}".format("/".join(steps[::-1]))  # XPathの作成。		
			xpathnodes = xpathnodesdic.setdefault(xpath, set(root.findall(xpath)))  # 作成したXPathで該当するノードの集合。	
			if xpathnodes<=ori_nodes:
				return xpath, xpathnodes	
		return "", set()
	createStepLists = steplistsCreator(parent_map)  # 各ノードのロケーションステップのリストを取得する関数。
	steplists = createStepLists(nodes.pop())  # まずひとつのノードについてロケーションステップのリストのリストを取得。ロケーションステップの順は逆になっている。
	for num in range(maxloc):  # まず1つですべてのノードを取得できるXPathを探す。
		if num:  # numが0のときはスキップ。
			for steplist in steplists[num:]:  # num+1個のロケーションパスの組のXPathの作成。
				for steps in product(*steplists[:num], steplist): 
					xpath = ".//{}//{}".format(steps[-1], "/".join(steps[-2::-1]))  # XPathの作成。	
					xpathnodes = xpathnodesdic.setdefault(xpath, set(root.findall(xpath)))  # 作成したXPathで該当するノードの集合。
					if xpathnodes==ori_nodes:
						return xpath,		
		for steps in product(*steplists[:num+1]):
			xpath = ".//{}".format("/".join(steps[::-1]))  # XPathの作成。	
			xpathnodes = xpathnodesdic.setdefault(xpath, set(root.findall(xpath)))  # 作成したXPathで該当するノードの集合。	
			if xpathnodes==ori_nodes:
				return xpath,		
	# 一つのXPathではすべてのノードが取得できなかったときは複数のXPathを使う。
	xpaths = []  # XPathのリスト。
	nodescheck = ori_nodes.copy()  # すべて出力されたか確認用ノードの集合。
	while steplists:
		for num in range(maxloc):  # maxlocまでロケーションステップを増やしていく。
			xpath, xpathnodes = _getXPath(steplists, num)  # XPathとそれで取得したノードの集合を取得。
			if xpath:  # XPathが取得できたとき。
				xpaths.append(xpath)  # XPathをリストに追加する。
				nodes.difference_update(xpathnodes)  # ノードのスタックから除く。
				nodescheck.difference_update(xpathnodes)  # 出力確認用ノード集合から除く。
				if not nodescheck:  # すべてのノードを取得できるXPathが揃った時。
					return xpaths
				break
		steplists = createStepLists(nodes.pop()) if nodes else None	
	print("Could not cover {} node(s).".format(len(nodescheck)))
	return None	
def steplistsCreator(parent_map):
	stepdic = {}  # 作成したロケーションパスのキャッシュ。	
	def _getStep(n):  # p: 親ノード。n: ノード、からnが取りうるロケーションステップのリストを返す。条件が緩いのから返す。
		steplist = []  # この階層での可能性のあるロケーションステップを入れるリスト。
		tag = n.tag  # ノードのタグ。
		steplist.append(tag)  # タグのみのパス。		
		children = [i for i in list(parent_map[n]) if i.tag==tag]  # 親ノードの子ノードの階層にあるノードのうち同じタグのノードのリストを取得。p.iter()だとすべての階層の要素が返ってしまう。
		if len(children)>1:  # 同じタグのノードが同じ階層に複数ある時。
			tagindex = "[{}]".format(children.index(n)+1)  # ノードの順位を取得。1から始まる。
			steplist.append("{}{}".format(tag, tagindex))  # タグに順位をつけたパス。			
		classattr = n.get("class")  # クラス属性の取得。
		if classattr:  # クラス属性がある時。
			classes = classattr.split(" ")  # クラスをリストにする。
			clss = ['[@class="{}"]'.format(" ".join(c)) for i in range(1, len(classes)+1) for c in permutations(classes, i)]  # classの全組み合わせを取得。
			[steplist.append('*{}'.format(c)) for c in clss]  # タグを特定しないクラス。
			[steplist.append('{}{}'.format(tag, c)) for c in clss]  # タグを特定したクラス。
		idattr = n.get("id")  # id属性の取得。
		if idattr:  # id属性がある時。
			steplist.append('*[@id="{}"]'.format(idattr))  # idのパス。idの場合はタグは影響しないので*にする。		
		return steplist	 # id、タグ、タグ[番号]、class、タグ+class、の順にロケーションステップを返す。
	def createStepLists(n):  # ノードのすべてのXPathパターンを返すイテレーターを返す。ロケーションステップのタプルが返る。
		steplists = []  # ロケーションステップのリストを入れるリスト。
		while n in parent_map:  # 親ノードがあるときのみ実行。
			steplists.append(stepdic.setdefault(n, _getStep(n)))  # nが取りうるロケーションステップのリストを辞書から取得。
			n = parent_map[n]  # 次の親ノードについて。
		return steplists  # rootから逆向きのリスト。
	return createStepLists
def createXML(f, pattern):  # ファイルオブジェクトと、ノードを抜き出す正規表現パターンからXMLのルートを返す。
	s = f.read()  # ファイルから文字列を取得する。
	subhtml = re.findall(pattern, s, flags=re.DOTALL)  # XMLに変換するhtmlを取得する。
	if not subhtml:
		print("There is no html matching r'{}'.".format(pattern), file=sys.stderr)
		sys.exit()	
	x = "<root>{}</root>".format(html2xml(subhtml[0])) # 最初にマッチングしたノードのみxmlにする処理をする。抜き出したhtmlにルート付ける。一つのノードにまとまっていないとjunk after document elementがでる。
	try:
		return ElementTree.XML(x)  # ElementTreeのElementにする。HTMLをXMLに変換して渡さないといけない。
	except ElementTree.ParseError as e:  # XMLとしてパースできなかったとき。
		errorLines(e, x)  # エラー部分の出力。
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
	