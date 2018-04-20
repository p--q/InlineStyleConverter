#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re, html, sys
from random import randrange
from xml.etree import ElementTree
def html2elem(s):
	regex = re.compile(r"(?is)<(?:(?:((script|style).*?)>(.+?)<\/\2)|(\w+).*?|(!DOCTYPE.*?))>")  # <script>要素、<style>要素、タグすべて、ドキュメントタイプ宣言、にマッチする正規表現オブジェクト。
	stashdic = {}  # XMLパーサーでエラーになる要素を一時的に退避しておく辞書。キー:  代替タグ名、値: マッチオブジェクト。
	replHTML = replHTMLCreator(stashdic)  # 置換する関数を取得。
	s = html.unescape(s)  # HTML文字参照をUnicodeに変換する。 
	s = regex.sub(replHTML, s)	# XMLパーサーでエラーになるタグの処理。
	x = "".join(["<root>", s, "</root>"]) # htmlにルート付ける。一つのノードにまとまっていないとjunk after document elementがでる。
	try:
		root = ElementTree.XML(x)  # ElementTreeのElementにする。HTMLをXMLに変換して渡さないといけない。
	except ElementTree.ParseError as e:  # XMLとしてパースできなかったとき。
		errorLines(e, x)  # エラー部分の出力。	
		sys.exit()	
	for t, m in stashdic.items():  # 退避していたタグを戻す。
		node = root.find("".join([".//", t]))  # XPathで代替タグを取得。
		if t=="doctype":
			node.text = m.group(0)  # ドキュメントタイプ宣言はdoctypeタグのテキストノードに入れる（処理方法がわからないため）。
		else:
			scriptnode = ElementTree.XML("".join(["<", m.group(1), "/>"]))  # scriptノードをパーサーに読み込ませて属性の処理をする。
			node.tag = scriptnode.tag  # 代替タグ名を戻す。
			node.text = m.group(3)  # 代替タグにテキストノードを戻す。
			for attr in scriptnode.items():  # 代替タグに属性を戻す。
				node.set(*attr)
	return root
def replHTMLCreator(stashdic):
	noendtags = "br", "img", "hr", "meta", "input", "embed", "area", "base", "col", "link", "param", "source", "wbr", "track"   # ウェブブラウザで保存すると終了タグがなくなるタグ。
	def replHTML(m):
		if m.group(4) is not None:
			if m.group(4).lower() in noendtags:  # 閉じられていないタグのとき。
				if not m.group(0).endswith("/>"):
					return "".join([m.group(0)[:-1], "/>"])  # タグを閉じて返す。
		elif m.group(1) is not None:  # scriptタグの時。
				if m.group(3) and m.group(3).strip():  # 空白文字以外のテキストノードがある時。
					key = "stashrepl{}".format(randrange(10000))  # 置換するランダムタグを生成。
					stashdic[key] = m
					return "".join(["<", key, "/>"])  # 代替タグを返す。
		elif m.group(5) is not None:  # ドキュメントタイプ宣言がある時。
			stashdic["doctype"] = m
			return "<doctype/>"
		return m.group(0)
	return replHTML
def errorLines(e, txt):  # エラー部分の出力。e: ElementTree.ParseError, txt: XML	
	print("Failed to convert HTML to XML.", file=sys.stderr)
	print(e, file=sys.stderr)
	outputs = []
	r, c = e.position  # エラー行と列の取得。行は1から始まる。
	lines = txt.split("\n")  # 行のリストにする。
	errorline = lines[r-1]  # エラー行を取得。
	lastcolumn = len(errorline) - 1  # エラー行の最終列を取得。	
	startc, endc = (c-2, c+3) if c>3 else (0, 5)
	outputs.append("\nline {}, column {}-{}: {}\n".format(r, startc, endc-1, errorline[startc:endc]))  # まずエラー列の前後5列を出力する。	
	maxcolmuns = 400  # 折り返す列数。	
	if lastcolumn>maxcolmuns:   # エラー行が400列より大きいときはエラー列の前後200列を2行に分けて出力する。
		startcolumn = c - int(maxcolmuns/2)
		startcolumn = 0 if startcolumn<0 else startcolumn
		endcolumn = c + int(maxcolmuns/2)
		endcolumn = lastcolumn if endcolumn>lastcolumn else endcolumn			
		outputs.append("{}c{}to{}:  {}".format(r, startcolumn, c-1, errorline[startcolumn:c]))
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
if __name__ == "__main__":	
	htmlfile = "source.html"
	with open(htmlfile, encoding="utf-8") as f:
		s = f.read()  # ファイルから文字列を取得する。
	elem = html2elem(s)  # HTMLをXMLにしてそのルートを取得。
	s = ElementTree.tostring(elem, encoding="unicode")
	outfile = "".join([*htmlfile.split(".")[:-1], ".xml"])  # 出力ファイル名。
	with open(outfile, 'w', encoding='utf-8') as f:  # htmlファイルをUTF-8で作成。すでにあるときは上書き。
		f.writelines(s)  # ファイルに書き出し。
