from curl_cffi import requests

url = "https://www.reddit.com/r/FreeGameFindings/comments/p0ik3q.json?sort=new"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

print(f"Testing direct Reddit connection to: {url}")
try:
    # impersonate="chrome120" handles the complex TLS/cipher fingerprinting
    resp = requests.get(url, headers=headers, impersonate="chrome120", timeout=15)
    
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("SUCCESS: Reddit allowed the GitHub Actions IP.")
        print(f"Payload received: {str(data)[:200]}...")
    else:
        print(f"FAILED: Reddit blocked us. Response: {resp.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
