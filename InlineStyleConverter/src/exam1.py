# -*- coding: utf-8 -*- 

# import urllib.request, urllib.error, urllib.parse
from html.parser import HTMLParser

class TestParser(HTMLParser): # HTMLParserを継承したクラスを定義する

	def __init__(self):
		HTMLParser.__init__(self)
		self.flag = False # タイトルタグの場合のフラグ

	def handle_starttag(self, tag, attrs): # 開始タグを扱うためのメソッド
		if tag == "body":
			self.flag = True

	def handle_data(self, data): # 要素内用を扱うためのメソッド
		if self.flag:
			print(data)
			self.flag = False

if __name__ == "__main__":

#	 url = "http://www.python.org/"
# 
#	 response = urllib.request.urlopen(url)
	
	parser = TestParser()		# パーサオブジェクトの生成
#	 parser.feed(response.read()) # パーサにHTMLを入力する
	parser.feed('<body><p><a class=link href=#main>tag soup</p ></a></body>')
	parser.close()
#	 response.close()