from src.crawlers import BaseCrawler


class PyCrawler(BaseCrawler):

    start_urls = ["http://python.org"]


if __name__ == "__main__":

    crawler = PyCrawler(debug=True)
    crawler.start()