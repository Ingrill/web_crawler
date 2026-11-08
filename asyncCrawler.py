import asyncio
import aiohttp
from urllib.parse import urlsplit
from crawl import PageData, normalize_url, extract_page_data

class AsyncCrawler:
    base_url:        str
    base_domain:     str
    page_data:       PageData
    visited:         set[str]
    lock:            asyncio.Lock
    max_concurrency: int
    semaphore:       asyncio.Semaphore
    session:         aiohttp.ClientSession
    max_pages:       int
    should_stop:     bool
    all_tasks:       set

    def __init__(self, base_url: str, max_concurrency: int, max_pages: int):
        self.base_url = base_url
        self.base_domain = urlsplit(base_url).netloc
        self.page_data = dict()
        self.visited = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks: set[asyncio.Task[None]] = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if self.should_stop:
                return False
            if normalized_url in self.visited:
                return False
            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                return False
            self.visited.add(normalized_url)
            return True

    async def get_html(self, url: str) -> str:
        try:
            async with self.session.get(url) as response:

                if response.status > 399:
                    raise Exception(f"got HTTP error: {response.status} {response.reason}")

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    raise Exception(f"got non-HTML response: {content_type}")

                return await response.text()

        except Exception as e:
                raise Exception(f"network error while fetching {url}: {e}")

    async def crawl_page(self, current_url: str) -> None:
        if self.should_stop:
            return

        current_url_obj = urlsplit(current_url)
        if current_url_obj.netloc != self.base_domain:
            return

        normalized_url = normalize_url(current_url)

        is_new = await self.add_page_visit(normalized_url)
        if not is_new:
            return

        async with self.semaphore:
            html = await self.get_html(current_url)
            if html is None:
                return

            page_info = extract_page_data(html, current_url)
            async with self.lock:
                self.page_data[normalized_url] = page_info

            next_urls = page_info["outgoing_links"]

        if self.should_stop:
            return

        tasks: list[asyncio.Task[None]] = []
        for next_url in next_urls:
            task = asyncio.create_task(self.crawl_page(next_url))
            tasks.append(task)
            self.all_tasks.add(task)

        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                for task in tasks:
                    self.all_tasks.discard(task)

    async def crawl(self) -> dict[str, PageData]:
        await self.crawl_page(self.base_url)
        return self.page_data


async def crawl_site_async(
    base_url: str, max_concurrency: int, max_pages: int
) -> dict[str, PageData]:
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()