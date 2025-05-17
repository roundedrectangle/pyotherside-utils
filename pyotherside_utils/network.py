import urllib.parse

__ALL__ = [
    'convert_proxy',
    'isurl',
]

def convert_proxy(proxy):
    if not proxy:
        return

    p = urllib.parse.urlparse(proxy, 'http') # https://stackoverflow.com/a/21659195
    netloc = p.netloc or p.path
    path = p.path if p.netloc else ''
    p = urllib.parse.ParseResult('http', netloc, path, *p[3:])

    return p.geturl()

def isurl(obj: str):
    """Returns True if an object is an internet URL"""
    return urllib.parse.urlparse(obj).scheme != '' #not in ('file','')