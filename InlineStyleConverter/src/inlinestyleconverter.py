# -*- coding: utf-8 -*-
import re
import html
import sys
from xml.etree import ElementTree


def inlinestyleconverter(htmlfile, pattern=r".*"):  # 正規表現が与えられていない時はすべてのノードについて実行する。
	style_xpath = './/*[@style]'  # sytleのあるノードを取得するXPath。
	with open(htmlfile, encoding="utf-8") as f:
		s = f.read()  # ファイルから文字列を取得する。
		subhtml = re.findall(pattern, s, flags=re.DOTALL)  # XMLに変換するhtmlを取得する。
		if not subhtml:
			print("There is no html matching r'{}'.".format(pattern), file=sys.stderr)
			sys.exit()	
		x = html2xml(subhtml[0])  # 最初にマッチングしたノードのみxmlにする処理をする
		x = "<root>{}</root>".format(x)  # 抜き出したhtmlにルート付ける。一つのノードにまとまっていないとjunk after document elementがでる。
		root = ElementTree.XML(x)  # ElementTreeのElementにする。
		parent_map = parent_map = {c:p for p in root.iter() for c in p if c.tag!="br"}  # 木の、子:親の辞書を作成。brタグはstyle属性のノードとは全く関係ないので除く。
		style_nodes = root.findall(style_xpath)  # style属性をもつノードをすべて取得。
		
			
			
			
			
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
	