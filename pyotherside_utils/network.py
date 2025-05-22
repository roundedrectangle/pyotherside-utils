from __future__ import annotations

import os, shutil
from pathlib import Path
from typing import TYPE_CHECKING, Iterator
import urllib.parse, urllib.request, urllib.error

try:
    import httpx
    HTTPX_AVAILABLE = True
except: HTTPX_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except: REQUESTS_AVAILABLE = False

if TYPE_CHECKING:
    import httpx, requests

from . import show_error, exception_safe, ExceptionHandlingInfo, DataFromException

def generate_headers(user_agent=None):
    return {
        "User-Agent": "python-requests/2.32.3" if user_agent is None else user_agent,
        #"Accept-Encoding": "gzip,deflate",
        #"Accept": "*/*",
        "Connection": "keep-alive",
    }

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

DOWNLOAD_CHUNK_SIZE = 1024*1024 # 1mb

def stream_urllib(url, proxies=None, user_agent=None):
    """Returns same as urllib.request.urlopen() or None if URL is invalid"""
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
        r = opener.open(urllib.request.Request(str(url), headers=generate_headers(user_agent)))
        if r.status != 200: return
        return r
    except urllib.error.URLError as e:
        show_error('cacheConnection', e)
    except Exception as e:
        show_error('cache', f'{type(e)}: {e}')

def stream_httpx(url, proxies=None, client: httpx.Client | None = None, user_agent=None):
    headers = {'User-Agent': user_agent} if user_agent is not None else None
    if client:
        context = client.stream('get', url, headers=headers)
    elif HTTPX_AVAILABLE:
        context = httpx.stream('get', url, headers=headers, proxy=proxies)
    else: return
    with context as r:
        for chunk in r.iter_bytes(DOWNLOAD_CHUNK_SIZE):
            yield chunk

def stream_requests(url, proxies=None, user_agent=None):
    headers = {'User-Agent': user_agent} if user_agent is not None else None
    if REQUESTS_AVAILABLE:
        try: r = requests.get(url, stream=True, proxies=proxies, headers=headers)
        except requests.ConnectionError as e:
            show_error('cacheConnection', str(e))
            return
        except requests.RequestException as e:
            show_error('cache', str(type(e)), str(e))
            return
        if r.status_code == 200:
            return iter(r)

if HTTPX_AVAILABLE:
    stream_httpx = exception_safe({httpx.HTTPError: ExceptionHandlingInfo('cacheConnection', DataFromException.str_exception)})(stream_httpx) # pyright:ignore[reportAssignmentType]
stream_httpx = exception_safe({Exception: ExceptionHandlingInfo('cache', lambda e: f'{type(e)}: {e}')})(stream_httpx) # pyright:ignore[reportAssignmentType]

def save_iterator(iterator: Iterator[bytes | str] | None, destination: Path | str):
    os.remove(destination)
    if iterator:
        for chunk in iterator:
            with open(destination, 'a' + ('b' if isinstance(chunk, bytes) else '')) as f:
                f.write(chunk)
        return True
    return False

def save_file_like(file, destination: Path | str):
    if file:
        with open(destination, 'wb') as f:
            shutil.copyfileobj(file, f, DOWNLOAD_CHUNK_SIZE)
        return True
    return False

def download_save(
    url,
    destination: Path | str,
    proxies: dict | None = None,
    user_agent: str | None = None,
    httpx_client: httpx.Client | None = None,
):
    if httpx_client or HTTPX_AVAILABLE:
        return save_iterator(stream_httpx(url, proxies, httpx_client, user_agent), destination)
    elif REQUESTS_AVAILABLE:
        return save_iterator(stream_requests(url, proxies, user_agent), destination)
    else:
        return save_file_like(stream_urllib(url, proxies, user_agent), destination)

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
    
    def __init__(self, proxy: str | None = None, user_agent: str | None = None, httpx_client: httpx.Client | None = None):
        self.proxies = {}
        self._proxy: str | None = None
        self.proxy = proxy
        self.user_agent = user_agent
        self.httpx_client = httpx_client
    
    def download_save(self, url, dest):
        return download_save(url, dest, self.proxies, self.user_agent, self.httpx_client)