import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.69shuba.com"
CATEGORY_AJAX_URL = "https://www.69shuba.com/ajax_novels/class/5/{page}.htm"

def get_books_from_category():
    """Scrapes all AJAX pages in the category and collects book URLs."""
    book_links = set()
    page = 0

    while True:
        url = f"{CATEGORY_AJAX_URL.format(page=page)}"
        response = requests.get(url)

        # Stop if no more pages
        if response.status_code != 200 or page > 10:
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Find book links
        for a_tag in soup.find_all("a", href=True):
            if "/book/" in a_tag["href"]:  # Only capture book pages
                book_links.add(a_tag["href"])

        page += 1

    return book_links

# Step 1: Get books from the category AJAX pages
category_books = get_books_from_category()
#print(category_books)
# Step 2: Get books from Google Search (Manually collected or Crawled)
google_books = {
    "https://www.69shuba.com/book/29778.htm"  # Example book found in Google but not in category
}

# Step 3: Find orphan pages (books in Google but missing from category)
orphan_books = google_books - category_books

# Print results
if orphan_books:
    print("Orphan pages detected:")
    for book in orphan_books:
        print(f"{book}")
else:
    print("No orphan pages found.")
