import aiohttp
import urllib.parse


def request(url, method='get', **kwargs):

    return aiohttp.request(method, url, **kwargs)


def get_session():

    return aiohttp.Session()