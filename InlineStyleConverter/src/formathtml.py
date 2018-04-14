#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
def formatHTML(html):  # HTMLを整形する。
	indentunit = "\t"  # インデントの1単位。
	tagregex = re.compile(r"(?is)<\/?(\w+)(?:(?:\s+[a-zA-Z0-9_\-]+(?:\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)+\s*|\s*)\/?>|(?<=>).+?(?=<)")  # 開始タグと終了タグ、テキストノードすべてを抽出する正規表現オブジェクト。ただし<や>を含んだテキストノードはうまく取得できない。
	replTag = repltagCreator(indentunit)  # マッチオブジェクトを処理する関数を取得。
	html = tagregex.sub(replTag, html)  # script要素とstyle要素以外インデントを付けて整形する。
	scriptregex = re.compile(r'(?is)<\s*?(script|style).*?>(.+?)<\s*?\/\s*?\1\s*?>')  # script要素、style要素のテキストノードを抽出する正規表現パターン。
	replScript = replScriptCreator(indentunit)
	html = scriptregex.sub(replScript, html)  # script要素とstyle要素をを整形する。
	return html[1:] if html.startswith("\n") else html  # 先頭の改行を削除して返す。
def repltagCreator(indentunit):  # 開始タグと終了タグのマッチオブジェクトを処理する関数を返す。
	c = 0  # インデントの数。
	starttagtype = ""  # 開始タグと終了タグが対になっているかを確認するため開始タグの要素型をクロージャに保存する。
	noendtags = "br", "img", "hr", "meta", "input", "embed", "area", "base", "col", "keygen", "link", "param", "source", "wbr", "track"  # HTMLでは終了タグがなくなるタグ。
	def replTag(m):  # 開始タグと終了タグのマッチオブジェクトを処理する関数。
		nonlocal c, starttagtype
		txt = m.group(0)  # マッチした文字列を取得。
		if txt.startswith("</"):  # 終了タグの時。
			c -= 1  # インデントの数を減らす。
			if m.group(1)!=starttagtype:  # 開始タグと同じ要素型ではない時。
				txt = "\n{}{}".format(indentunit*c, txt)  # タグの前で改行してインデントする。
			starttagtype = ""  # 開始タグの要素型をリセットする。
		elif txt.startswith("<"):  # 開始タグの時。
			txt = "\n{}{}".format(indentunit*c, txt)  # 開始タグの前で改行してインデントする。
			tagtype = m.group(1)  # 要素型を取得。
			if tagtype in noendtags:  # 終了タグのないタグの時。 
				starttagtype = ""  # 開始タグの要素型をリセットする。
			else:  # 終了タグのないタグでない時。 
				starttagtype = tagtype  # タグの要素型をクロージャに取得。
				c += 1  # インデントの数を増やす。
		else:  # テキストノードの時。
			if not txt.strip():  # 改行や空白だけのとき。
				return ""  # 削除する。
			if "\n" in txt: # テキストノードが複数行に渡る時。
				newbreak = "\n{}".format(indentunit*c)  # 改行とインデントを作成。
				if starttagtype in ("script", "style"):  # scriptやstyleノードの時。
					txt = "".join([newbreak, txt])  # 先頭にだけ改行とインデントを挿入する。テキストノードすべてを取得できないときがあるので。
				else:
					txt = txt[:-1] if txt.endswith("\n") else txt  # 最後の改行を除く。
					txt = "".join([newbreak, txt.replace("\n", newbreak), "\n", indentunit*(c-1)])  # 全行をインデントする。
			elif not starttagtype:  # 開始タグに続くテキストノードではない時。
				txt = "\n{}{}".format(indentunit*c, txt)  # 前で改行してインデントする。
		return txt
	return replTag
def replScriptCreator(indentunit):
	def replScript(m):  # マッチしたscript要素とstyle要素を整形する。
		txt = m.group(2).rstrip()  # テキストノードを取得。最後の改行や空白を削除する。
		if "\n" in txt:  # 複数行ある時。
			lines = txt.split("\n")  # テキストノードを各行のリストにする。
			headerlength = len(lines[1]) - len(lines[1].lstrip())  # インデントの長さを取得。
			indent = lines[1][:headerlength]  # 2行目からインデントを取得。
			newbreak = "\n{}".format(indent)
			tagindent = indent[:-len(indentunit)]  # 終了タグ用のインデントを作成。
			tagtype = m.group(1)  # 要素型を取得。
			return "".join(["<{}>\n".format(tagtype), lines[0], newbreak.join(lines[1:]), "\n", tagindent, "</{}>".format(tagtype)])  # 全行をインデントして返す。
		return txt  # 1行しかないときはそのまま返す。
	return replScript
if __name__ == "__main__":
	htmlfile = "p--q.html"
	htmlfile = "source.html"
	with open(htmlfile, encoding="utf-8") as f:
		s = f.read()  # ファイルから文字列を取得する。	
	print(formatHTML(s))