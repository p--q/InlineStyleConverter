#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re, sys, html
from xml.etree import ElementTree
def htmlToXML(htmlfile, pattern=r".*"):
	regex = re.compile(pattern, re.DOTALL)  # HTMLからXMLに変換する部分を抜き出す正規表現オブジェクト。
	with open(htmlfile, encoding="utf-8") as f:
		s = f.read()  # ファイルから文字列を取得する。
	return convertToXML(s, regex)  # ファイルから正規表現で抽出したHTMLをXMLにしてそのルートを取得。
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
def html2xml(s):  # HTML文字参照をUnicodeに変換する。閉じられていないタグを閉じる。
	txt = html.unescape(s)  # HTML文字参照をUnicodeに変換する。 
	noendtags = "br", "img", "hr", "meta", "input", "embed", "area", "base", "col", "keygen", "link", "param", "source", "wbr", "track"  # ウェブブラウザで保存すると閉じられなくなるタグ。
	noend_regex = re.compile("|".join([r"(?i)(?<=<)\s*?{}.*?(?=>)".format(i) for i in noendtags]))  # 各タグについて正規表現オブジェクトの作成。各タグの<>内のみを抽出する。大文字でも取得する。
	txt = noend_regex.sub(repl, txt)  # マッチングオブジェクトをreplに渡して処理。
	return txt
def repl(m):  # マッチングオブジェクトの処理。
	e = m.group(0).rstrip().lower()  # タグを小文字にする。
	return e if e.endswith("/") else "".join([e, "/"])  # 要素が/で終わっていない時は/で閉じる。
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
		startcolumn = c - maxcolmuns/2
		startcolumn = 0 if startcolumn<0 else startcolumn
		endcolumn = c + maxcolmuns/2
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
	sys.exit()			
if __name__ == "__main__":	
# 	htmlToXML("source.html", r'<div id="tcuheader".*<\/div>')  # htmlファイルと、sytle属性のあるノードを抽出する正規表現を渡す。なるべく<script>や<style>要素が入らないようにする。
	htmlToXML("source.html") 