import requests
from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

def normalize_url(url: str) -> str:
    parsed = urlsplit(url)
    norm_path = parsed.netloc + parsed.path
    if norm_path[-1] == "/":
        norm_path = norm_path[:-1]
    return norm_path

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find("h1") or soup.find("h2")
    if heading is None:
        return ""
    else:
        return heading.getText(strip=True)

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if main is None:
        first_p = soup.find("p")
        if first_p is None:
            return ""
        else:
            return first_p.getText(strip=True)
    else:
        first_p = main.find("p")
        if first_p is None:
            return ""
        else:
            return first_p.getText(strip=True)

def get_urls_from_html(html: str, base_url: str) -> [str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = soup.find_all("a")
    full_urls = []
    for url in urls:
        href = url.get("href")
        full_url = urljoin(base_url, href)
        full_urls.append(full_url)
    return full_urls

def get_images_from_html(html: str, base_url: str) -> [str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = soup.find_all("img")
    full_urls = []
    for url in urls:
        href = url.get("src")
        full_url = urljoin(base_url, href)
        full_urls.append(full_url)
    return full_urls

def extract_page_data(html: str, page_url: str) -> PageData:
    page_data: PageData = {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url)
    }
    return page_data

def get_html(url: str) -> str:
    try:
        response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    except Exception as e:
        raise Exception(f"network error while fetching {url}: {e}")

    if response.status_code > 399:
        raise Exception(f"got HTTP error: {response.status_code} {response.reason}")

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise Exception(f"got non-HTML response: {content_type}")

    return response.text

def crawl_page(base_url, current_url=None, page_data=None):
    base_parsed = urlsplit(base_url)
    if current_url == None:
        current_parsed = base_parsed
        current_url = base_url
    else:
        current_parsed = urlsplit(current_url)

    if base_parsed.hostname != current_parsed.hostname:
        return page_data

    normalized_current =normalize_url(current_url)

    if page_data is None:
        page_data = {}

    if normalized_current in page_data.keys():
        return page_data

    print(f"crawling {current_url}")
    try:
        html = get_html(current_url)
    except Exception:
        return page_data

    page_data[normalized_current] = extract_page_data(html, current_url)

    for url in page_data[normalized_current]["outgoing_links"]:
        crawl_page(base_url, url, page_data)

    return page_data