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
		createStepLists = steplistsCreator(parent_map)
		styles = set(i.get("style") for i in root.iterfind(style_xpath))  # style属性をもつノードのすべてからstyle属性をすべて取得する。iterfind()は直下以外の子ノードも返る。
		stylenodedic = {i:root.iterfind('.//*[@style="{}"]'.format(i)) for i in styles}  # キー：sytle属性、値: そのstyle属性のあるノードを返すジェネレーター、の辞書。
		cssdic = dict()  # キー: sytle属性の値、値: CSSセレクタ
		for style, nodeiter in stylenodedic.items():  # 各style属性について。
			nodes = set(nodeiter)  # このstyle属性のあるノードの集合を取得。
			maxloc = 3
			xpaths = getStyleXPaths(root, nodes, maxloc, createStepLists)
			if xpaths:
				cssdic[style] = xpaths
			else:
				print("Can not cover all nodes having styles below with up to {} location step(s).".format(maxloc), file=sys.stderr)	
				print("{}".format(style))
				sys.exit()
		pass
			
			
			
# 			steplists = createStepLists(nodes[0])  # まずひとつのノードについてロケーションステップのリストのリストを取得。ロケーションステップの順は逆になっている。
# 			for num in range(3):  # ロケーションパスが3個までは調べる。
# 				xpath = getStyleXPath(root, nodes, steplists, num)
		
					
			
			
			
# 			while nodes:  # ノードがあるとき。
# 				steplists = createStepLists(nodes.pop())  # ノードのロケーションステップのリストのリストを取得。ロケーションステップの順は逆になっている。
# 
# 				xpath = getStyleXPath(root, nodes, steplists, num)
# 
# 				
# 				for step in steplists[0]:  # このノードの階層のローケーションパスについて。
# 					
# 					xpath = ".//{}".format(step)  # XPathの作成。
# 					xpathnodes = set(root.findall(xpath))  # 作成したXPathで該当するノードの集合。
# 					if nodes==xpathnodes:  # XPathで同じstyle属性をもつノードすべてが取得できたときはこのXPathを採用する。
# 						cssdic[style] = xpath
# 						break
# 				else:  # 1個のロケーションパスではすべてのノードが取得できなかったとき。
# 					for steplist in steplists[1:]:  # 上の階層のロケーションパスの一つと組み合わせる。
# 						for steps in product(steplist, steplists[0]):
# 							xpath = ".//{}//{}".format(*steps)  # XPathの作成。
# 							xpathnodes = set(root.findall(xpath))  # 作成したXPathで該当するノードの集合。
# 							if nodes==xpathnodes:
# 								cssdic[style] = xpath
# 								break
# 					if style in cssdic:  # XPathが取得されているとき。
# 						break
# 					else:  # 2つのロケーションパスの組み合わせではすべてのノードを取得できなかったとき。
# 						
# 						
# 						for steps in product(steplists[1], steplists[0]):  # 1つ上の階層のロケーションパスのみとの組み合わせについて。
# 							xpath = ".//{}/{}".format(*steps)  # XPathの作成。
# 							xpathnodes = set(root.findall(xpath))  # 作成したXPathで該当するノードの集合。
# 							if nodes==xpathnodes:
# 								cssdic[style] = xpath
# 								break		
# 					if not style in cssdic:  # まだXPathが取得されていないとき。
# 						
# 						
# 						for steplist in steplists[2:]:  # 3組のロケーションパスのXPathの作成。
# 							for steps in product(steplist, steplists[1], steplists[0]): 
# 								xpath = ".//{}//{}/{}".format(*steps)  # XPathの作成。				
# 								xpathnodes = set(root.findall(xpath))  # 作成したXPathで該当するノードの集合。
# 								if nodes==xpathnodes:
# 									cssdic[style] = xpath
# 									break	
# 						if style in cssdic:  # XPathが取得されているとき。
# 							break				
# 						else:
# 							for steps in product(steplist[2], steplists[1], steplists[0]): 
# 								xpath = ".//{}/{}/{}".format(*steps)  # XPathの作成。				
# 								xpathnodes = set(root.findall(xpath))  # 作成したXPathで該当するノードの集合。
# 								if nodes==xpathnodes:
# 									cssdic[style] = xpath
# 									break						
# 					if not style in cssdic:  # まだXPathが取得されていないとき。
# 						print("Could not create XPath for {}.".format(style))			




# def getStyleXPath(root, nodes, steplists, num):	# root: ルートノード、nodes, 同じstyle属性をもつノードの集合、ロケーションパスのリストのリスト、使用するロケーションパスの数-1
	
def getStyleXPaths(root, nodes, maxloc, createStepLists):	# root: ルートノード、nodes: 同じstyle属性をもつノードの集合、maxloc: 使用するロケーションパスの最大値	
	ori_nodes = nodes.copy()
	steplists = createStepLists(nodes.pop())  # まずひとつのノードについてロケーションステップのリストのリストを取得。ロケーションステップの順は逆になっている。
	for num in range(maxloc):  # まず1つですべてのノードを取得できるXPathを探す。
		if num:  # numが0のとき以外。
			for steplist in steplists[num:]:  # num+1個のロケーションパスの組のXPathの作成。
				for steps in product(*steplists[:num], steplist): 
					xpath = ".//{}//{}".format(steps[-1], "/".join(steps[-2::-1]))  # XPathの作成。				
					xpathnodes = set(root.findall(xpath))  # 作成したXPathで該当するノードの集合。
					if xpathnodes==ori_nodes:
						return xpath,		
		for steps in product(*steplists[:num+1]):
			xpath = ".//{}".format("/".join(steps[::-1]))  # XPathの作成。		
			xpathnodes = set(root.findall(xpath))  # 作成したXPathで該当するノードの集合。
			if xpathnodes==ori_nodes:
				return xpath,		
	xpaths = []
	while nodes:
		for num in range(maxloc):
			if nodes:
				xpath, xpathnodes = getXPath(root, steplists, nodes, num)
				if xpath:
					xpaths.append(xpath)
					nodes.difference_update(xpathnodes)	
					ori_nodes.difference_update(xpathnodes)	
					if not ori_nodes:
						return xpaths
		steplists = createStepLists(nodes.pop()) 
def getXPath(root, steplists, nodes, num):
	if num:  # numが0のとき以外。
		for steplist in steplists[num:]:  # num+1個のロケーションパスの組のXPathの作成。
			for steps in product(*steplists[:num], steplist): 
				xpath = ".//{}//{}".format(steps[-1], "/".join(steps[-2::-1]))  # XPathの作成。				
				xpathnodes = set(root.findall(xpath))  # 作成したXPathで該当するノードの集合。
				if xpathnodes<nodes:
					return xpath, xpathnodes	
	for steps in product(*steplists[:num+1]):
		xpath = ".//{}".format("/".join(steps[::-1]))  # XPathの作成。		
		xpathnodes = set(root.findall(xpath))  # 作成したXPathで該当するノードの集合。
		if xpathnodes<nodes:
			return xpath, xpathnodes	
	return "", set()		
	
	
		
		
		
# 		for steps in product(steplist[2], steplists[1], steplists[0]): 
# 			xpath = ".//{}/{}/{}".format(*steps)  # XPathの作成。				
# 			xpathnodes = set(root.findall(xpath))  # 作成したXPathで該当するノードの集合。
# 			if nodes==xpathnodes:
# 				cssdic[style] = xpath
# 				break					
			
			
# 			if len(nodes)==1:  # ノードの数が1個の時。
# 				n = nodes[0]  # このstyle属性のあるノードを取得。
# 				for step in generateStep(n):
# 					xpath = ".//{}".format(step)  # XPathにする。
# 					xpathnodes = root.findall(xpath)  # 作成したXPathで該当するノードを取得してみる。
# 					if xpathnodes==1 and xpathnodes[0]==n:
# 						cssdic[style] = xpath
# 						break
# 				else:
# 					p = parent_map[n]
					
					
				

				
				
# 				for paths in getElementXPathIter(n):  # このノードを選択するロケーションステップのリストを取得。
# 					path = "/".join(paths)  # XPathのロケーションステップを/で結合。
# 					idsep = "*[@id="
# 					if idsep in path:  # idのロケーションステップがあるとき
# 						paths = "{}{}".format(idsep, path.rsplit(idsep, 1)[-1]).split("/")  # idパス以降のロケーションステップを取得。
# 						
# 						
# 						
# 						xpath = ".//{}".format("/".join(paths))  # XPathにする。
# # 						path = "{}{}".format(idsep, path.rsplit(idsep, 1)[-1])  # id属性のあるノードの子のロケーションパスのリストを取得。"*[@id="で分割して最後の要素を取得して"*[@id="を先頭に追加し直す。
# # 						xpath = ".//{}".format(path)  # ルートノードからのXPathを作成。
# 
# 						xpathnodes = root.findall(xpath)  # 作成したXPathで該当するノードを取得してみる。
# 						if n in xpathnodes:  # 目的のノードを取得できたとき。
# 							
# 							
# 							xpathnodes.remove(n)  # 目的のノードを除外。
# 							if xpathnodes:  # まだノードが残っている時。目的のノードと同じ階層かを調べる。
# 								if parent_map[n] in [parent_map[i] for i in xpathnodes]:  # 各ノードの親ノードが一致するときは同じ階層に他のノードがあるので不適格。(これはありえないはず)
# 									print("Could not create the CSS selector to select only one node having\nstyle='{}'".format(style), file=sys.stderr)
# 							# CSSパスが短く出来ないか真ん中を削ってみる。
# 							# pathsの最初と最後の要素をスペースでつなぐ。
# 							 # ダメなら最後の要素だけノードからパターンを再取得してチャレンジ。
# 							# ダメなら最初はスペース、最後の2つの要素を>というようにする。	
# 									
# 							
# 							css[style] = paths2CSSOneNode(paths)  # 動作確認したXPathをCSSパスとして採用。		
# 							break  # ループをでる。
# 						else:  # XPathで元のノードが取得できなかったとき(これはありえないはず)。
# 							print("Could not create the CSS selector to select one node having\nstyle='{}'".format(style), file=sys.stderr)		
# 					else:  # idのパスがないとき。
# 						print("This script does not create a CSS selector as it can not find a node with id attribute up to the root.", file=sys.stderr)
# 			else:  # 同じstyleを持つノードが複数ある時。
# 				pass
		
		
		
		
		
# 		stylenodes = root.findall(style_xpath)  # style属性をもつノードをすべて取得。iterfind()は直下以外の子ノードも返る。
# 		for n in stylenodes:  # style属性をもつ各ノードについて。
# 			xpathiter = getElementXPathIter(n)  # このノードで取りうるXPathのロケーションパスのリストを返すイテレーターを取得。
# 			for xpath in xpathiter:
# 				print("/".join(xpath))
# 				".//{}".format("/".join(xpath))

# def createStepGenerator(parent_map):			
# 	def generateStep(node):  # ロケーションステップを返すジェネレーター。
# 		tag = node.tag  # ノードのタグ。
# 		idattr = node.get("id")  # id属性の取得。
# 		if idattr:  # id属性がある時。
# 			yield '*[@id="{}"]'.format(idattr)  # idのロケーションステップを返す。idの場合はタグは影響しないので*にする。
# 		yield tag  # タグのみのを返す。
# 		children = [i for i in list(parent_map[node]) if i.tag==tag]  # 親ノードの子ノードの階層にあるノードのうち同じタグのノードのリストを取得。parent_map[node].iter()だとすべての階層の要素が返ってしまう。
# 		if len(children)>1:  # 同じタグのノードが同じ階層に複数ある時。
# 			pathindex = "[{}]".format(children.index(node)+1)  # ノードの順位を取得。1から始まる。
# 			yield "{}{}".format(tag, pathindex)  # タグに順位をつけたパス。		
# 		classattr = node.get("class")  # クラス属性の取得。
# 		if classattr:  # クラス属性がある時。
# 			classes = classattr.split(" ")  # クラスをリストにする。
# 			for i in range(1, len(classes)+1):  # 順列の長さ。
# 				for c in permutations(classes, i):  # 各順列について。
# 					cls = '[@class="{}"]'.format(" ".join(c))  # クラスのあらゆる組み合わせのパス。
# 					yield '*{}'.format(cls)  # タグを特定しないクラスを返す。
# 					yield '{}{}'.format(tag, cls)  # タグを特定したクラスを返す。		
# 	return generateStep
# def paths2CSSOneNode(paths):  # paths: ロケーションパスのリスト。
# 	csspath = []
# 	for path in paths:
# 		if "*[@id=" in path:
# 			csspath.append(path.replace('*[@id="', "#").split('"')[0])
# 		elif "[@class=" in path:
# 			csspath.append(".".join(path.split('[@class="')).split('"')[0])
# 		else:
# 			csspath.append(path)	
# 	return " ".join(csspath)  # 1つのノードしか選択しないCSSセレクターを返す。		
	
	
# 	path =[i.replace('*[@id="{', "#").replace('*[@class="{', ".").split("}")[0] for i in paths if "{" in i]
# 	csspath = ">".join([i.replace('*[@id="', "#").replace('*[@class="', ".").split('"')[0] if "@" in i else i for i in paths])
			
		
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
			

	
# def xpathiterCreator(parent_map):	
# 	pathdic = {}  # 作成したロケーションパスのキャッシュ。	
# 	def _getPath(p, n):  # p: 親ノード。n: ノード、からnが取りうるロケーションパスのリストを返す。
# 		path = []  # この階層での可能性のあるロケーションパスを入れるリスト。
# 		tag = n.tag  # ノードのタグ。
# 		idattr = n.get("id")  # id属性の取得。
# 		if idattr:  # id属性がある時。
# 			path.append('*[@id="{}"]'.format(idattr))  # idのパス。idの場合はタグは影響しないので*にする。
# 		classattr = n.get("class")  # クラス属性の取得。
# 		if classattr:  # クラス属性がある時。
# 			classes = classattr.split(" ")  # クラスをリストにする。
# 			for i in range(1, len(classes)+1):  # 順列の長さ。
# 				for c in permutations(classes, i):  # 各順列について。
# 					cls = '[@class="{}"]'.format(" ".join(c))  # クラスのあらゆる組み合わせのパス。
# 					path.append('{}{}'.format(tag, cls))  # タグを特定する。
# 					path.append('*{}'.format(cls))  # タグを特定しない。
# 		children = [i for i in list(p) if i.tag==tag]  # 親ノードの子ノードの階層にあるノードのうち同じタグのノードのリストを取得。p.iter()だとすべての階層の要素が返ってしまう。
# 		if len(children)>1:  # 同じタグのノードが同じ階層に複数ある時。
# 			pathindex = "[{}]".format(children.index(n)+1)  # ノードの順位を取得。1から始まる。
# 			path.append("{}{}".format(tag, pathindex))  # タグに順位をつけたパス。		
# 		path.append(tag)  # タグのみのパス。			
# 		return path	 # id、タグ+class、class、タグ[番号]、タグ、の順にする。
# 	def getElementXPathIter(n, r=None):  # ノードのすべてのXPathパターンを返すイテレーターを返す。ロケーションパスのタプルが返る。rは遡る階層数。
# 		paths = []  # ロケーションパスのリストを入れるリスト。
# 		c = 1  # 階層。1段階から始まる。
# 		while n in parent_map:  # 親ノードがあるときのみ実行。
# 			p = parent_map[n]  # 親ノードの取得。
# 			path = pathdic.setdefault(n, _getPath(p, n))  # nが取りうるロケーションパスのリストを辞書に取得。
# 			paths.append(path)  # この階層のロケーションパスのリストを取得。
# 			n = p  # 上の階層について調べる。
# 			if r is not None:
# 				c += 1
# 				if c==r:  # 階層番号に達したらwhile文を出る。
# 					break
# # 		paths.append(["./"])  # XPathの先頭のロケーションパスをリストで追加。
# 		paths.reverse()  # 右に子が来るように逆順にする。
# 		return product(*paths)  # pathsの要素のリストのすべての組み合わせを返すイテレーターを返す。
# 	return getElementXPathIter

	
	
	
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
	