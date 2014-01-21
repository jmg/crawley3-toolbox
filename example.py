from src.crawlers import BaseCrawler
import asyncio
import sys
import signal


class PyCrawler(BaseCrawler):

    start_url = "http://python.org"


if __name__ == "__main__":

    crawler = PyCrawler(debug=True)
    crawler.start()