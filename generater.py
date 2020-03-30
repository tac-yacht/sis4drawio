# インポート
import gzip
import json
import base64
import urllib.parse
import xml.etree.ElementTree as ET
import zlib

# 定数類
MX_GRAPH_FORMAT = '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="2" value="" style="shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,{}" vertex="1" parent="1"><mxGeometry width="{}" height="{}" as="geometry"/></mxCell></root></mxGraphModel>'
VIEW_BOX_INDEX_WIDTH = 2
VIEW_BOX_INDEX_HEIGHT = 3


ET.register_namespace('', 'http://www.w3.org/2000/svg')
# https://stackoverflow.com/questions/18338807/cannot-write-xml-file-with-default-namespace/18340978
# FIXME デフォルトネームスペースがtostringのほうで使えてよいはずだが、、、暫定回避
rootArray = []

fileName = 'SIS0003-交換局.svg'
# 元になるSVGをbase64でエンコードする。ついでにviewBoxから高さと幅を取る
tree = ET.parse('R:/SIS_SVG/BK/' + fileName)
root = tree.getroot()
viewBox = root.attrib['viewBox'].split()

rawSVG = ET.tostring(root, encoding='UTF-8')
# https://docs.python.org/ja/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.tostring

escapeSVG = base64.b64encode(rawSVG).decode('ascii')

# 生xmlは URLエンコード、Deflate、Base64の順で符号化
# https://drawio-app.com/extracting-the-xml-from-mxfiles/
rawXML = MX_GRAPH_FORMAT.format(
    escapeSVG, viewBox[VIEW_BOX_INDEX_WIDTH], viewBox[VIEW_BOX_INDEX_HEIGHT])
escapeXML = urllib.parse.quote(rawXML)
# https://docs.python.org/ja/3/library/urllib.parse.html#urllib.parse.quote

compressXML = zlib.compress(escapeXML.encode('ascii'))[2:-4]
# https://docs.python.org/ja/3/library/zlib.html#zlib.compress
# https://stackoverflow.com/questions/1089662/python-inflate-and-deflate-implementations

jsonValueXML = base64.b64encode(compressXML).decode('ascii')

jsonNode = {
    'xml': jsonValueXML,
    'w': viewBox[VIEW_BOX_INDEX_WIDTH],
    'h': viewBox[VIEW_BOX_INDEX_HEIGHT],
    'title': fileName.split('.')[0],
    'aspect': 'fixed'
}

rootArray.append(jsonNode)