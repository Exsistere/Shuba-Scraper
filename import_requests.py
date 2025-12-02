import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# Headers to mimic a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Configure retries with exponential backoff
retry_strategy = Retry(
    total=5,                   # Maximum retry attempts
    backoff_factor=2,          # Exponential backoff: 2s, 4s, 8s, 16s, etc.
    status_forcelist=[500, 502, 503, 504],  # Retry on server errors
    allowed_methods=["GET"]
)

# Create a session with retry logic
s = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
s.mount("https://", adapter)

# Attempt to make the request with backoff handling
url = "https://www.69shuba.com"

for attempt in range(6):  # Up to 6 attempts
    try:
        response = s.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise error for HTTP failure codes
        print(response.text[:500])  # Print first 500 characters of response
        break  # Exit loop if request succeeds

    except requests.exceptions.ConnectionError as e:
        print(f"⚠️ Attempt {attempt + 1}: Connection error. Retrying in {2 ** attempt} seconds...")
        time.sleep(2 ** attempt)  # Exponential backoff

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        break  # Exit loop if error is not recoverable
