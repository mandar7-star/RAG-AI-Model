import requests
from bs4 import BeautifulSoup

class WebSearcher:
    def search(self, query: str, num_results=3):
        results = []
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            # Add abstract
            if data.get('Abstract'):
                results.append({
                    "title": "Summary",
                    "link": data.get('AbstractURL', ''),
                    "snippet": data.get('Abstract', '')[:300]
                })
            
            # Add related topics
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        "title": topic.get('Text', '').split('-')[0],
                        "link": topic.get('FirstURL', ''),
                        "snippet": topic.get('Text', '')[:300]
                    })
        except Exception as e:
            results = [{"title": "Error", "link": "", "snippet": f"Web search failed: {str(e)}"}]
        
        return results[:num_results]