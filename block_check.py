import requests
import concurrent.futures
import threading
import time

base_url = "https://www.69shuba.com/book/"
start_id = 1
max_workers = 60  # Number of threads (adjustable)
consecutive_fail_limit = 500  # Stop after this many failures in a row
reset_interval = 300  # Reset session after this many requests

session = requests.Session()
REQUEST_COUNT = 0
valid_pages = 0
consecutive_failures = 0
lock = threading.Lock()

def get_headers():
    """Generate headers (modify if needed)."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

def clear_cookies():
    """Reset session to avoid blocking."""
    global session, REQUEST_COUNT
    session.cookies.clear()
    session = requests.Session()
    session.headers.update(get_headers())
    REQUEST_COUNT = 0
    print("🔄 Session reset to avoid blocking!")

def check_book(book_id):
    """Check if a book page exists."""
    global valid_pages, consecutive_failures, REQUEST_COUNT

    url = f"{base_url}{book_id}.htm"

    try:
        response = session.head(url, timeout=5)  # Use HEAD request (faster)
    except requests.RequestException:
        print(f"⚠️ Request failed: {url}")
        return

    with lock:
        REQUEST_COUNT += 1
        if response.status_code == 200:
            print(f"✅ Found: {url}")
            valid_pages += 1
            consecutive_failures = 0
        else:
            print(f"❌ Not Found: {url}")
            consecutive_failures += 1

        if REQUEST_COUNT >= reset_interval:
            clear_cookies()

def main():
    global consecutive_failures

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        book_id = start_id

        while consecutive_failures < consecutive_fail_limit:
            executor.submit(check_book, book_id)
            book_id += 1
            time.sleep(0.01)  # Small delay to avoid getting blocked

    print(f"🔹 Total valid book pages: {valid_pages}")

if __name__ == "__main__":
    session.headers.update(get_headers())  # Set headers before starting
    main()
