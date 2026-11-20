import requests

# PullPush uses slightly different endpoints and parameters (size instead of limit)
url = "https://api.pullpush.io/reddit/search/comment/"
params = {
    "link_id": "p0ik3q",  # Itch.io megathread ID
    "size": 5,
    "sort": "desc"
}

print("Testing PullPush API for the Itch.io megathread...")
try:
    resp = requests.get(url, params=params, timeout=15)
    print(f"Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        comments = data.get("data", [])
        
        if comments:
            print(f"SUCCESS: Found {len(comments)} comments.")
            for c in comments:
                # Truncating body for clean log output
                body = c.get('body', '').replace('\n', ' ')
                print(f"- {c.get('author')}: {body[:80]}...")
        else:
            print("FAILED: PullPush returned a 200 status but the data array is empty.")
    else:
        print(f"FAILED: HTTP {resp.status_code}")
        print(resp.text[:200])
except Exception as e:
    print(f"Error: {e}")
