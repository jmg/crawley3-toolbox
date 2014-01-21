Crawley3 Toolbox
================

Crawley Toolbox implementation for python3 using asyncio.

###Requirements

- python >= 3.3
- asyncio
- aiohttp

###Example


```python
from src.crawlers import BaseCrawler

class PyCrawler(BaseCrawler):

    start_urls = ["http://python.org"]

if __name__ == "__main__":
    crawler = PyCrawler(debug=True)
    crawler.start()
```
