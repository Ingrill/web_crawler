import unittest
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html, extract_page_data


class TestNormalize(unittest.TestCase):
    def test_normalize_url_https1(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_https2(self):
        input_url = "https://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_http1(self):
        input_url = "http://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_http2(self):
        input_url = "http://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

class TestGetHeading(unittest.TestCase):
    def test_get_heading_h1(self):
        input_html = "<h1>Hello world</h1>"
        actual = get_heading_from_html(input_html)
        expected = "Hello world"
        self.assertEqual(actual, expected)

    def test_get_heading_h2(self):
        input_html = "<h2>Hello world</h2>"
        actual = get_heading_from_html(input_html)
        expected = "Hello world"
        self.assertEqual(actual, expected)

    def test_get_heading_no_h1_h2(self):
        input_html = "<b>Hello world</b>"
        actual = get_heading_from_html(input_html)
        expected = ""
        self.assertEqual(actual, expected)

class TestParagraph(unittest.TestCase):
    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_no_paragraph(self):
        input_body = """<html><body>
            <main>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

class TestGetUrls(unittest.TestCase):
    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/home"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/home"]
        self.assertEqual(actual, expected)

    def test_get_two_urls_from_html(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/home"><span>Boot.dev</span></a><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/home", "https://crawler-test.com"]
        self.assertEqual(actual, expected)

class TestGetImages(unittest.TestCase):
    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)
    
    def test_get_images_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://crawler.com/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_two_images_from_html(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"><img src="https://crawler.com/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png", "https://crawler.com/logo.png"]
        self.assertEqual(actual, expected)

class TestExtractPageData(unittest.TestCase):
    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data(self):
        input_url = "https://crawler.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <h2>Test sub Title</h2>
            <p>This is the first paragraph.</p>
            <p>This is the second paragraph.</p>
            <a href="/link1">Link 1</a>
            <a href="https://boot.dev/">Boot.dev</a>
            <img src="/image1.jpg" alt="Image 1">
            <img src="https://example.com/image1.jpg" alt="Image 2">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler.com/link1", "https://boot.dev/"],
            "image_urls": ["https://crawler.com/image1.jpg", "https://example.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()