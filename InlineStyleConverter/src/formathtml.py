#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re, html
def formatHTML(s):  # HTMLを整形する。
	s = html.unescape(s)
	indentunit = "\t"  # インデントの1単位。
	tagregex = re.compile(r"(?s)<\/?(\w+).*?\/?>|<!--.*?-->|(?<=>).+?(?=<)")  # 開始タグと終了タグ、コメント、テキストノードすべてを抽出する正規表現オブジェクト。ただし<や>を含んだテキストノードはうまく取得できない。
	replTag = repltagCreator(indentunit)  # マッチオブジェクトを処理する関数を取得。
	s = tagregex.sub(replTag, s)  # script要素とstyle要素以外インデントを付けて整形する。
	scriptregex = re.compile(r'(?is)<(script|style).*?>(.+?)<\/\1>')  # script要素、style要素のテキストノードを抽出する正規表現パターン。
	replScript = replScriptCreator(indentunit)
	s = scriptregex.sub(replScript, s)  # script要素とstyle要素をを整形する。
	return s[1:] if s.startswith("\n") else s  # 先頭の改行を削除して返す。
def repltagCreator(indentunit):  # 開始タグと終了タグのマッチオブジェクトを処理する関数を返す。
	commentregex = re.compile(r'<!--.*?-->')  # コメント。
	emptytagregex = re.compile(r"<(\w+)(?:\s+[a-zA-Z0-9_\-]+\s*=\s*(?:(?:\".*?\")|(?:'.*?'))\s*)?\/>")  # />で終わる空要素。正式のHTMLにはないはず。
	starttagregex = re.compile(r"<(\w+)(?:\s+[a-zA-Z0-9_\-]+\s*=\s*(?:(?:\".*?\")|(?:'.*?'))\s*)?>")  # 開始タグ。
	endtagregex = re.compile(r'<\/(\w+)>')  # 終了タグ。 
	endendtagregex = re.compile(r'<\/(\w+)>$')  # 終了タグで終わっているか。 
	noendtags = "br", "img", "hr", "meta", "input", "embed", "area", "base", "col", "keygen", "link", "param", "source", "wbr", "track"  # HTMLでは終了タグがなくなるタグ。
	c = 0  # インデントの数。
	starttagtype = ""  # 開始タグと終了タグが対になっているかを確認するため開始タグの要素型をクロージャに保存する。
	txtnodeflg = False  # テキストノードを処理したときに立てるフラグ。テキストノードが分断されたときのため。
	def replTag(m):  # 開始タグと終了タグのマッチオブジェクトを処理する関数。
		nonlocal c, starttagtype, txtnodeflg
		txt = m.group(0)  # マッチした文字列を取得。
		tagtype = m.group(1)  # 要素型を取得。
		if commentregex.match(txt):  # コメントの時。
			pass  # そのまま返す。
		elif endtagregex.match(txt):  # 終了タグの時。
			c -= 1  # インデントの数を減らす。
			if m.group(1)!=starttagtype:  # 開始タグと同じ要素型ではない時。
				txt = "\n{}{}".format(indentunit*c, txt)  # タグの前で改行してインデントする。
			starttagtype = ""  # 開始タグの要素型をリセットする。
			txtnodeflg = False
		elif tagtype in noendtags or emptytagregex.match(txt):  # 空要素の時。
			txt = "\n{}{}".format(indentunit*c, txt)  # タグの前で改行してインデントする。
			starttagtype = ""  # 開始タグの要素型をリセットする。					
		elif starttagregex.match(txt):  # 開始タグの時。
			txt = "\n{}{}".format(indentunit*c, txt)  # 開始タグの前で改行してインデントする。
			starttagtype = tagtype  # タグの要素型をクロージャに取得。
			c += 1  # インデントの数を増やす。
			txtnodeflg = False
		else:  # テキストノードの時。
			if not txt.strip():  # 改行や空白だけのとき。
				return ""  # 削除する。
			if "\n" in txt: # テキストノードが複数行に渡る時。
				newbreak = "\n{}".format(indentunit*c)  # 改行とインデントを作成。
				if starttagtype in ("script", "style"):  # scriptやstyleノードのテキストノードの時。
					if not txtnodeflg:  # 直前に処理したのがテキストノードでない時のみ。
						txt = "".join([newbreak, txt])  # 先頭にだけ改行とインデントを挿入する。テキストノードすべてを取得できないときがあるので。
				else:
					txt = txt[:-1] if txt.endswith("\n") else txt  # 最後の改行を除く。
					if txtnodeflg:  # 前回処理したのがテキストノードの時。
						txt = "".join([txt.replace("\n", newbreak), "\n", indentunit*(c-1)])  # 先頭行以外の全行をインデントする。
					else:  # 前回処理したのがテキストノードでない時のみ。
						txt = "".join([newbreak, txt.replace("\n", newbreak), "\n", indentunit*(c-1)])  # 全行をインデントする。
			elif not starttagtype:  # 開始タグに続くテキストノードではない時。
				txt = "\n{}{}".format(indentunit*c, txt)  # 前で改行してインデントする。
			if txtnodeflg and endendtagregex.search(txt):  # 終了タグで終わっている時。テキストノードに<が入っている時に該当。
				c -= 1  # インデントを減らす。
			txtnodeflg = True
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
# 	htmlfile = "p--q.html"
	htmlfile = "source.html"
# 	htmlfile = "tem.html"
	with open(htmlfile, encoding="utf-8") as f:
		s = f.read()  # ファイルから文字列を取得する。
	s = formatHTML(s)	
	outfile = "formatted_{}".format(htmlfile)  # 出力ファイル名。
	with open(outfile, 'w', encoding='utf-8') as f:  # htmlファイルをUTF-8で作成。すでにあるときは上書き。
		f.writelines(s)  # ファイルに書き出し。
# 	print(s)