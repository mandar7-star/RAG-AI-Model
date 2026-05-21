import requests
import urllib.parse

class WebSearcher:
    def search(self, query: str, num_results=5):
        results = []
        
        try:
            # Using DuckDuckGo API - Most reliable, no browser needed
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            # Add main abstract result
            if data.get('AbstractURL') and data.get('AbstractURL').startswith('http'):
                results.append({
                    "title": data.get('Heading', query)[:150],
                    "link": data.get('AbstractURL'),
                    "snippet": data.get('AbstractText', '')[:500]
                })
            
            # Add related topics
            for topic in data.get('RelatedTopics', []):
                if len(results) >= num_results:
                    break
                if isinstance(topic, dict):
                    if topic.get('FirstURL') and topic.get('FirstURL').startswith('http'):
                        text = topic.get('Text', '')
                        title = text.split(' - ')[0][:150] if ' - ' in text else text[:150]
                        results.append({
                            "title": title,
                            "link": topic.get('FirstURL'),
                            "snippet": text[:500] if text else ""
                        })
                    
                    elif topic.get('Topics'):
                        for subtopic in topic.get('Topics', []):
                            if len(results) >= num_results:
                                break
                            if subtopic.get('FirstURL') and subtopic.get('FirstURL').startswith('http'):
                                text = subtopic.get('Text', '')
                                title = text.split(' - ')[0][:150] if ' - ' in text else text[:150]
                                results.append({
                                    "title": title,
                                    "link": subtopic.get('FirstURL'),
                                    "snippet": text[:500] if text else ""
                                })
            
            # If no results, try Wikipedia
            if not results:
                wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query.replace(' ', '_'))}"
                wiki_response = requests.get(wiki_url, timeout=10)
                if wiki_response.status_code == 200:
                    wiki_data = wiki_response.json()
                    if wiki_data.get('content_urls', {}).get('desktop', {}).get('page'):
                        results.append({
                            "title": wiki_data.get('title', query)[:150],
                            "link": wiki_data['content_urls']['desktop']['page'],
                            "snippet": wiki_data.get('extract', '')[:500]
                        })
            
            # If still no results, provide search links
            if not results:
                results.append({
                    "title": f"Google Search: {query}",
                    "link": f"https://www.google.com/search?q={urllib.parse.quote(query)}",
                    "snippet": f"Click to search Google for {query}"
                })
                results.append({
                    "title": f"Wikipedia Search: {query}",
                    "link": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(query.replace(' ', '_'))}",
                    "snippet": f"Click to search Wikipedia for {query}"
                })
                
        except Exception as e:
            print(f"Search error: {e}")
            # Fallback results
            results.append({
                "title": f"Search results for {query}",
                "link": f"https://www.google.com/search?q={urllib.parse.quote(query)}",
                "snippet": f"Click to search Google for {query}"
            })
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for r in results:
            if r['link'] not in seen:
                seen.add(r['link'])
                unique_results.append(r)
        
        return unique_results[:num_results]