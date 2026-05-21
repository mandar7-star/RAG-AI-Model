import requests
import re
import json

class WebSearcher:
    def search(self, query: str, num_results=3):
        results = []
        try:
            # Method 1: DuckDuckGo Lite (most reliable for links)
            url = f"https://lite.duckduckgo.com/lite/?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html"
            }
            response = requests.get(url, headers=headers, timeout=15)
            
            # Parse the HTML response
            lines = response.text.split('\n')
            current_result = {}
            
            for line in lines:
                # Look for result links
                if 'http://' in line or 'https://' in line:
                    link_match = re.search(r'(https?://[^\s"\']+)', line)
                    if link_match:
                        link = link_match.group(1)
                        # Clean up the link
                        link = link.replace('&amp;', '&')
                        if 'duckduckgo.com' not in link:
                            current_result['link'] = link
                
                # Look for titles
                if 'class="result__title"' in line or 'result__a' in line:
                    title_match = re.search(r'>([^<]+)</a>', line)
                    if title_match:
                        current_result['title'] = title_match.group(1).strip()
                
                # Look for snippets
                if 'class="result__snippet"' in line:
                    snippet_match = re.search(r'>([^<]+)</', line)
                    if snippet_match:
                        current_result['snippet'] = snippet_match.group(1).strip()
                        # When we have a snippet, save the result
                        if 'title' in current_result and 'link' in current_result:
                            results.append(current_result.copy())
                            current_result = {}
                        if len(results) >= num_results:
                            break
            
            # Method 2: If no results, try alternative API
            if not results:
                results = self._search_via_api(query, num_results)
                
        except Exception as e:
            print(f"Web search error: {e}")
            results = self._search_via_api(query, num_results)
        
        # Ensure each result has a valid link
        for i, result in enumerate(results):
            if not result.get('link'):
                result['link'] = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            if not result.get('title'):
                result['title'] = f"Result {i+1} for {query}"
            if not result.get('snippet'):
                result['snippet'] = "Click the link for more information."
        
        return results
    
    def _search_via_api(self, query: str, num_results: int):
        results = []
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            data = response.json()
            
            if data.get('AbstractURL'):
                results.append({
                    "title": data.get('Heading', query),
                    "link": data.get('AbstractURL'),
                    "snippet": data.get('AbstractText', '')[:300]
                })
            
            for topic in data.get('RelatedTopics', []):
                if len(results) >= num_results:
                    break
                if isinstance(topic, dict) and topic.get('FirstURL'):
                    results.append({
                        "title": topic.get('Text', '').split('-')[0][:100],
                        "link": topic.get('FirstURL'),
                        "snippet": topic.get('Text', '')[:300]
                    })
        except Exception as e:
            print(f"API search error: {e}")
        
        return results