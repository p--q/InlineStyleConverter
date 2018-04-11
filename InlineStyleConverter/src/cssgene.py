#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re, sys, html, webbrowser
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from itertools import permutations, product, chain
from collections import ChainMap
def inlinestyleconverter(htmlfile, pattern=r".*", *, args=None):  # 正規表現が与えられていない時はすべてのノードについて実行する。
	regex = re.compile(pattern, flags=re.DOTALL)  # HTMLからXMLに変換する部分を抜き出す正規表現オブジェクト。
	with open(htmlfile, encoding="utf-8") as f:
		s = f.read()  # ファイルから文字列を取得する。
	root = convertToXML(s, regex)  # ファイルから正規表現で抽出したHTMLをXMLにしてそのルートを取得。
	root = generateCSS(root, args)  # インラインStyle属性をCSSに変換してstyleタグを挿入。
	replhtml = "".join([ElementTree.tostring(i, encoding="unicode", method="html") for i in root])  # XMLをHTMLのユニコード文字列に戻す。
	newhtml = formatHTML(regex.sub(replhtml, s))   # 元ファイルのHTMLをCSS入りに置換。
	outfile = args.output if args is not None and args.output else "converted_{}".format(htmlfile)  # 出力ファイル名。
	print("Opening {} using the default browser.".format(outfile))
	with open(outfile, 'w', encoding='utf-8') as f:  # htmlファイルをUTF-8で作成。すでにあるときは上書き。ホームフォルダに出力される。
		f.writelines(newhtml)  # ファイルに書き出し。
		webbrowser.open_new_tab(f.name)  # デフォルトのブラウザの新しいタブでhtmlファイルを開く。	
def formatHTML(html):  # HTMLを整形する。
	tagregex = re.compile(r"(?i)<\/?(\w+)((\s+[a-zA-Z0-9_\-]+(\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)+\s*|\s*)\/?>")  # 開始タグと終了タグすべてを抽出する正規表現オブジェクト。
	repltag = repltagCreator()  # マッチオブジェクトを処理する関数を取得。
	return tagregex.sub(repltag, html)
def repltagCreator():  # 開始タグと終了タグのマッチオブジェクトを処理する関数を返す。
	indent = "\t"  # インデント。
	c = 0  # インデントの数。
	starttagtype = ""  # 開始タグと終了タグが対になっているかを確認するため開始タグの要素型をクロージャに保存する。
	noendtags = "br", "img", "hr", "meta", "input", "embed", "area", "base", "col", "keygen", "link", "param", "source"  # HTMLでは終了タグがなくなるタグ。
	def repltag(m):  # 開始タグと終了タグのマッチオブジェクトを処理する関数。
		nonlocal c, starttagtype
		tag = m.group(0)  # タグを取得。
		if tag.startswith("</"):  # 終了タグの時。
			c -= 1  # インデントの数を減らす。
			if m.group(1)!=starttagtype:  # 開始タグを同じ要素型の時。
				txt = "\n{}{}".format(indent*c, tag)  # タグの前で改行してインデントする。
			else:  # 開始タグと異なる要素型のときはそのまま返す。
				txt = tag
			starttagtype = ""  # 開始タグの要素型をリセットする。
		else:  # 開始タグの時。
			tagtype = m.group(1)  # 要素型を取得。
			if tagtype in noendtags:  # 終了タグのないタグのときはそのまま返す。
				txt = tag
			else:  # 終了タグのないタグでない時。	
				txt = "\n{}{}".format(indent*c, tag)  # 開始タグの前で改行してインデントする。
				starttagtype = tagtype  # タグの要素型をクロージャに取得。
				c += 1  # インデントの数を増やす。
		return txt
	return repltag
def generateCSS(root, args=None):  # インラインStyle属性をもつXMLのルートを渡して、CSSのstyleタグにして返す。argsはコマンドラインの引数。
	maxloc = 3  # 使用するロケーションステップの最大個数。
	pseudoclasses = ["active", "checked", "default", "defined", "disabled", "empty", "enabled", "first", "first-child", \
	"first-of-type", "focus", "focus-within", "hover", "indeterminate", "in-range", "invalid", "lang", "last-child", "last-of-type",\
	"left", "link", "only-child", "only-of-type", "optional" , "out-of-range", "read-only", "read-write", "required", "right",\
	"root", "scope", "target", "valid", "visited"]  # 擬似クラス。引数のあるものを除く。
	pseudoelements = ["after", "backdrop", "before", "first-letter", "first-line", "-moz-focus-inner"]  # 擬似要素	
	if args is not None:
		maxloc = args.maxsteps
		pseudoclasses.extend(args.pseudoclasses)
		pseudoelements.extend(args.pseudoelements)
	attrnames = list(chain(["style"], ("pseudo{}".format(i) for i in pseudoclasses), ("pseudoelem{}".format(i) for i in pseudoelements)))  # 抽出する属性名のイテレーター。	
	parent_map = {c:p for p in root.iter() for c in p if c.tag!="br"}  # 木の、子:親の辞書を作成。brタグはstyle属性のノードとは全く関係ないので除く。
	attrnodesdic = createNodesDic(root, attrnames)  # キー: ノードの属性、値: その属性を持つノードを返すジェネレーター、の辞書を取得。
	cssdic = dict()  # キー: 属性の値、値: CSSセレクタとなるXPath。
	for attrval, nodeiter in attrnodesdic.items():  # 各属性値について。
		print("\n{}".format(attrval))
		nodes = set(nodeiter)  # この属性値のあるノードの集合を取得。
		c = len(nodes)
		xpaths = getStyleXPaths(root, nodes, maxloc, parent_map)  # nodesを取得するXPathのリストを取得。
		if xpaths:  # XPathsのリストが取得できたとき。
			cssdic[attrval] = xpaths  # 属性値をキーとして辞書に取得。
			print("\t{} XPaths for {} nodes:              			  			  \n\t\t{}".format(len(xpaths), c, "\n\t\t".join(xpaths)))  # スペースを入れないとend=\rで出力した内容が残ってくる。
		else:  # XPathを取得できなかった属性値を出力する。
			print("Could not generate XPath covering nodes within {} location step(s).".format(maxloc), file=sys.stderr)	
	print("\n\n####################Generated CSS####################\n")
	csses = []  #完成したCSSを入れるリスト。
	for attrval, xpaths in cssdic.items():  # attrval: 属性値。最初の要素には属性名が入ってくる。
		attrval = attrval.rstrip(";")  # 最後のセミコロンは除く。
		attrname, *styles = attrval.split(";")  # 属性の値をリストで取得する。最初の要素は属性名。
		if attrname.startswith("pseudo"):  # 擬似クラス名または擬似要素の時。
			pseudo = attrname.replace("pseudoelem", ":").replace("pseudo", "")  # CSSセレクターに追加する形式に変換。
			selector = ", ".join(["{}:{}".format(xpathToCSS(i), pseudo) for i in xpaths])
		else:
			selector = ", ".join([xpathToCSS(i) for i in xpaths])
		css = "{} {{\n\t{};\n}}\n".format(selector, ";\n\t".join(styles))  # CSSに整形。
		print(css)
		csses.append(css)
	for attrname in attrnames:	
		for n in root.iterfind('.//*[@{}]'.format(attrname)):
			del n.attrib[attrname]  # CSSにした属性をXMLから削除する。				
	root.insert(0, createElement("style", text="\n".join(csses)))  # CSSをstyleタグにしてXMLに追加。子要素の先頭に入れる必要あり。	
	return root
def createElement(tag, attrib={},  **kwargs):  # ET.Elementのアトリビュートのtextとtailはkwargsで渡す。		
	txt = kwargs.pop("text", None)
	tail = kwargs.pop("tail", None)
	elem = Element(tag, attrib, **kwargs)
	if txt:
		elem.text = txt
	if tail:
		elem.tail = tail	
	return elem	
def createNodesDic(root, attrnames):	# 属性の値をキーとする辞書に、その属性を持つノードを返すジェネレーターを取得する。
	dics = []
	for attrname in attrnames:
		attr_xpath = './/*[@{}]'.format(attrname)  # 属性のあるノードを取得するXPath。
		attrvals = set(i.get(attrname).strip() for i in root.iterfind(attr_xpath))  # 属性をもつノードのすべてから属性の値をすべて取得する。iterfind()だと直下以外の子ノードも返る。前後の空白を除いておく。
		dics.append({"{};{}".format(attrname, i):root.iterfind('.//*[@{}="{}"]'.format(attrname, i)) for i in attrvals})  # キー：属性の値、値: その属性のあるノードを返すジェネレーター、の辞書。キーの先頭に属性名が入っている。		
	return ChainMap(*dics)
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
				for steps in product(*steplists[:num], steplist):  # Python3.5以上が必要。
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
		print("\tSearching XPaths for {} nodes...".format(len(nodescheck)), end='\r')
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
	print("\tCould not cover {} node(s)          ".format(len(nodescheck)))
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
def convertToXML(s, regex):  # s:文字列、regex: ノードを抜き出す正規表現パターン。
	subhtml = regex.findall(s)  # XMLに変換するhtmlを取得する。
	if not subhtml:
		print("There is no html matching r'{}'.".format(regex.pattern), file=sys.stderr)
		sys.exit()	
	x = "<root>{}</root>".format(html2xml(subhtml[0])) # 最初にマッチングしたノードのみxmlにする処理をする。抜き出したhtmlにルート付ける。一つのノードにまとまっていないとjunk after document elementがでる。
	try:
		return ElementTree.XML(x)  # ElementTreeのElementにする。HTMLをXMLに変換して渡さないといけない。
	except ElementTree.ParseError as e:  # XMLとしてパースできなかったとき。
		errorLines(e, x)  # エラー部分の出力。
def errorLines(e, txt):  # エラー部分の出力。e: ElementTree.ParseError, txt: XML	
	print("Failed to convert HTML to XML.", file=sys.stderr)
	print(e, file=sys.stderr)
	outputs = []
	r, c = e.position  # エラー行と列の取得。行は1から始まる。
	lines = txt.split("\n")  # 行のリストにする。
	errorline = lines[r-1]  # エラー行を取得。
	lastcolumn = len(errorline) - 1  # エラー行の最終列を取得。		
	maxcolmuns = 400  # 折り返す列数。	
	if lastcolumn>maxcolmuns:   # エラー行が400列より大きいときはエラー列の前後200列を2行に分けて出力する。
		firstcolumn = c - maxcolmuns/2
		firstcolumn = 0 if firstcolumn<0 else firstcolumn
		endcolumn = c + maxcolmuns/2
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
def commadline():  # /opt/libreoffice5.4/program/python cssgene.py source.html -r '<div id="tcuheader".*<\/div>'
	import argparse
	parser = argparse.ArgumentParser(description="convert inline style attributes of HTML file to <style> element")
	parser.add_argument('htmlfile', help='HTML file with inline style attributes')
	parser.add_argument('-r', '--regexpattern', default='.*', help="a regular expression pattern that extracts HTML to be converted to XML (default: '.*')")
	parser.add_argument('-m', '--maxsteps', default=3, type=int, help='maximum number of selector elements (default: 3)')
	parser.add_argument('-c', '--pseudoclasses', default=[], nargs='*', metavar="Pseudo-class", help='additional pseudo-classes for inline attribute')
	parser.add_argument('-e', '--pseudoelements', default=[], nargs='*', metavar="Pseudo-element", help='additional pseudo-elements for inline attribute')
	parser.add_argument('-o', '--output', help='output file (default: prefix converted_)')
	parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.1.0')
	args = parser.parse_args()
	inlinestyleconverter(args.htmlfile, args.regexpattern, args=args)
if __name__ == "__main__":
	commadline()  # コマンドラインから実行する時。
# 	inlinestyleconverter("p--q.html")  # このスクリプトを直接実行する時。
