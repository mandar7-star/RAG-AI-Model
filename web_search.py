import requests
import re

class WebSearcher:
    def search(self, query: str, num_results=3):
        results = []
        try:
            # Using DuckDuckGo Lite - simple HTML page with clean links
            url = f"https://lite.duckduckgo.com/lite/?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            
            # Parse the HTML response line by line
            lines = response.text.split('\n')
            
            titles = []
            links = []
            snippets = []
            
            for i, line in enumerate(lines):
                # Find links
                if 'href="http' in line:
                    link_match = re.search(r'href="([^"]+)"', line)
                    if link_match:
                        link = link_match.group(1)
                        if 'duckduckgo.com' not in link:
                            links.append(link)
                
                # Find titles
                if 'class="result__title"' in line or 'class="result-link"' in line:
                    title_match = re.search(r'>([^<]+)</a>', line)
                    if title_match:
                        titles.append(title_match.group(1).strip())
                
                # Find snippets
                if 'class="result__snippet"' in line:
                    snippet_match = re.search(r'>([^<]+)</', line)
                    if snippet_match:
                        snippets.append(snippet_match.group(1).strip())
            
            # Build results
            for i in range(min(len(titles), len(links), num_results)):
                if i < len(titles) and i < len(links):
                    results.append({
                        "title": titles[i],
                        "link": links[i],
                        "snippet": snippets[i] if i < len(snippets) else ""
                    })
            
            # If no results, try alternative method
            if not results:
                results = self._search_via_api(query, num_results)
            
            # If still no results, return fallback
            if not results:
                results = [{
                    "title": f"Search results for {query}",
                    "link": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                    "snippet": "Click the link to view search results on DuckDuckGo."
                }]
                
        except Exception as e:
            print(f"Web search error: {e}")
            results = [{
                "title": f"Search results for {query}",
                "link": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                "snippet": f"Could not fetch results. Error: {str(e)[:100]}"
            }]
        
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