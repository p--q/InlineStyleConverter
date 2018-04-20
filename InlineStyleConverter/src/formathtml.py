#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re, html
def formatHTML(s, reset=None):  # HTMLを整形する。第2引数があるときはすでにあるインデントを除去する。
	if reset is not None:  # 第2引数がある時。
		s = re.sub(r'(?<=>)\s+?(?=<)', "", s)  # 空文字だけのtextとtailを削除してすでにあるインデントをリセットする。
	indentunit = "\t"  # インデントの1単位。
	tagregex = re.compile(r"(?s)<(?:\/?(\w+).*?\/?|!--.*?--)>|(?<=>).+?(?=<)")  # 開始タグと終了タグ、コメント、テキストノードすべてを抽出する正規表現オブジェクト。ただし<を含んだテキストノードはそこまでしか取得できない。
	replTag = repltagCreator(indentunit)  # マッチオブジェクトを処理する関数を取得。
	s = html.unescape(s)  # HTMLの文字参照をユニコードに戻す。
	s = tagregex.sub(replTag, s)  # script要素とstyle要素以外インデントを付けて整形する。
	return s.lstrip("\n")  # 先頭の改行を削除して返す。
def repltagCreator(indentunit):  # 開始タグと終了タグのマッチオブジェクトを処理する関数を返す。
	starttagregex = re.compile(r'<\w+.*?>')  # 開始タグ。
	endendtagregex = re.compile(r'<\/\w+>$')  # 終了タグで終わっているか。 
	noendtags = "br", "img", "hr", "meta", "input", "embed", "area", "base", "col", "link", "param", "source", "wbr", "track"  # HTMLでは終了タグがなくなるタグ。
	c = 0  # インデントの数。
	starttagtype = ""  # 開始タグと終了タグが対になっているかを確認するため開始タグの要素型をクロージャに保存する。
	txtnodeflg = False  # テキストノードを処理したときに立てるフラグ。テキストノードが分断されたときのため。
	def replTag(m):  # 開始タグと終了タグのマッチオブジェクトを処理する関数。
		nonlocal c, starttagtype, txtnodeflg  # 変更するクロージャ変数。
		txt = m.group(0)  # マッチした文字列を取得。
		tagtype = m.group(1)  # 要素型を取得。Noneのときもある。
		tagtype = tagtype and tagtype.lower()  # 要素型を小文字にする。
		if tagtype in noendtags:  # 空要素の時。開始タグと区別がつかないのでまずこれを最初に判別する必要がある。
			txt = "".join(["\n", indentunit*c, txt])  # タグの前で改行してインデントする。
			starttagtype = ""  # 開始タグの要素型をリセットする。		
			txtnodeflg = False  # テキストノードのフラグを倒す。	
		elif txt.endswith("</{}>".format(tagtype)):  # 終了タグの時。
			c -= 1  # インデントの数を減らす。
			if tagtype!=starttagtype:  # 開始タグと同じ要素型ではない時。
				txt = "".join(["\n", indentunit*c, txt])  # タグの前で改行してインデントする。
			starttagtype = ""  # 開始タグの要素型をリセットする。
			txtnodeflg = False  # テキストノードのフラグを倒す。			
		elif starttagregex.match(txt) is not None:  # 開始タグの時。
			txt = "".join(["\n", indentunit*c, txt])  # タグの前で改行してインデントする。
			starttagtype = tagtype  # タグの要素型をクロージャに取得。
			c += 1  # インデントの数を増やす。
			txtnodeflg = False  # テキストノードのフラグを倒す。		
		elif txt.startswith("<!--"):  # コメントの時。
			pass  # そのまま返す。
		else:  # 上記以外はテキストノードと判断する。
			if not txt.strip():  # 改行や空白だけのとき。
				txt = ""  # 削除する。
			if "\n" in txt: # テキストノードが複数行に渡る時。
				txt = txt.rstrip("\n").replace("\n", "".join(["\n", indentunit*c]))  # 最後の改行を除いたあと全行をインデントする。
				if not txtnodeflg:  # 直前に処理したのがテキストノードではない時。
					txt = "".join(["\n", indentunit*c, txt])  # 前を改行してインデントする。		
				if endendtagregex.search(txt):  # 終了タグで終わっている時。テキストノードに<があるときそうなる。
					c -= 1  # インデントを一段上げる。
					txt = endendtagregex.sub(lambda m: "".join(["\n", indentunit*c, m.group(0)]), txt)  # 終了タグの前を改行してインデントする。
				starttagtype = ""  # 開始タグの要素型をリセットする。開始タグと終了タグが一致しているままだと終了タグの前で改行されないため。
			elif not starttagtype:  # 単行、かつ、開始タグが一致していない時。
				txt = "".join(["\n", indentunit*c, txt])  # テキストノードの前で改行してインデントする。
			txtnodeflg = True  # テキストノードのフラグを立てる。
		return txt
	return replTag
if __name__ == "__main__":
	htmlfile = "source.html"
	with open(htmlfile, encoding="utf-8") as f:
		s = f.read()  # ファイルから文字列を取得する。
	s = formatHTML(s)	
	outfile = "formatted_{}".format(htmlfile)  # 出力ファイル名。
	with open(outfile, 'w', encoding='utf-8') as f:  # htmlファイルをUTF-8で作成。すでにあるときは上書き。
		f.writelines(s)  # ファイルに書き出し。