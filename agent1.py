import requests
from collections import deque

SEARCH_URL = "https://en.wikipedia.org/w/rest.php/v1/search/page"
SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
PARSE_URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": "autonomous-wiki-agent/1.0"
}

class WikiResearchAgent:
    def __init__(self, depth=2, max_pages=5):
        self.depth = depth
        self.max_pages = max_pages
        self.visited = set()

    def search(self, query, limit=5):
        params = {"q": query, "limit": limit}
        r = requests.get(SEARCH_URL, headers=HEADERS, params=params)
        data = r.json()
        return [p["title"] for p in data.get("pages", [])]

    def get_summary(self, title):
        url = SUMMARY_URL + title.replace(" ", "_")
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200: return ""
        return r.json().get("extract", "")

    def get_links(self, title):
        params = {"action": "parse", "page": title, "prop": "links", "format": "json"}
        r = requests.get(PARSE_URL, headers=HEADERS, params=params)
        try:
            links = r.json()["parse"]["links"]
            return [l["*"] for l in links if l["ns"] == 0]
        except: return []

    def research(self, topic):
        queue = deque([(p, 0) for p in self.search(topic)])
        results = []
        while queue and len(results) < self.max_pages:
            title, depth = queue.popleft()
            if title in self.visited: continue
            self.visited.add(title)
            summary = self.get_summary(title)
            results.append({"title": title, "summary": summary})
            if depth < self.depth:
                for l in self.get_links(title)[:3]:
                    queue.append((l, depth + 1))
        return results

if __name__ == "__main__":
    agent = WikiResearchAgent()
    topic = input("Enter research topic: ")
    print("Researching... please wait.")
    articles = agent.research(topic)
    
    print("\n--- Research Results ---")
    for a in articles:
        print(f"\nTitle: {a['title']}")
        print(f"Summary: {a['summary']}")

