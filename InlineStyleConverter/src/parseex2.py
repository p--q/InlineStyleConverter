# -*- coding: utf-8 -*-

from html.parser import HTMLParser
# from html.entities import name2codepoint

class MyHTMLParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.flag = False

	def handle_starttag(self, tag, attrs):
		if tag=="body":
			self.flag = True
		
		
# 		print("Start tag:", tag)
# 		for attr in attrs:
# 			print("	 attr:", attr)

# 	def handle_endtag(self, tag):
# 		print("End tag  :", tag)

	def handle_data(self, data):
		if self.flag:
			print(data)
			self.flag = False
		
		
# 		print("Data	 :", data)

# 	def handle_comment(self, data):
# 		print("Comment  :", data)

# 	def handle_entityref(self, name):
# 		c = chr(name2codepoint[name])
# 		print("Named ent:", c)

# 	def handle_charref(self, name):
# 		if name.startswith('x'):
# 			c = chr(int(name[1:], 16))
# 		else:
# 			c = chr(int(name))
# 		print("Num ent  :", c)

# 	def handle_decl(self, data):
# 		print("Decl	 :", data)

parser = MyHTMLParser()

parser.feed('<body><p><a class=link href=#main>tag soup</p ></a></body>')

