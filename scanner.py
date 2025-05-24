import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

visited = set()
results = []

# Check if URL is valid and in same domain
def is_valid(url, base_domain):
    parsed = urlparse(url)
    return parsed.netloc == base_domain and parsed.scheme in ["http", "https"]

# Extract and scan forms
def extract_forms(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        forms = soup.find_all("form")
        form_data = []

        for form in forms:
            action = form.attrs.get("action", "").strip()
            method = form.attrs.get("method", "GET").upper()
            inputs = []
            for input_tag in form.find_all("input"):
                input_type = input_tag.attrs.get("type", "text")
                input_name = input_tag.attrs.get("name", "")
                flag = "⚠️" if any(keyword in input_name.lower() for keyword in ["user", "pass", "id", "email", "search"]) else ""
                inputs.append({
                    "name": input_name,
                    "type": input_type,
                    "flag": flag
                })
            form_data.append({
                "action": action,
                "method": method,
                "inputs": inputs
            })

        return form_data
    except Exception as e:
        print(f"Error fetching forms from {url}: {e}")
        return []

# Crawl function
def crawl(url, base_domain, depth=2):
    if url in visited or depth == 0:
        return
    visited.add(url)
    print(f"[Crawling] {url}")

    forms = extract_forms(url)
    results.append({
        "url": url,
        "forms": forms
    })

    # Find more links
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        for link_tag in soup.find_all("a"):
            href = link_tag.attrs.get("href")
            if href:
                next_url = urljoin(url, href)
                if is_valid(next_url, base_domain):
                    crawl(next_url, base_domain, depth - 1)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

# Main
if __name__ == "__main__":
    target = input("Enter target URL (e.g., http://testphp.vulnweb.com): ").strip()
    parsed_target = urlparse(target)
    base_domain = parsed_target.netloc

    crawl(target, base_domain)

    # Save results
    with open("output/results.json", "w") as f:
        json.dump(results, f, indent=4)

    print("\n✅ Scan complete. Results saved to output/results.json")
