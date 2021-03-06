# インポート
import json
import base64
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
import pathlib
import urllib.request
import zipfile
import io

# 定数類
SOURCE_URL = 'https://dev.soracom.io/files/SIS_SVG.zip'
SOURCE_DIR = pathlib.Path(__file__).parent / 'build' / 'svg'
OUTPUT_DIR = pathlib.Path(__file__).parent / 'dist' / 'output'
FILE_NAME_FORMAT = 'SORACOM アイコンセット({}).xml'
FILE_ROOT_FORMAT = '<mxlibrary>{}</mxlibrary>'
MX_GRAPH_FORMAT = '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="2" value="" style="shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,{}" vertex="1" parent="1"><mxGeometry width="{}" height="{}" as="geometry"/></mxCell></root></mxGraphModel>'
VIEW_BOX_INDEX_WIDTH = 2
VIEW_BOX_INDEX_HEIGHT = 3
COLOR = {
    'BK': '黒',
    'CL': 'チェレステブルー',
    'GY': 'グレー',
    'WH': 'ホワイト',
}

# global初期化
ET.register_namespace('', 'http://www.w3.org/2000/svg')
# https://stackoverflow.com/questions/18338807/cannot-write-xml-file-with-default-namespace/18340978
# FIXME デフォルトネームスペースがtostringのほうで使えてよいはずだが、、、暫定回避


def convertSVG(source):
    # 元になるSVGをbase64でエンコードする。ついでにviewBoxから高さと幅を取る
    root = ET.parse(source).getroot()
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

    return {
        'xml': jsonValueXML,
        'w': viewBox[VIEW_BOX_INDEX_WIDTH],
        'h': viewBox[VIEW_BOX_INDEX_HEIGHT],
        'title': source.stem,
        'aspect': 'fixed'
    }


def makeTemplateFile(sorceDir):
    rootArray = []
    for child in sorceDir.iterdir():
        if '.svg' == child.suffix:
            rootArray.append(convertSVG(child))

    (OUTPUT_DIR / FILE_NAME_FORMAT.format(sorceDir.name)).write_text(
        FILE_ROOT_FORMAT.format(json.dumps(rootArray))
    )


def getRemoteSourceFile():
    req = urllib.request.Request(SOURCE_URL)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    with zipfile.ZipFile(io.BytesIO(body)) as existing_zip:
        existing_zip.extractall(SOURCE_DIR)


def main():
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    #使い捨て環境想定のためざっくり作る

    #getRemoteSourceFile()

    for child in (SOURCE_DIR / 'SIS_SVG').iterdir(): makeTemplateFile(child)

if __name__ == "__main__":
    main()
