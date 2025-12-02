import requests
import json
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
from itertools import zip_longest
import random
import sys
# Base URL of the site
BASE_URL = "https://www.69yuedu.net"
BASE_URL1= "https://www.69shuba.com"

# Keyword to search for
KEYWORD = "状元"

# Rotate User-Agents Randomly
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

# Headers to appear human-like
def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "DNT": "1",
        "Cache-Control": "no-cache"
    }

session = requests.Session()
session.headers.update(get_headers())

# Clear cookies every N requests
REQUEST_COUNT = 0
CLEAR_COOKIES_AFTER = 5  # Clear cookies every 5 requests
CACHE_FILE = "scraped_data.json"
def clear_cookies():
    global session, REQUEST_COUNT
    session.cookies.clear()  # Clear session cookies
    session = requests.Session()  # Reset session
    session.headers.update(get_headers())  # Update headers
    REQUEST_COUNT = 0
    #print("🧹 Cleared Cookies to Avoid Blocking")

# Random Delay
def random_delay():
    time.sleep(random.uniform(2, 6))


# Load cached data
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"books": [], "chapters": {}}

# Save updated cache data
def save_cache(cache_data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=4)

def check_website():
    try:
        response = requests.get(BASE_URL, headers=get_headers(), timeout=10)
        response1 = requests.get(BASE_URL1, headers=get_headers(), timeout=10)
        if response.status_code == 200 and response1.status_code == 200:
            print("✅ Connected to Websites")
            return True
        else:
            print(f"❌ Website returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Could not connect to the website. Check your internet or the site’s status.")
        return False
    

# Step 1: Get all book URLs
def get_all_books():
    global REQUEST_COUNT
    cache = load_cache()
    book_urls = set()
    page = 1
    while True:
        print(page)
        page_book_url = set()
        if page == 1:
            yuedu_book_list_url = f"{BASE_URL}/articlelist/class/0.html"  # Modify if needed
            shuba_book_list_url = f"{BASE_URL1}/novels/class/0.htm"
            response = session.get(yuedu_book_list_url, headers=get_headers())
            response1 = session.get(shuba_book_list_url, headers=get_headers())
            if response.status_code != 200 and response1.status_code != 200:
                print("❌ Failed to fetch book list")
                return []
        else: 
            yuedu_book_list_url = f"{BASE_URL}/ajax_articlelist/full/0/{page}.htm"
            shuba_book_list_url = f"{BASE_URL1}/ajax_novels/class/0/{page}.htm"

        print(yuedu_book_list_url,"\n", shuba_book_list_url)
        random_delay()
        response = session.get(yuedu_book_list_url, headers=get_headers())
        response1 = session.get(shuba_book_list_url, headers=get_headers())
        
        REQUEST_COUNT += 1
        if REQUEST_COUNT >= CLEAR_COOKIES_AFTER:
            clear_cookies()

        
        

        yuebu_soup = BeautifulSoup(response.text, "html.parser")
        shuba_soup = BeautifulSoup(response1.text, "html.parser")
        # Extract book links (Modify selector if needed)
        for link1, link2 in zip_longest(yuebu_soup.find_all("a", href=True), shuba_soup.find_all("a", href=True)):

            if link1 and "/article/" in link1["href"]:  # Adjust based on actual URL structure 
                full_url = BASE_URL + link1["href"]
                if full_url not in cache["books"]:  # Skip already scraped books
                    page_book_url.add(full_url)

            if link2 and "/book/" in link2["href"]:  # Adjust based on actual URL structure
                full_url = link2["href"]
                if full_url not in cache["books"]:  # Skip already scraped books
                    page_book_url.add(full_url)

        if not page_book_url or page == 31:
            break
        book_urls.update(page_book_url)
        page += 1

    print("while in book loop exit....")
    ##book_urls = list(set(book_urls + cache["books"]))
    if book_urls != set(cache["books"]):
        cache["books"] = list(book_urls)
        print("book cache updated")
        save_cache(cache)
    
    random.shuffle(list(book_urls)) 
    return list(book_urls)

# Step 2: Get all chapter URLs from a book page
def get_chapters(book_url):
    new_chapters = []
    cache = load_cache()
    cached_chapters = cache["chapters"].get(book_url, [])
    
    
    if "/article/" in book_url:
        book_id = book_url.split("/")[-1].replace(".html", "")
        chapters_url = f"{BASE_URL}/chapters/{book_id}.html"
        random_delay()
        response = session.get(chapters_url, headers=get_headers())
        if response.status_code != 200:
            print(response.status_code)
            print(f"❌ Failed to fetch book: {book_url}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract chapter links (Modify selector if needed)
        for link in soup.find_all("a", href=True):
            if "/r/" in link["href"]:  # Adjust based on actual URL pattern
                full_url = BASE_URL + link["href"]
                new_chapters.append(full_url)
                
    elif "/book/" in book_url:
        
        book_id = book_url.split("/")[-1].replace(".htm","")
        chapters_url = f"{BASE_URL1}/book/{book_id}/"
        random_delay()
        response = session.get(chapters_url, headers=get_headers())

        #clear cookies to avoid ip block
        global REQUEST_COUNT 
        REQUEST_COUNT += 1
        if REQUEST_COUNT >= CLEAR_COOKIES_AFTER:
            clear_cookies()

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
        save_cache(cache)
    return updated_chapters

# Step 3: Search for keyword inside chapters
def search_in_chapter(chapter_url):
    start_time = time.time()
    retries = 3
    for attempt in range(retries):
        try:
            #print("searching chapter....")
            random_delay()
            session = requests.Session()
            session.headers.update(get_headers())
            response = session.get(chapter_url, headers=get_headers(), timeout=30)
            global REQUEST_COUNT
            REQUEST_COUNT += 1
            if REQUEST_COUNT >= CLEAR_COOKIES_AFTER:
                #print("clearing...")
                clear_cookies()

            time.sleep(10)
            if response.status_code != 200:
                return None
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract text inside <font> tags
            if "/txt/" in chapter_url:
                chapter_text = "\n".join([p.next_sibling.strip() for p in soup.find_all("br") if p.next_sibling and isinstance(p.next_sibling, str)])
            elif "/r/" in chapter_url:
                chapter_text = " ".join([p.get_text() for p in soup.find_all("p", class_="cp")])
            chapter_text_lower = chapter_text.lower()
            if KEYWORD.lower() in chapter_text_lower:
                #print(chapter_url,KEYWORD)
                return chapter_url  # Return the URL if keyword is found
            
            end_time = time.time()
            #sys.stdout.write(f"\r\033[K{chapter_url}: {end_time-start_time}",end='')
            #sys.stdout.flush()
            #print(f"\r\033[KTime taken for {chapter_url}: {end_time - start_time} seconds",end='')
            return None
            
        except (requests.exceptions.ChunkedEncodingError, 
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            print(f"⚠️ Attempt {attempt+1}/{retries} failed due to: {e}")
            
            time.sleep(2)  # Wait before retrying
            

# Step 4: Run the scraper using multithreading and caching
def main():
    clear_cookies()
    if not check_website():
        return
    cache = load_cache()
    books = get_all_books()
    books = cache["books"]
    # Include cached books in the process
    all_books = list(set(books + (cache["books"])))

    for book in all_books:
        clear_cookies()
        print(f"\n📖 Checking book: {book}")
        chapters = get_chapters(book)
        
        # Use ThreadPoolExecutor to speed up chapter scraping
        with ThreadPoolExecutor(max_workers=30) as executor:
            found_chapters = {}
            found_chapters = {executor.submit(search_in_chapter, ch): ch for ch in chapters}
            
            #print("\n\nresult: \033[F", end='')
            
            for future in found_chapters:
                result = future.result()
                if result:  
                    print(f"\nresult: {result}")
                    with open("topper.txt", "a", encoding="utf-8") as f:  
                        f.write(result + "\n")
                    for f in found_chapters:
                        if not f.done():
                            f.cancel()
                    break
                


 

if __name__ == "__main__":
    main()
