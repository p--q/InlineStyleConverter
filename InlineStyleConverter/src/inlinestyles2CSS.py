#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, webbrowser
from xml.etree.ElementTree import Element
from itertools import permutations, product, chain
from collections import ChainMap
from html2elem import html2elem  # HTMLをElementオブジェクトにして返す関数。
from elem2html import elem2html  # ElementオブジェクトからHTMLを返す関数。
from formathtml import formatHTML  # HTMLを整形する関数。
def inlinestyles2CSS(s):  # s: HTML文字列。
	root = html2elem(s)  # HTMLをElementTreeに変換してそのルートを取得。
	cssroot = generateCSS(root)  # インラインStyle属性をCSSに変換してstyleタグを挿入したElementTreeのrootを取得。
	h = elem2html(cssroot)  # ElementTreeをHTMLに変換。
	h = formatHTML(h)  # HTMLを整形。
	filename = "cssgenerated.html"  # HTMLを書き出すファイル名。
	print("Opening {} using the default browser.".format(filename))
	with open(filename, 'w', encoding='utf-8') as f:  # htmlファイルをUTF-8で作成。すでにあるときは上書き。
		f.writelines(h)  # ファイルに書き出し。
		webbrowser.open_new_tab(f.name)  # デフォルトのブラウザの新しいタブでhtmlファイルを開く。	
def generateCSS(root):  # インラインStyle属性をもつXMLのルートを渡して、CSSのstyleタグにして返す。argsはコマンドラインの引数。
	maxloc = 3  # 使用するロケーションステップの最大個数。
	pseudoclasses = ["active", "checked", "default", "defined", "disabled", "empty", "enabled", "first", "first-child", \
	"first-of-type", "focus", "focus-within", "hover", "indeterminate", "in-range", "invalid", "lang", "last-child", "last-of-type",\
	"left", "link", "only-child", "only-of-type", "optional" , "out-of-range", "read-only", "read-write", "required", "right",\
	"root", "scope", "target", "valid", "visited"]  # 擬似クラス。引数のあるものを除く。
	pseudoelements = ["after", "backdrop", "before", "first-letter", "first-line", "-moz-focus-inner"]  # 擬似要素	
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
	if csses:  # CSSが生成されたとき。
		for attrname in attrnames:	
			for n in root.iterfind('.//*[@{}]'.format(attrname)):
				del n.attrib[attrname]  # CSSにした属性をXMLから削除する。
		stylenode = createElement("style", text="\n".join(csses))  # CSSをstyleノードにする。
		for t in "head", "body", :
			node = root.find(".//{}".format(t))
			if node:
				node.append(stylenode)
				break
		else:
			root.insert(0, stylenode) 
	else:
		print("no CSS generated\n")
	return root		
def createNodesDic(root, attrnames):	# 属性の値をキーとする辞書に、その属性を持つノードを返すジェネレーターを取得する。
	dics = []
	for attrname in attrnames:
		attr_xpath = './/*[@{}]'.format(attrname)  # 属性のあるノードを取得するXPath。
		attrvals = set(i.get(attrname).strip() for i in root.iterfind(attr_xpath))  # 属性をもつノードのすべてから属性の値をすべて取得する。iterfind()だと直下以外の子ノードも返る。前後の空白を除いておく。
		dics.append({"{};{}".format(attrname, i):root.iterfind('.//*[@{}="{}"]'.format(attrname, i)) for i in attrvals})  # キー：属性の値、値: その属性のあるノードを返すジェネレーター、の辞書。キーの先頭に属性名が入っている。		
	return ChainMap(*dics)
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
def xpathToCSS(xpath):  # XPathをCSSセレクタに変換。
	prefix = ".//"
	if xpath.startswith(prefix):
		xpath = xpath.replace(prefix, "", 1)
	idw = '*[@id="'
	if idw in xpath:
		xpath = "#{}".format(xpath.split(idw)[-1])  # idより上階のXPathは削除する。
	xpath = xpath.replace('*[@class="', ".").replace('[@class="', ".").replace(" ", ".").replace('"]', "").replace("//", " ").replace("/", ">")  # classを変換、複数classを結合、閉じ角括弧を削除、子孫結合子を変換、子結合子を変換。
	return xpath.replace("[", ":nth-of-type(").replace("]", ")")
def createElement(tag, attrib={},  **kwargs):  # ET.Elementのアトリビュートのtextとtailはkwargsで渡す。		
	txt = kwargs.pop("text", None)
	tail = kwargs.pop("tail", None)
	elem = Element(tag, attrib, **kwargs)
	if txt is not None:
		elem.text = txt
	if tail is not None:
		elem.tail = tail	
	return elem	
if __name__ == "__main__":
	s = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Calendar</title></head><body><div id="calendar5_blogger"><div style="display:flex;flex-wrap:wrap;"><div style="flex:0 0 14%;text-align:center;"></div><div style="flex: 1 0 72%; text-align: center; cursor: pointer; color: rgb(62, 62, 62);" title="公開日と更新日を切り替える" id="title_calendar">2018年4月</div><div style="flex: 0 0 14%; text-align: center; cursor: pointer;" title="前月へ" id="right_calendar">»</div><div style="flex: 1 0 14%; text-align: center; color: rgb(255, 0, 0);" data-remainder="0">日</div><div style="flex:1 0 14%;text-align:center;" data-remainder="1">月</div><div style="flex:1 0 14%;text-align:center;" data-remainder="2">火</div><div style="flex:1 0 14%;text-align:center;" data-remainder="3">水</div><div style="flex:1 0 14%;text-align:center;" data-remainder="4">木</div><div style="flex:1 0 14%;text-align:center;" data-remainder="5">金</div><div style="flex: 1 0 14%; text-align: center; color: rgb(0, 51, 255);" data-remainder="6">土</div><div style="flex: 1 0 14%; text-align: center; color: rgb(255, 0, 0);" class="nopost" data-remainder="0">1</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="1">2</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="2">3</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="3">4</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="4">5</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="5">6</div><div style="flex: 1 0 14%; text-align: center; color: rgb(0, 51, 255);" class="nopost" data-remainder="6">7</div><div style="flex: 1 0 14%; text-align: center; color: rgb(255, 0, 0);" class="nopost" data-remainder="0">8</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="1">9</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="2">10</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="3">11</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="4">12</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="5">13</div><div style="flex: 1 0 14%; text-align: center; color: rgb(0, 51, 255);" class="nopost" data-remainder="6">14</div><div style="flex: 1 0 14%; text-align: center; color: rgb(255, 0, 0);" class="nopost" data-remainder="0">15</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="1">16</div><div pseudohover="dummy:val;" style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="2">17</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="3">18</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="4">19</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="5">20</div><div style="flex: 1 0 14%; text-align: center; color: rgb(0, 51, 255);" class="nopost" data-remainder="6">21</div><div style="flex: 1 0 14%; text-align: center; color: rgb(255, 0, 0);" class="nopost" data-remainder="0">22</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="1">23</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="2">24</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="3">25</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="4">26</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="5">27</div><div style="flex: 1 0 14%; text-align: center; color: rgb(0, 51, 255);" class="nopost" data-remainder="6">28</div><div style="flex: 1 0 14%; text-align: center; color: rgb(255, 0, 0);" class="nopost" data-remainder="0">29</div><div style="flex: 1 0 14%; text-align: center; color: rgb(255, 0, 0);" class="nopost" data-remainder="1">30</div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="2"></div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="3"></div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="4"></div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="5"></div><div style="flex: 1 0 14%; text-align: center; color: rgb(0, 51, 255);" class="nopost" data-remainder="6"></div><div style="flex: 1 0 14%; text-align: center; color: rgb(255, 0, 0);" class="nopost" data-remainder="0"></div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="1"></div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="2"></div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="3"></div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="4"></div><div style="flex:1 0 14%;text-align:center;" class="nopost" data-remainder="5"></div><div style="flex: 1 0 14%; text-align: center; color: rgb(0, 51, 255);" class="nopost" data-remainder="6"></div><div style="flex: 1 0 14%; text-align: center; display: none; color: rgb(255, 0, 0);" class="nopost" data-remainder="0"></div><div style="flex: 1 0 14%; text-align: center; display: none;" class="nopost" data-remainder="1"></div><div style="flex: 1 0 14%; text-align: center; display: none;" class="nopost" data-remainder="2"></div><div style="flex: 1 0 14%; text-align: center; display: none;" class="nopost" data-remainder="3"></div><div style="flex: 1 0 14%; text-align: center; display: none;" class="nopost" data-remainder="4"></div><div style="flex: 1 0 14%; text-align: center; display: none;" class="nopost" data-remainder="5"></div><div style="flex: 1 0 14%; text-align: center; display: none; color: rgb(0, 51, 255);" class="nopost" data-remainder="6"></div></div><div style="display:flex;flex-direction:column;padding-top:5px;text-align:center;"></div></div></body></html>'	
	inlinestyles2CSS(s)
	