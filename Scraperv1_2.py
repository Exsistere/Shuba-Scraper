import requests
import json
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
from itertools import zip_longest
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
class ScraperConfig:
    BASE_URL = "https://www.69yuedu.net"
    BASE_URL1 = "https://www.69shuba.com"
    CACHE_FILE = "scraped_data_v1_2.json" 
    KEYWORD =" "##enter the keywowrd
    USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    ]
    CLEAR_COOKIES_AFTER = 5


class ScraperSession:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.request_count = 0
        self.update_headers()

    def update_headers(self):
        self.session.headers.update({
            "User-Agent": random.choice(self.config.USER_AGENTS),
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        })
    def clear_cookies(self):
        self.session.cookies.clear()
        self.session = requests.Session()
        self.update_headers()
        self.request_count = 0

    def get(self, url):
        if self.request_count >= self.config.CLEAR_COOKIES_AFTER:
            self.clear_cookies()
            self.request_count = 0
        self.request_count += 1
        time.sleep(random.uniform(2, 6))
        return self.session.get(url, headers=self.session.headers, timeout=20)
    
    def random_delay(self):
        time.sleep(random.uniform(2, 6))

class Cache:
    def __init__(self, config):
        self.config = config

    def load_cache(self):
        if os.path.exists(self.config.CACHE_FILE):
            with open(self.config.CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"books": [], "chapters": {}}

    def save_cache(self, cache_data):
        with open(self.config.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4)

class BookListUrl:
    def __init__(self, config):
        self.config = config

    def shuba_book_list(self):
        return f"{self.config.BASE_URL1}/novels/class/3.htm"
    
    def yuedu_book_list(self):
        pass
        

class BookScraper:
    def __init__(self, session, config, cache,):
        self.session = session
        self.config = config
        self.cache = cache

    def get_all_books(self, BookListUrl):
        # move your logic from `get_all_books()` here
        cache = self.cache.load_cache()
        book_urls = set()
        page = 1
        while True:
            ##print(page)
            page_book_url = set()
            if page == 1:
                if "novels/" in BookListUrl:
                    response = self.session.get(BookListUrl)
                elif "articlelist/" in BookListUrl:
                    pass
                    


                """yuedu_book_list_url = f"{self.config.BASE_URL}/articlelist/class/0.html"  # Modify if needed
                shuba_book_list_url = f"{self.config.BASE_URL1}/novels/class/0.htm"
                response = self.session.get(yuedu_book_list_url)
                response1 = self.session.get(shuba_book_list_url)"""
                if response.status_code != 200:
                    print("❌ Failed to fetch book list")
                    return []
            else:
                if "novels/" in BookListUrl:
                    book_list_url = f"{self.config.BASE_URL1}/ajax_novels/class/3/{page}.htm"
                    response = self.session.get(book_list_url)
                elif "articlelist/" in BookListUrl:
                    book_list_url = f"{self.config.BASE_URL}/ajax_articlelist/full/0/{page}.htm"
                    response = self.session.get(book_list_url)
 
                """yuedu_book_list_url = f"{self.config.BASE_URL}/ajax_articlelist/full/0/{page}.htm"
                shuba_book_list_url = f"{self.config.BASE_URL1}/ajax_novels/class/0/{page}.htm"""

            
            self.session.random_delay()
            """response = self.session.get(yuedu_book_list_url)
            response1 = self.session.get(shuba_book_list_url)
            
            yuebu_soup = BeautifulSoup(response.text, "html.parser")
            shuba_soup = BeautifulSoup(response1.text, "html.parser")
            # Extract book links (Modify selector if needed)
            for link1, link2 in zip_longest(yuebu_soup.find_all("a", href=True), shuba_soup.find_all("a", href=True)):

                if link1 and "/article/" in link1["href"]:  # Adjust based on actual URL structure 
                    full_url = self.config.BASE_URL + link1["href"]
                    if full_url not in cache["books"]:  # Skip already scraped books
                        page_book_url.add(full_url)

                if link2 and "/book/" in link2["href"]:  # Adjust based on actual URL structure
                    full_url = link2["href"]
                    if full_url not in cache["books"]:  # Skip already scraped books
                        page_book_url.add(full_url)"""

            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href = True):
                if link and "/book/" in link["href"]:
                    full_url = link["href"]
                    if full_url not in cache["books"]:
                        page_book_url.add(full_url)
            if not page_book_url or page == 31:
                break
            book_urls.update(page_book_url)
            page += 1

        print("while in book loop exit....")
        ##book_urls = list(set(book_urls + cache["books"]))
        if book_urls != set(cache["books"]):
            cache["books"] = list(book_urls)
            print("CACHE UPDATED!")
            self.cache.save_cache(cache)
        
        random.shuffle(list(book_urls)) 
        return list(book_urls)
        
class ChapterScraper:
    def __init__(self, session, config, books, cache):
        self.session = session
        self.config = config
        self.books = books
        self.cache = cache

    def get_chapters(self, book_url):
        # move your logic from `get_chapters()` here
        new_chapters = []
        cache = self.cache.load_cache()
        cached_chapters = cache["chapters"].get(book_url, [])
        
        
        if "/article/" in book_url:
            book_id = book_url.split("/")[-1].replace(".html", "")
            chapters_url = f"{self.config.BASE_URL}/chapters/{book_id}.html"
            self.session.random_delay()
            response = self.session.get(chapters_url)
            if response.status_code != 200:
                print(response.status_code)
                print(f"❌ Failed to fetch book: {book_url}")
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            # Extract chapter links (Modify selector if needed)
            for link in soup.find_all("a", href=True):
                if "/r/" in link["href"]:  # Adjust based on actual URL pattern
                    full_url = self.config.BASE_URL + link["href"]
                    new_chapters.append(full_url)
                    
        elif "/book/" in book_url:
            
            book_id = book_url.split("/")[-1].replace(".htm","")
            chapters_url = f"{self.config.BASE_URL1}/book/{book_id}/"
            self.session.random_delay()
            response = self.session.get(chapters_url)

            

            if response.status_code != 200:
                print(response.status_code)
                print(f"❌ Failed to fetch book: {book_url}")
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            # Extract chapter links (Modify selector if needed)
            for link in soup.find_all("a", href=True):
                if "/txt/" in link["href"]:  # Adjust based on actual URL pattern
                    full_url = link["href"]
                    new_chapters.append(full_url)

        updated_chapters = list(set(cached_chapters + new_chapters))

        if(set(updated_chapters) != set(cached_chapters)):
            cache["chapters"][book_url] = updated_chapters
            self.cache.save_cache(cache)
        return updated_chapters
        
class KeywordSearcher:
    def __init__(self, config, session):
        self.config = config
        self.session = session

    def search_in_chapter(self, chapter_url):
        retries = 3
        for attempt in range(retries):
            try:
                #print("searching chapter....")
                self.session.random_delay()
                response = self.session.get(chapter_url)
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, "html.parser")

                # Extract text inside <font> tags
                if "/txt/" in chapter_url:
                    chapter_text = "\n".join([p.next_sibling.strip() for p in soup.find_all("br") if p.next_sibling and isinstance(p.next_sibling, str)])
                elif "/r/" in chapter_url:
                    chapter_text = " ".join([p.get_text() for p in soup.find_all("p", class_="cp")])
                chapter_text_lower = chapter_text.lower()
                if self.config.KEYWORD.lower() in chapter_text_lower:
                    #print(chapter_url,KEYWORD)
                    return chapter_url  # Return the URL if keyword is found
                
                #end_time = time.time()
                #sys.stdout.write(f"\r\033[K{chapter_url}: {end_time-start_time}",end='')
                #sys.stdout.flush()
                #print(f"\r\033[KTime taken for {chapter_url}: {end_time - start_time} seconds",end='')
                return None
                
            except (requests.exceptions.ChunkedEncodingError, 
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout) as e:
                print(f"⚠️ Attempt {attempt+1}/{retries} failed due to: {e}")
                
                time.sleep(2)

def run_scraper():
    config = ScraperConfig()
    session = ScraperSession(config)
    cache = Cache(config)
    book_list_url = BookListUrl(config)
    book_scraper = BookScraper(session, config, cache)
    cache_data = cache.load_cache()
    print("📚 Fetching book URLs...")
    books = list(set(book_scraper.get_all_books(book_list_url.shuba_book_list()) + cache_data["books"]))

    print(f"✅ Total books found: {len(books)}")

    chapter_scraper = ChapterScraper(session, config, books, cache)
    searcher = KeywordSearcher(config, session)

    all_chapter_urls = []

    print("📄 Extracting chapters from all books...")
    for book_url in books:
        chapter_urls = chapter_scraper.get_chapters(book_url)
        all_chapter_urls.extend(chapter_urls)

        print(f"✅ Total chapters collected: {len(chapter_urls)}")

        print("🔍 Searching for keyword in chapters...")
        found_chapters = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            found_chapters = {executor.submit(searcher.search_in_chapter, url): url for url in chapter_urls}
            for future in found_chapters:
                result = future.result()
                if result:
                    print(f"✅ Keyword found in: {result}")
                    with open("v1_2.txt", "a", encoding="utf-8") as f:  
                        f.write(result + "\n")
                    for f in found_chapters:
                        if not f.done():
                            f.cancel()
                    break


if __name__ == "__main__":
    run_scraper()