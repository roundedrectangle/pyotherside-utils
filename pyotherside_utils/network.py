import os, shutil
from pathlib import Path
import urllib.parse, urllib.request, urllib.error

from . import qsend

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

DOWNLOAD_CHUNK_SIZE = 1024

def download(url, proxies: dict | None):
    """Returns same as urllib.request.urlopen() or None if URL is invalid"""
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
        r = opener.open(str(url))
        if r.status != 200: return
        return r
    except urllib.error.URLError as e:
        qsend('error', 'cacheConnection', str(e))
    except Exception as e:
        qsend('error', 'cache', f'{type(e)}: {e}')

def download_save(url, destination: Path | str, proxies: dict | None):
    r = download(url, proxies)
    if r:
        with open(destination, 'wb') as f:
            shutil.copyfileobj(r, f, DOWNLOAD_CHUNK_SIZE)
        return True
    return False

def get_extension_from_url(url: str, default='png'):
    res = os.path.splitext(urllib.parse.urlparse(url).path)[1]
    if res.startswith('.'): # removeprefix() was sadly introduced in python 3.9
        res = res[1:]
    return res or default

class DownloadManager:
    @property
    def proxy(self):
        return self._proxy

    @proxy.setter
    def proxy(self, value: str | None):
        self._proxy = value
        if value == None:
            self.proxies = {}
        else:
            self.proxies = {
                "http": value,
                "https": value,
            }
    
    def __init__(self, proxy: str | None = None):
        self.proxies = {}
        self._proxy: str | None = None
        self.proxy = proxy
    
    def download_save(self, url, dest):
        return download_save(url, dest, self.proxies)