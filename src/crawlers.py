import re
import signal
import sys
import asyncio
import urllib.parse

from .http import request, get_session


class BaseCrawler:
    """
        Base crawler adapted from https://github.com/fafhrd91/aiohttp/blob/master/examples/crawl.py
        Thanks https://github.com/fafhrd91 :-)
    """

    start_urls = []

    def __init__(self, maxtasks=100, debug=False, session=None, use_iocp=False):

        self.loop = asyncio.get_event_loop()
        self.todo = set()
        self.busy = set()
        self.done = {}
        self.tasks = set()
        self.sem = asyncio.Semaphore(maxtasks)
        self.debug = debug

        # session stores cookies between requests and uses connection pool
        if session is None:
            session = get_session()

        self.session = session

        if use_iocp:
            asyncio.events.set_event_loop(asyncio.windows_events.ProactorEventLoop())            

    def start(self):

        for url in self.start_urls:

            self.loop.add_signal_handler(signal.SIGINT, self.loop.stop)
            asyncio.Task(self._run(url))
            self.loop.run_forever()

    @asyncio.coroutine
    def _run(self, url):

        asyncio.Task(self._add_urls([(url, '')]))  # Set initial work.
        yield from asyncio.sleep(1)
        while self.busy:
            yield from asyncio.sleep(1)

        self.session.close()
        self.loop.stop()

    @asyncio.coroutine
    def _add_urls(self, urls):

        for url, parenturl in urls:

            url = urllib.parse.urljoin(parenturl, url)
            url, frag = urllib.parse.urldefrag(url)

            if url in self.busy or url in self.done or url in self.todo:
                continue

            self.todo.add(url)
            yield from self.sem.acquire()
            task = asyncio.Task(self._process(url))
            task.add_done_callback(lambda t: self.sem.release())
            task.add_done_callback(self.tasks.remove)
            self.tasks.add(task)

    @asyncio.coroutine
    def _process(self, url):

        if self.debug:
            print('Crawling ->', url)

        self.todo.remove(url)
        self.busy.add(url)
        try:
            response = yield from request(url)
        except Exception as exc:
            print('...', url, 'has error', repr(str(exc)))
            self.done[url] = False
        else:
            if response.status == 200 and response.get_content_type() == 'text/html':
                data = (yield from response.read()).decode('utf-8', 'replace')
                urls = re.findall(r'(?i)href=["\']?([^\s"\'<>]+)', data)
                asyncio.Task(self._add_urls([(u, url) for u in urls]))

            response.close()
            self.done[url] = True

        self.busy.remove(url)

        if self.debug:
            print (len(self.done), 'completed tasks,', len(self.tasks), 'still pending, todo', len(self.todo))