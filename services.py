import os
import heapq
import json
import math
import requests
import re
import base64
import time
from groq import Groq
from config import Config
from global_countries import (
    get_country_info, get_currency, get_currency_symbol, get_tts_voice,
    get_country_center_coords, search_destinations,
    get_tts_fallback_lang, ALL_COUNTRY_NAMES, COUNTRIES
)


def _build_global_country_knowledge():
    """Build a concise knowledge string of all 40 countries for the AI system prompt."""
    lines = []
    for name, data in COUNTRIES.items():
        top_dests = ", ".join(data.get("popular_destinations", [])[:8])
        lines.append(
            f"- {name} ({data['continent']}): Currency={data['currency']} ({data['currency_symbol']}), "
            f"Timezone={data['timezone']}, Top destinations: {top_dests}"
        )
    return "\n".join(lines)

class GraphService:
    @staticmethod
    def dijkstra(graph, start):
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        priority_queue = [(0, start)]
        path = {}

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in graph[current_node].items():
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    path[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        return distances, path

    @staticmethod
    def get_shortest_path(graph, start, end):
        distances, predecessors = GraphService.dijkstra(graph, start)
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors.get(current)
        return path[::-1] if distances[end] != float('inf') else None

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        import math
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def optimize_route(locations):
        """
        Simple Nearest Neighbor TSP for route optimization.
        locations: list of dicts with 'lat', 'lng'
        """
        if not locations or len(locations) <= 1:
            return locations
            
        unvisited = list(locations)
        optimized = [unvisited.pop(0)] # Start with the first one
        
        while unvisited:
            current = optimized[-1]
            next_idx = 0
            min_dist = float('inf')
            
            for i, loc in enumerate(unvisited):
                d = GraphService.haversine(
                    float(current.get('lat', 0)), float(current.get('lng', 0)),
                    float(loc.get('lat', 0)), float(loc.get('lng', 0))
                )
                if d < min_dist:
                    min_dist = d
                    next_idx = i
            
            optimized.append(unvisited.pop(next_idx))
            
        return optimized

def _get_fallback_image(query):
    """Generate a reliable fallback image URL from a curated pool of travel images."""
    # Curated pool of high-quality, reliable travel/landscape images from Unsplash
    _FALLBACK_IMAGES = {
        'beach': [
            'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1473116763249-2faaef81ccda?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1506953823976-52e1fdc0149a?w=800&h=600&fit=crop',
        ],
        'temple': [
            'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1564804955922-3f98e04c1e21?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1585135497273-1a86b09fe70e?w=800&h=600&fit=crop',
        ],
        'mountain': [
            'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1486870591958-9b9d0d1dda99?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=800&h=600&fit=crop',
        ],
        'lake': [
            'https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&h=600&fit=crop',
        ],
        'fort': [
            'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800&h=600&fit=crop',
        ],
        'heritage': [
            'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&h=600&fit=crop',
        ],
        'waterfall': [
            'https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1432405972618-c6b0cfba1950?w=800&h=600&fit=crop',
        ],
        'forest': [
            'https://images.unsplash.com/photo-1448375240586-882707db888b?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1473448912268-2022ce9509d8?w=800&h=600&fit=crop',
        ],
        'wildlife': [
            'https://images.unsplash.com/photo-1456926631375-92c8ce872def?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1474511320723-9a56873571b7?w=800&h=600&fit=crop',
        ],
        'church': [
            'https://images.unsplash.com/photo-1548625149-fc4a29cf7092?w=800&h=600&fit=crop',
        ],
        'mosque': [
            'https://images.unsplash.com/photo-1585036156171-384164a8c8f3?w=800&h=600&fit=crop',
        ],
        'palace': [
            'https://images.unsplash.com/photo-1599660444531-fa3da26bcc34?w=800&h=600&fit=crop',
        ],
        'garden': [
            'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800&h=600&fit=crop',
        ],
        'landscape': [
            'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&h=600&fit=crop',
        ],
        'aerial': [
            'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=600&fit=crop',
        ],
        'shopping': [
            'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=800&h=600&fit=crop',
        ],
        'hotel': [
            'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&h=600&fit=crop',
        ],
        'restaurant': [
            'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800&h=600&fit=crop',
        ],
        'city': [
            'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&h=600&fit=crop',
        ],
        'panorama': [
            'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&h=600&fit=crop',
        ],
        'desert': [
            'https://images.unsplash.com/photo-1473580044384-7ba9967e16a0?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1509316785289-025f54846b43?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1542350237-9e964601314a?w=800&h=600&fit=crop',
        ]
    }
    _DEFAULT_IMAGES = [
        'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1530789253388-582c481c54b0?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1500835556837-99ac94a94552?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1503220317375-aaad61436b1b?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1539635278303-d4002c07eae3?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?w=800&h=600&fit=crop',
    ]
    
    query_lower = query.lower()
    # Priority matching
    if any(k in query_lower for k in ['jaisalmer', 'desert', 'sand', 'rajasthan']):
        images = _FALLBACK_IMAGES.get('desert', _FALLBACK_IMAGES.get('landscape'))
        return images[hash(query) % len(images)]

    # Find matching category
    for keyword, images in _FALLBACK_IMAGES.items():
        if keyword in query_lower:
            # Use hash of query for consistent but varied selection
            idx = hash(query) % len(images)
            return images[idx]
    
    # Default: use hash for variety
    idx = hash(query) % len(_DEFAULT_IMAGES)
    return _DEFAULT_IMAGES[idx]


class DuckDuckGoService:
    """Free search service using DuckDuckGo. No API key required."""

    @staticmethod
    def search(query, max_results=5):
        """Web search via DuckDuckGo. Returns list of dicts with title, url, snippet."""
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            return [
                {'title': r.get('title', ''), 'url': r.get('href', ''), 'snippet': r.get('body', '')}
                for r in results
            ]
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []

    @staticmethod
    def search_images(query, max_results=15):
        """Image search via DuckDuckGo. Returns list of image URL strings."""
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.images(query, max_results=max_results))
            urls = []
            seen = set()
            for r in results:
                url = r.get('image', '')
                if url and url not in seen:
                    seen.add(url)
                    urls.append(url)
            return urls
        except Exception as e:
            print(f"DuckDuckGo image search error: {e}")
            return []

    @staticmethod
    def search_with_fallback(query, num_results=5):
        """Search that returns results in a standard format."""
        results = DuckDuckGoService.search(query, max_results=num_results)
        if not results:
            return {}
        return {
            'organic': [
                {'title': r['title'], 'link': r['url'], 'snippet': r['snippet']}
                for r in results
            ]
        }


class SearchService:
    @staticmethod
    def _tokenize_query(text):
        stop = {
            'tourism', 'tourist', 'travel', 'sightseeing', 'landmark', 'landmarks',
            'destination', 'destinations', 'high', 'quality', 'city', 'view', 'best', 'places',
            'place', 'famous', 'attraction', 'attractions', 'route', 'map', 'trail', 'photo',
            'photos', 'image', 'images', 'cinematic', '4k'
        }
        tokens = re.findall(r'[a-zA-Z0-9]+', (text or '').lower())
        return [t for t in tokens if len(t) > 2 and t not in stop]

    @staticmethod
    def _looks_like_real_photo(url, img_obj):
        if not url:
            return False
        u = url.lower()
        banned = ['logo', 'icon', 'vector', 'svg', 'sticker', 'emoji', 'sprite', 'button', 'favicon']
        if any(b in u for b in banned):
            return False

        # Commonly hotlink-blocked / irrelevant result patterns
        blocked_hosts = ['gstatic.com', 'googleusercontent.com/proxy', 'ytimg.com', 'twimg.com']
        if any(h in u for h in blocked_hosts):
            return False

        w = img_obj.get('imageWidth') or img_obj.get('width') or 0
        h = img_obj.get('imageHeight') or img_obj.get('height') or 0
        try:
            if int(w) and int(h) and (int(w) < 360 or int(h) < 240):
                return False
        except Exception:
            pass

        return True

    @staticmethod
    def _score_image_candidate(img_obj, required_tokens):
        url = str(img_obj.get('imageUrl') or '')
        title = str(img_obj.get('title') or '')
        source = str(img_obj.get('source') or img_obj.get('domain') or '')
        hay = f"{url} {title} {source}".lower()

        score = 0
        trusted_hosts = [
            'images.unsplash.com', 'upload.wikimedia.org', 'images.pexels.com',
            'cdn.pixabay.com', 'flickr.com', 'staticflickr.com', 'tripsavvy.com',
            'lonelyplanet.com', 'natgeo.com', 'nationalgeographic.com', 'cntraveller.in',
            'outlooktraveller.com', 'travelandleisure.com'
        ]
        if any(h in url.lower() for h in trusted_hosts):
            score += 10 # Strong boost for trusted sources

        for tok in required_tokens[:4]:
            if tok in hay:
                score += 3
        for tok in required_tokens[4:8]:
            if tok in hay:
                score += 1

        # Prefer high-resolution landscape images for hero usage
        w = img_obj.get('imageWidth') or img_obj.get('width') or 0
        h = img_obj.get('imageHeight') or img_obj.get('height') or 0
        try:
            w = int(w)
            h = int(h)
            if w >= 1600:
                score += 5
            elif w >= 1200:
                score += 3
            elif w >= 800:
                score += 1
            
            if h > 0:
                ratio = w / h
                if 1.5 <= ratio <= 2.2: # Ideal cinematic aspect ratio
                    score += 7
                elif ratio > 1.1: # Basic landscape
                    score += 3
                elif ratio < 0.9: # Vertical/Portrait (penalty for hero)
                    score -= 10
        except Exception:
            pass

        return score


    @staticmethod
    def get_images(query):
        import hashlib
        query_hash = hashlib.sha256(query.lower().strip().encode()).hexdigest()

        # Check cache first
        try:
            from models import db, ImageSearchCache
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            cached = ImageSearchCache.query.filter_by(query_hash=query_hash).first()
            if cached and cached.expires_at > now:
                return cached.images
            if cached:
                db.session.delete(cached)
                db.session.commit()
        except Exception:
            pass

        images = []

        # DuckDuckGo (free, no billing required)
        images = DuckDuckGoService.search_images(query)

        # Cache results
        if images:
            try:
                from models import db, ImageSearchCache
                from datetime import datetime, timedelta
                now = datetime.utcnow()
                db.session.add(ImageSearchCache(
                    query_hash=query_hash,
                    query_text=query[:500],
                    images=images,
                    fetched_at=now,
                    expires_at=now + timedelta(hours=6)
                ))
                db.session.commit()
            except Exception:
                pass

        return images

    @staticmethod
    def get_search_results(query):
        # DuckDuckGo (free, no billing required)
        ddg_result = DuckDuckGoService.search_with_fallback(query)
        if ddg_result:
            return ddg_result
        return {}

    @staticmethod
    def get_images_parallel(queries):
        """Fetch images for multiple queries concurrently instead of sequentially."""
        if not queries:
            return []
        from concurrent.futures import ThreadPoolExecutor, as_completed
        results = {}
        def _fetch(idx, q):
            try:
                imgs = SearchService.get_images(q)
                return idx, imgs
            except Exception:
                return idx, []
        with ThreadPoolExecutor(max_workers=min(len(queries), 8)) as pool:
            futures = {pool.submit(_fetch, i, q): i for i, q in enumerate(queries)}
            for f in as_completed(futures):
                idx, imgs = f.result()
                results[idx] = imgs
        return [results.get(i, []) for i in range(len(queries))]


class AIService:
    @staticmethod
    def _resolve_destination_country(destination):
        """Resolve a destination name to its country info dict. Returns (country_name, country_info) or (None, None)."""
        if not destination:
            return None, None
        results = search_destinations(destination)
        if results:
            country_name = results[0].get('country')
            if country_name:
                return country_name, get_country_info(country_name)
        return None, None

    @staticmethod
    def _get_country_context(destination):
        """Return a context dict for a destination with currency, timezone, coords, etc."""
        country_name, country_info = AIService._resolve_destination_country(destination)
        if country_info:
            return {
                'country': country_name,
                'currency': country_info.get('currency', 'USD'),
                'currency_symbol': country_info.get('currency_symbol', '$'),
                'timezone': country_info.get('timezone', 'UTC'),
                'center_coords': get_country_center_coords(country_name),
            }
        return {
            'country': None,
            'currency': 'USD',
            'currency_symbol': '$',
            'timezone': 'UTC',
            'center_coords': {"lat": 20.0, "lng": 0.0},
        }

    @staticmethod
    def _build_search_query(destination, suffix=""):
        """Build a search query for a destination without hardcoding 'India'."""
        if not destination:
            return suffix or "travel destination"
        country_name, _ = AIService._resolve_destination_country(destination)
        if country_name:
            return f"{destination} {country_name} {suffix}".strip()
        return f"{destination} {suffix}".strip()

    @staticmethod
    def analyze_image_for_travel(image_bytes, mime_type, user_prompt=None):
        """
        Analyze an uploaded image in travel context.
        Uses a vision-capable Groq model when available.
        """
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            prompt = user_prompt.strip() if user_prompt else "What is in this image? Explain it for a traveler and suggest best travel tips based on it."
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            data_url = f"data:{mime_type};base64,{image_b64}"

            completion = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Skupheon, a travel assistant. Describe images clearly and provide practical travel-focused guidance."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url}}
                        ]
                    }
                ],
                temperature=0.4,
                max_completion_tokens=700,
                top_p=1,
                stream=False
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"AI image analysis error: {e}")
            return "I received your image, but image analysis is temporarily unavailable. Please try again in a moment."

    @staticmethod
    def general_chat(message, history=None, my_trip_context=None):
        """
        Generic chat for the Profile AI Assistant with history support.
        history: list of dicts like [{"role": "user", "content": "..."}, {"role": "ai", "content": "..."}]
        my_trip_context: optional string with the user's trips/saved destinations data for context-aware answers.
        """
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            _global_knowledge = _build_global_country_knowledge()
            system_msg = f"""
            You are Skupheon, the intelligent travel assistant for RoutheonSkups.
            You are helpful, friendly, and expert in all things travel across the ENTIRE WORLD.
            Your goal is to assist the user with their travel queries, provide destination insights, help with budgets, or just chat about their upcoming trips.
            Keep your responses concise but insightful.

            IMPORTANT: You have deep knowledge of ALL 40 countries supported by RoutheonSkups.
            You can help users plan trips, compare destinations, suggest itineraries, discuss budgets, local cuisine, culture, weather, visa info, and travel tips for ANY of these countries — not just India.

            Here is your complete global country knowledge base:
{_global_knowledge}

            When a user asks about a destination, ALWAYS use the correct currency, timezone, and regional context for that country.
            You can discuss destinations across Europe, Asia, North America, South America, Africa, and Oceania.
            If a user mentions a place, identify which country it belongs to and respond with accurate, country-specific travel advice.
            """
            
            if my_trip_context:
                # Detect scope from context
                is_trips_only = "USER'S SAVED TRIPS" in my_trip_context and "SAVED DESTINATIONS" not in my_trip_context
                is_destinations_only = "SAVED DESTINATIONS" in my_trip_context and "USER'S SAVED TRIPS" not in my_trip_context
                
                if is_trips_only:
                    scope_rule = """
SCOPE: Plan a Trip — The user selected "Plan a Trip" scope. You have ONLY their saved trip data.
- Answer questions about their saved trips, itineraries, budgets, dates, travelers, etc.
- If asked about destinations/saved places that are NOT in their trips, tell them: "This destination is not in your saved trips. Switch to 'Explore Destination' scope or connect My Trip to see all your data."
- Focus exclusively on trip planning, trip details, budget breakdowns, itinerary reviews, and travel advice related to their saved trips.
"""
                elif is_destinations_only:
                    scope_rule = """
SCOPE: Explore Destination — The user selected "Explore Destination" scope. You have ONLY their saved/favorite destination data.
- Answer questions about their saved destinations, favorites, tags, descriptions, etc.
- If asked about trips/itineraries that are NOT in their saved destinations, tell them: "This is trip data. Switch to 'Plan a Trip' scope to ask about your saved trips."
- Focus exclusively on destination information, travel tips for their saved places, and exploration advice.
"""
                else:
                    scope_rule = """
SCOPE: All My Trip Data — The user has access to all their trip and destination data.
- Answer using both their saved trips and saved destinations.
"""

                system_msg += f"""

IMPORTANT: The user has connected their "My Trip" data to this conversation.
{scope_rule}
Rules:
1. You MUST use this data to answer questions about the user's trips and saved destinations.
2. When the user asks about a specific destination, check if it exists in their data FIRST.
3. If the destination IS in their data: provide detailed answers using the info you have.
4. If the destination is NOT in their data: clearly tell them the destination is not found in their current scope.
5. Never make up or fabricate trip data. Only use what is provided in the context below.

Here is the user's data:
""" + my_trip_context
            
            messages = [{"role": "system", "content": system_msg}]
            
            if history:
                # Add historical context, map 'ai' role to 'assistant' for Groq
                for entry in history:
                    role = "assistant" if entry['role'] == 'ai' else "user"
                    messages.append({"role": role, "content": entry['content']})
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1024,
                top_p=1,
                stream=False
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            print(f"AI General Chat Error: {e}")
            return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment! 🐾"

    @staticmethod
    def generate_chat_response(message):
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            # System prompt to guide the AI to act as a travel planner
            system_msg = """
            You are a smart travel assistant named Skupheon with expertise across ALL 40 countries supported by RoutheonSkups: Italy, Japan, France, Spain, United States, New Zealand, Greece, Switzerland, Australia, Thailand, United Kingdom, Canada, Maldives, Portugal, Iceland, Brazil, Costa Rica, Mexico, Vietnam, Austria, Egypt, South Africa, Norway, Turkey, Peru, Indonesia, United Arab Emirates, Germany, South Korea, Netherlands, India, Croatia, Ireland, Singapore, Czech Republic, Sri Lanka, Morocco, Argentina, Finland, and China.
            
            Your goal is to help users plan trips to ANY destination worldwide.
            If the user asks to plan a trip or gives enough details (destination, days), 
            extract the following information in a JSON block at the END of your response (after your natural language reply).
            
            JSON Structure:
            {{
                "intent": "plan_trip",
                "destination": "Paris",
                "country": "France",
                "days": 3,
                "preferences": "museums, food"
            }}
            
            If the user is just asking general questions, just reply normally.
            If the user mentions a place but doesn't explicitly ask for a full plan yet, verify if they want images.
            
            Use the correct currency for the destination country (EUR for Europe, JPY for Japan, THB for Thailand, USD for US, GBP for UK, etc.).
            Make your natural language response friendly and engaging.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
                stop=None
            )
            
            content = completion.choices[0].message.content
            
            # Basic parsing to see if we have JSON data for a plan
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            extracted_data = {}
            if json_match:
                try:
                    json_str = json_match.group(0)
                    extracted_data = json.loads(json_str)
                    # Remove the JSON from the displayed text
                    content = content.replace(json_str, '').strip()
                except:
                    pass
            
            # If we have a destination, fetch images
            images = []
            destination = extracted_data.get('destination')
            
            if not destination:
                # Smart heuristic for guide context
                if " in context of " in message:
                    potential = message.split(" in context of ")[0].strip()
                    if len(potential.split()) < 4:
                        destination = potential
                elif len(message.split()) < 5:
                    destination = message
            
            if destination:
                print(f"Fetching images for chatbot destination: {destination}")
                images = SearchService.get_images(f"{destination} tourist attractions sightseeing high quality")
                print(f"Found {len(images)} images for {destination}")
            
            return {
                "response": content,
                "images": images,
                "data": extracted_data
            }

        except Exception as e:
            import traceback
            trace = traceback.format_exc()
            print(f"AIService Error: {str(e)}")
            print(trace)
            return {"response": f"Sorry, I encountered an error: {str(e)}", "images": [], "data": {}}

    @staticmethod
    def generate_itinerary(destination, days, preferences):
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            ctx = AIService._get_country_context(destination)
            country_suffix = f", {ctx['country']}" if ctx['country'] else ""
            
            prompt = f"""
            Create a highly detailed cinematic {days}-day itinerary for a trip to {destination}{country_suffix}.
            Preferences: {preferences}.
            
            Format the output strictly as a JSON object with the following structure:
            {{
                "title": "A {days}-Day Journey through {destination}",
                "description": "A premium cinematic exploration of {destination}.",
                "center_coords": {{"lat": "latitude", "lng": "longitude"}},
                "days": [
                    {{
                        "day": 1,
                        "title": "Arrival & Initial Exploration",
                        "time_range": "09:00 AM - 09:00 PM",
                        "summary": "Brief summary of the day",
                        "activities": [
                            {{
                                "time": "09:00 AM",
                                "duration": "2 hours",
                                "title": "Activity Title",
                                "description": "Engaging description of the activity.",
                                "icon": "fas fa-landmark",
                                "lat": "latitude_float",
                                "lng": "longitude_float",
                                "image_keyword": "specific landmark name in {destination}",
                                "estimated_cost_usd": 25
                            }}
                        ]
                    }}
                ],
                "budget_summary": {{
                    "accommodation_average_per_day": 100,
                    "food_average_per_day": 50,
                    "transport_average_per_day": 30,
                    "currency": "{ctx['currency']}"
                }}
            }}
            Do not include any markdown formatting, just raw JSON.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=16383,
                top_p=1,
                stream=False,
                stop=None
            )
            
            text = completion.choices[0].message.content
            itinerary = json.loads(text)
            
            # Enrich with real images and robust coordinates - PARALLEL image fetch
            dest_name = itinerary.get('destination', destination)
            ctx = AIService._get_country_context(dest_name)
            if not itinerary.get('center_coords'):
                itinerary['center_coords'] = ctx['center_coords']

            act_queries = []
            act_refs = []
            for day in itinerary.get('days', []):
                for act in day.get('activities', []):
                    act_queries.append(f"{act.get('title')} {dest_name} sightseeing")
                    act_refs.append(act)
            all_images = SearchService.get_images_parallel(act_queries)
            for i, act in enumerate(act_refs):
                imgs = all_images[i] if i < len(all_images) else []
                act['image_url'] = imgs[0] if imgs else _get_fallback_image(f"{act.get('title', '')} {dest_name}")
                if 'lat' not in act or 'lng' not in act:
                    act['lat'] = itinerary['center_coords']['lat']
                    act['lng'] = itinerary['center_coords']['lng']
            
            return itinerary
        except Exception as e:
            print(f"Error generating itinerary: {e}")
            return {"error": "Failed to generate itinerary", "details": str(e)}

    @staticmethod
    def explore_place(place, age, season):
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            prompt = f"""
            Explore the place "{place}" for a traveler of age {age} in the season "{season}".
            
            Format the output strictly as a JSON object:
            {{
                "place": "{place}",
                "overview": "Detailed overview of the place...",
                "best_time": "Optimal months to visit...",
                "attractions": [
                    {{
                        "name": "Attraction 1",
                        "description": "Short description",
                        "coords": ["lat", "lng"]
                    }},
                    {{
                        "name": "Attraction 2",
                        "description": "Short description",
                        "coords": ["lat", "lng"]
                    }}
                ],
                "graph": {{
                    "Attraction 1": {{"Attraction 2": 5, "Attraction 3": 10}},
                    "Attraction 2": {{"Attraction 1": 5, "Attraction 3": 3}},
                    "Attraction 3": {{"Attraction 1": 10, "Attraction 2": 3}}
                }}
            }}
            Identify at least 4 attractions. Provide a mock connectivity graph for them (weights in minutes/km).
            Do not include any markdown formatting. Just raw JSON.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=2048
            )
            
            text = completion.choices[0].message.content
            # Improved JSON extraction using regex
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    text_clean = text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(text_clean)
            else:
                text_clean = text.replace('```json', '').replace('```', '').strip()
                data = json.loads(text_clean)
            
            # Add images - PARALLEL
            place_query = f"{place} travel destination tourism high resolution"
            attr_queries = [f"{attr['name']} {place} tourist attraction" for attr in data['attractions']]
            all_images = SearchService.get_images_parallel([place_query] + attr_queries)
            data['images'] = all_images[0] if all_images[0] else [_get_fallback_image(f"{place} landscape")]
            for i, attr in enumerate(data['attractions']):
                imgs = all_images[i + 1] if i + 1 < len(all_images) else []
                attr['images'] = imgs if imgs else [_get_fallback_image(f"{attr['name']} {place}")]
            
            # Calculate shortest path between first and last attraction as a showcase
            if len(data['attractions']) >= 2:
                start = data['attractions'][0]['name']
                end = data['attractions'][-1]['name']
                data['shortest_path'] = GraphService.get_shortest_path(data['graph'], start, end)
            
            return data
        except Exception as e:
            print(f"Error exploring place: {e}")
            return {"error": "Failed to explore place", "details": str(e)}

    @staticmethod
    def generate_milestone_trip(start, end, preferences):
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            prompt = f"""
            Plan a road trip from "{start}" to "{end}" with milestones (interesting stops) along the way.
            Preferences: {preferences}.
            
            Format the output strictly as a JSON object:
            {{
                "title": "Road Trip: {start} to {end}",
                "route": [
                    {{
                        "place": "{start}",
                        "type": "start",
                        "description": "Starting point description...",
                        "coords": [lat, lng]
                    }},
                    {{
                        "place": "Milestone City 1",
                        "type": "stopover",
                        "description": "Things to explore and stay here...",
                        "coords": [lat, lng]
                    }},
                    {{
                        "place": "{end}",
                        "type": "end",
                        "description": "Final destination description...",
                        "coords": [lat, lng]
                    }}
                ]
            }}
            Provide 3-5 stopovers between {start} and {end}.
            Do not include any markdown formatting. Just raw JSON.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=2048
            )
            
            text = completion.choices[0].message.content
            # Improved JSON extraction using regex
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    text_clean = text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(text_clean)
            else:
                text_clean = text.replace('```json', '').replace('```', '').strip()
                data = json.loads(text_clean)
            
            # Add images for each place
            for stop in data['route']:
                stop['images'] = SearchService.get_images(f"{stop['place']} sightseeing travel")
                
            return data
        except Exception as e:
            print(f"Error generating milestones: {e}")
            return {"error": "Failed to generate milestones", "details": str(e)}

    @staticmethod
    def get_guide_context(place):
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            prompt = f"""
            Provide travel guide context for "{place}".
            
            Format the output strictly as a JSON object:
            {{
                "popular_topics": [
                    {{"label": "Photography Spots", "icon": "fa-camera"}},
                    {{"label": "Best Entry Gates", "icon": "fa-door-open"}},
                    {{"label": "Food near {place}", "icon": "fa-utensils"}},
                    {{"label": "Cultural Etiquette", "icon": "fa-landmark"}}
                ],
                "live_status": {{
                    "status": "Open",
                    "msg": "{place} is currently welcoming visitors.",
                    "details": "Current Wait: ~15 mins"
                }},
                "bot_profile": {{
                    "name": "Skupheon",
                    "subtitle": "AI Travel Specialist",
                    "greeting": "Hello! I am Skupheon, your personal guide to {place}. I can help you plan your entry, suggest the best photography angles, or explain the history of this place. What's on your mind today?"
                }}
            }}
            Do not include any markdown formatting. Just raw JSON.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=1024
            )
            
            text = completion.choices[0].message.content
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(text.strip())
        except Exception as e:
            print(f"Error getting guide context: {e}")
            return {
                "popular_topics": [
                    {"label": "Highlights", "icon": "fa-star"},
                    {"label": "Tips", "icon": "fa-lightbulb"}
                ],
                "live_status": {"status": "Unknown", "msg": "Status info unavailable."},
                "bot_profile": {"name": "Travel AI", "subtitle": "Guide", "greeting": f"Hello! How can I help you explore {place}?"}
            }

    @staticmethod
    def generate_destination_story(name):
        """Generate a beautiful narrative story for a destination using Groq."""
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            prompt = f"""
            Write a detailed and engaging travel story about {name}.

            Requirements:
            - Story length: 4 to 6 paragraphs.
            - Total length: approximately 600 to 900 words.
            - Use simple, natural English.
            - Make it feel like a real travel experience.
            - Describe the place, beauty, atmosphere, culture, and experiences in a smooth flowing narrative.
            - Keep each paragraph medium length and easy to read on a website.
            - Avoid repetition.
            - Keep the story immersive and realistic.
            - Do NOT include headings, titles, bullet points, labels, or meta commentary.
            - Return only continuous paragraphs in the story field.
             
            Format the output strictly as a JSON object:
            {{
                "name": "{name}",
                "story": "The immersive narrative text here...",
                "closing_quote": "A single, powerful inspiring sentence about this place."
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_completion_tokens=1500
            )
            
            text = completion.choices[0].message.content
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(text.strip())
        except Exception as e:
            print(f"Error generating story: {e}")
            return {
                "name": name,
                "story": f"Imagine waking up to the mist-covered hills of {name}. The air is crisp, carrying the scent of fresh tea leaves and damp earth. As the first golden rays of the sun pierce through the canopy, the landscape transforms into a shimmering emerald paradise. Every corner of this enchanted place tells a story of nature's grandeur and timeless beauty.",
                "closing_quote": f"{name} isn't just a place; it's a feeling that stays with you forever."
            }

    @staticmethod
    def explore_destinations(state=None, category=None, search_query=None, page=1):
        """Generate destination list for explore page using Groq + search."""
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            # Build the prompt based on filters.
            # Supports: state-only, category-only, search-only, and all combinations.
            location_scope = f'in the region of "{state}"' if state else "across the world"
            category_filter = f' belonging to any of these categories: "{category}"' if category else ''
            search_filter = f' strongly matching this destination name/keyword query: "{search_query}"' if search_query else ''
            page_context = f" This is page {page} of results, so ensure you provide 9 unique destinations that haven't been listed on previous pages." if page > 1 else ""
            
            prompt = f"""
            List exactly 9 popular and high-quality travel destinations {location_scope}{category_filter}{search_filter}.
            {page_context}
             
            Format the output strictly as a JSON object:
            {{
                "state": "{state or 'Global'}",
                "category": "{category or 'All'}",
                "total_count": <estimated total number of such destinations in this state>,
                "destinations": [
                    {{
                        "name": "Destination Name",
                        "description": "A compelling 1-2 sentence description of this destination for travelers.",
                        "tag": "Category Tag (e.g. Coastal, Heritage, Spiritual, Hill Station, Wildlife, etc.)",
                        "icon": "A Google Material Symbol icon name that fits the tag (e.g. beach_access, temple_hindu, landscape, forest, castle, waves, etc.)",
                        "best_season": "Prime months to visit (e.g. Oct - Mar, Nov - Feb)",
                        "age_suitability": "Primary age group/type (e.g. Families, All Ages, Young Adults, Senior Citizens, Couples)"
                    }}
                ]
            }}
            
            Make the descriptions vivid and travel-inspiring. Each destination should be a real, well-known place.
            Use varied and appropriate tags and icons for each destination.
            Do not include any markdown formatting. Just raw JSON.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=2048
            )
            
            text = completion.choices[0].message.content
            # Robust JSON extraction
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    text_clean = text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(text_clean)
            else:
                text_clean = text.replace('```json', '').replace('```', '').strip()
                data = json.loads(text_clean)
            
            # Enrich each destination with an image (with Unsplash fallback) - PARALLEL
            dest_queries = [f"{d['name']} {state or 'world'} tourist sightseeing iconic" for d in data.get('destinations', [])]
            all_images = SearchService.get_images_parallel(dest_queries)
            for i, dest in enumerate(data.get('destinations', [])):
                imgs = all_images[i] if i < len(all_images) else []
                dest['image'] = imgs[0] if imgs else _get_fallback_image(f"{dest['name']} {state or 'world'}")
             
            return data
        except Exception as e:
            print(f"Error exploring destinations: {e}")
            import traceback
            traceback.print_exc()
            return {"error": "Failed to fetch destinations", "details": str(e)}

    @staticmethod
    def get_destination_detail(name):
        """Generate comprehensive destination detail using Groq + search."""
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            ctx = AIService._get_country_context(name)
            center_lat = ctx['center_coords']['lat']
            center_lng = ctx['center_coords']['lng']
            
            prompt = f"""
            Provide a comprehensive travel overview for the destination "{name}".

            
            Format the output strictly as a JSON object:
            {{
                "name": "{name}",
                "state": "The region/state/province this destination is in",
                "tagline": "A poetic one-line tagline describing this place",
                "tag": "Category tag (e.g. Hill Station, Beach, Heritage, Spiritual, etc.)",
                "coordinates": "Latitude° N/S, Longitude° E/W",
                "overview_p1": "First paragraph of a detailed overview (3-4 sentences about history and significance)",
                "overview_p2": "Second paragraph of overview (2-3 sentences about geography and unique features)",
                "highlights": [
                    {{"name": "Activity 1 name", "keyword": "search keyword for image"}},
                    {{"name": "Activity 2 name", "keyword": "search keyword for image"}},
                    {{"name": "Activity 3 name", "keyword": "search keyword for image"}},
                    {{"name": "Activity 4 name", "keyword": "search keyword for image"}}
                ],
                "best_time": {{
                    "peak": "Peak months (e.g. Oct - Mar)",
                    "summer": {{"months": "Mar-Jun", "temp": "temperature range", "description": "Brief description for summer travel"}},
                    "monsoon": {{"months": "Jul-Sep", "temp": "temperature range", "description": "Brief description for monsoon travel"}},
                    "winter": {{"months": "Oct-Feb", "temp": "temperature range", "description": "Brief description for winter travel"}}
                }},
                "nearby_cities": [
                    {{"name": "City1", "distance": "distance in km"}},
                    {{"name": "City2", "distance": "distance in km"}}
                ],
                "center_coords": {{"lat": {center_lat}, "lng": {center_lng}}},
                "guide": {{
                    "packing": "What to pack advice (2 sentences)",
                    "safety": "Safety and wellness tips (2 sentences)",
                    "culture": "Cultural etiquette tips (2 sentences)",
                    "money": "Currency and tipping tips (2 sentences)"
                }},
                "stats": {{
                    "popularity": "Very High/High/Medium/Low",
                    "ideal_duration": "X - Y Days",
                    "rating": "X.X / 5.0"
                }},
                "how_to_reach": {{
                    "air": "Brief summary of nearest airport and connectivity",
                    "rail": "Brief summary of nearest major railway station",
                    "road": "Connectivity by bus or car from major nearby cities"
                }},
                "local_flavors": [
                    {{"name": "Dish Name", "description": "1 sentence about this local specialty"}},
                    {{"name": "Dish Name 2", "description": "1 sentence about this local specialty"}}
                ],
                "general_timings": "Typical visiting hours if applicable (e.g. 6 AM - 6 PM), otherwise 'Always Open'"
            }}
            
            Make all descriptions vivid and travel-inspiring. Use accurate geographical information.
            Do not include any markdown formatting. Just raw JSON.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=2048
            )
            
            text = completion.choices[0].message.content
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    text_clean = text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(text_clean)
            else:
                text_clean = text.replace('```json', '').replace('```', '').strip()
                data = json.loads(text_clean)
            
            # Fetch hero, highlight images, and map image in PARALLEL
            hero_query = f"{name} {data.get('state', '')} tourism landscape cinematic 4K"
            highlight_queries = [f"{h.get('keyword', h['name'])} {name}" for h in data.get('highlights', [])]
            map_query = f"{name} terrain satellite aerial view"
            all_queries = [hero_query] + highlight_queries + [map_query]
            all_images = SearchService.get_images_parallel(all_queries)
            data['hero_image'] = all_images[0][0] if all_images[0] else _get_fallback_image(f"{name} landscape")
            for i, h in enumerate(data.get('highlights', [])):
                imgs = all_images[i + 1] if i + 1 < len(all_images) else []
                h['image'] = imgs[0] if imgs else _get_fallback_image(f"{h.get('keyword', h['name'])} {name}")
            map_imgs = all_images[-1] if all_images else []
            data['map_image'] = map_imgs[0] if map_imgs else _get_fallback_image(f"{name} aerial")
            
            return data
        except Exception as e:
            print(f"Error getting destination detail: {e}")
            import traceback
            try:
                traceback.print_exc()
            except OSError:
                traceback.print_exc(file=open(os.devnull, 'w'))
            return {
                "name": name,
                "state": "",
                "tagline": f"Discover the beauty of {name}",
                "tag": "Destination",
                "coordinates": "",
                "overview_p1": f"{name} is a beautiful destination worth exploring.",
                "overview_p2": "",
                "center_coords": {"lat": 20.0, "lng": 0.0},
                "highlights": [],
                "best_time": {"peak": "Oct - Mar", "summer": {"months": "Mar-Jun", "temp": "", "description": ""}, "monsoon": {"months": "Jul-Sep", "temp": "", "description": ""}, "winter": {"months": "Oct-Feb", "temp": "", "description": ""}},
                "nearby_cities": [],
                "guide": {"packing": "", "safety": "", "culture": "", "money": ""},
                "stats": {"popularity": "High", "ideal_duration": "2-3 Days", "rating": "4.5 / 5.0"},
                "how_to_reach": {"air": "N/A", "rail": "N/A", "road": "N/A"},
                "local_flavors": [],
                "general_timings": "Always Open",
                "hero_image": "",
                "map_image": "",
                "error": str(e)
            }

    @staticmethod
    def get_attractions(name):
        """Generate attractions list for a destination using Groq + search."""
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            ctx = AIService._get_country_context(name)
            center_lat = ctx['center_coords']['lat']
            center_lng = ctx['center_coords']['lng']
            
            prompt = f"""
            List 6 must-visit attractions/landmarks in "{name}".
            
            Format the output strictly as a JSON object:
            {{
                "destination": "{name}",
                "center_coords": {{"lat": {center_lat}, "lng": {center_lng}}},
                "attractions": [
                    {{
                        "name": "Attraction Name",
                        "location": "Specific area/neighborhood within {name}",
                        "description": "A compelling 1-2 sentence description of this attraction for travelers.",
                        "tag": "Category (e.g. National Park, Temple, Beach, Museum, Viewpoint, Fort, Dam & Lake, Waterfall, Garden, etc.)",
                        "entry_fee": "Entry fee (e.g. $10+, Free, €5, etc.)",
                        "icon": "A Google Material Symbol icon name (e.g. park, temple_hindu, water_drop, museum, visibility, castle, waves, forest, etc.)",
                        "lat": 12.3456, // VERY IMPORTANT: Use the REAL geographic latitude of this specific attraction. Do not copy the center coords.
                        "lng": 78.9012 // VERY IMPORTANT: Use the REAL geographic longitude of this specific attraction. Do not copy the center coords.
                    }}
                ]
            }}
            
            Make the descriptions vivid and informative. Each attraction should be a real, well-known place.
            Use varied and appropriate tags for each attraction.
            Do not include any markdown formatting. Just raw JSON.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=2048
            )
            
            text = completion.choices[0].message.content
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    text_clean = text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(text_clean)
            else:
                text_clean = text.replace('```json', '').replace('```', '').strip()
                data = json.loads(text_clean)
            
            # Enrich each attraction with an image and timing - images PARALLEL
            attractions = data.get('attractions', [])
            attr_image_queries = []
            for attr in attractions:
                attr_name = (attr.get('name') or '').strip() or f"{name} Attraction"
                attr_image_queries.append(f"{attr_name} {name} {data.get('state', '')} tourism landmark sightseeing")
            map_query = f"{name} aerial satellite terrain view"
            all_queries = attr_image_queries + [map_query]
            all_images = SearchService.get_images_parallel(all_queries)

            for i, attr in enumerate(attractions):
                try:
                    attr_name = (attr.get('name') or '').strip()
                    if not attr_name:
                        attr_name = f"{name} Attraction"
                        attr['name'] = attr_name

                    imgs = all_images[i] if i < len(all_images) else []
                    attr['image'] = imgs[0] if imgs else _get_fallback_image(f"{attr_name} {name}")

                    # Fetch timing using search
                    search_query = f"{attr_name} {name} opening closing hours timings"
                    search_results = SearchService.get_search_results(search_query)

                    timing = attr.get('timings') or attr.get('opening_hours') or attr.get('hours')

                    # Try knowledge graph first
                    if not timing:
                        kg = search_results.get('knowledgeGraph', {})
                        if 'hours' in kg:
                            timing = kg['hours']
                        elif 'attributes' in kg:
                            attrs_dict = kg.get('attributes', {})
                            for key in ['Hours', 'hours', 'Opening hours', 'Timings', 'Open hours']:
                                if key in attrs_dict:
                                    timing = attrs_dict[key]
                                    break

                    # Try answer box
                    if not timing:
                        answer_box = search_results.get('answerBox', {})
                        if answer_box:
                            answer_text = answer_box.get('answer', '') or answer_box.get('snippet', '')
                            if answer_text:
                                time_match = re.search(
                                    r'\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\s*[-â€“to]+\s*\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)',
                                    answer_text
                                )
                                if time_match:
                                    timing = time_match.group(0)

                    # Try search snippets with improved patterns
                    if not timing:
                        time_patterns = [
                            r'\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\s*[-â€“to]+\s*\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)',
                            r'\d{1,2}:\d{2}\s*[-â€“to]+\s*\d{1,2}:\d{2}',
                            r'(?:open|available)\s+24\s*(?:hours|hrs)',
                            r'sunrise\s+to\s+sunset',
                        ]

                        for organic in search_results.get('organic', []):
                            snippet = organic.get('snippet', '')
                            snippet_lower = snippet.lower()
                            if any(kw in snippet_lower for kw in ['opening', 'hours', 'open', 'timing', 'closed', 'visit']):
                                for pattern in time_patterns:
                                    time_match = re.search(pattern, snippet, re.I)
                                    if time_match:
                                        timing = time_match.group(0).strip()
                                        break
                            if timing:
                                break

                    if timing:
                        timing = str(timing).strip().replace('â€“', '-').replace('  ', ' ')
                        timing = re.sub(r'\b(am|pm)\b', lambda m: m.group(0).upper(), timing, flags=re.I)

                    attr['timings'] = timing if timing else 'Check local timing'
                except Exception:
                    attr['timings'] = attr.get('timings') or 'Check local timing'
                    if not attr.get('image'):
                        attr['image'] = _get_fallback_image(f"{attr.get('name', name)} {name}")
            # Map image already fetched in parallel above
            map_imgs = all_images[-1] if all_images else []
            data['map_image'] = map_imgs[0] if map_imgs else _get_fallback_image(f"{name} aerial")
            
            return data
        except Exception as e:
            print(f"Error getting attractions: {e}")
            import traceback
            traceback.print_exc()
            return {"destination": name, "attractions": [], "map_image": "", "error": str(e)}


    @staticmethod
    def get_itinerary(name, days=3):
        """Generate a multi-day itinerary for a destination using Groq + search."""
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            ctx = AIService._get_country_context(name)
            country_suffix = f" in {ctx['country']}" if ctx['country'] else ""
            
            prompt = f"""
            Create a detailed {days}-day travel itinerary for "{name}"{country_suffix}.
            
            Format the output strictly as a JSON object:
            {{
                "destination": "{name}",
                "center_coords": {{"lat": {ctx['center_coords']['lat']}, "lng": {ctx['center_coords']['lng']}}},
                "total_days": {days},
                "days": [
                    {{
                        "day_number": 1,
                        "title": "A creative theme title for this day",
                        "weather_note": "Expected weather",
                        "activities": [
                            {{
                                "time": "09:00 AM",
                                "name": "Activity Name",
                                "description": "Description...",
                                "keyword": "search keyword",
                                "lat": 12.3456,
                                "lng": 78.9012,
                                "estimated_cost_usd": 25
                            }}
                        ]
                    }}
                ],
                "budget_summary": {{
                    "accommodation_avg_per_day": 100,
                    "food_avg_per_day": 50,
                    "transport_avg_per_day": 30,
                    "currency": "{ctx['currency']}"
                }}
            }}
            
            Allocate time properly to time-consuming activities. Include a realistic number of activities per day (e.g., 2 to 4 activities depending on duration). Do not force exactly 3 activities per day.
            Make the itinerary practical and achievable. Include real places in {name}.
            Do not include any markdown formatting. Just raw JSON.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=2048
            )
            
            text = completion.choices[0].message.content
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    text_clean = text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(text_clean)
            else:
                text_clean = text.replace('```json', '').replace('```', '').strip()
                data = json.loads(text_clean)
            
            # Fetch images for each activity
            for day in data.get('days', []):
                for act in day.get('activities', []):
                    keyword = act.get('keyword', act['name'])
                    images = SearchService.get_images(f"{keyword} {name}")
                    act['image'] = images[0] if images else _get_fallback_image(f"{keyword} {name}")
            
            # Fetch route map image
            map_images = SearchService.get_images(f"{name} map route tourist trail")
            data['route_map'] = map_images[0] if map_images else _get_fallback_image(f"{name} panorama")
            
            return data
        except Exception as e:
            print(f"Error generating itinerary for {name}: {e}")
            import traceback
            traceback.print_exc()
            return {"destination": name, "total_days": days, "days": [], "route_map": "", "error": str(e)}

    @staticmethod
    def get_gallery(name, count=20):
        """Fetch a gallery of images for a destination."""
        try:
            queries = [
                f"\"{name}\" tourism landmarks travel photography",
                f"\"{name}\" famous tourist attractions photography",
                f"\"{name}\" scenic viewpoint travel photo",
                f"\"{name}\" culture heritage travel image",
                f"\"{name}\" destination gallery",
            ]
            all_images = []
            seen = set()
            for q in queries:
                images = SearchService.get_images(q)
                for img in images:
                    if img not in seen:
                        seen.add(img)
                        all_images.append(img)
                    if len(all_images) >= count:
                        break
                if len(all_images) >= count:
                    break
            
            # Ensure at least 4 destination-focused images whenever possible
            if len(all_images) < 4:
                booster_queries = [
                    f"\"{name}\" lake mountain landscape",
                    f"\"{name}\" temple fort architecture",
                    f"\"{name}\" aerial destination photo",
                ]
                for q in booster_queries:
                    for img in SearchService.get_images(q):
                        if img not in seen:
                            seen.add(img)
                            all_images.append(img)
                        if len(all_images) >= max(4, count):
                            break
            
            # If still short, add some fallbacks but don't overwrite
            if len(all_images) < count:
                fallback_keywords = [name, f"{name} beach", f"{name} temple", f"{name} landscape",
                                     f"{name} architecture", f"{name} nature", f"{name} sunset",
                                     f"{name} mountain", f"{name} culture", f"{name} heritage"]
                for kw in fallback_keywords:
                    if len(all_images) >= count: break
                    img = _get_fallback_image(kw)
                    if img not in seen:
                        seen.add(img)
                        all_images.append(img)

            return {"images": all_images[:count]}
        except Exception as e:
            print(f"Gallery error for {name}: {e}")
            return {"images": [], "error": str(e)}

    @staticmethod
    def get_hero_image(name):
        """Fetch a single high-quality hero image for a destination."""
        try:
            # Targeted queries for "Hero-like" images (landscape, high-res, iconic)
            queries = [
                f"{name} tourism landscape 4K",
                f"{name} sunset skyline",
                f"{name} landmark aerial",
                f"{name} tourism"
            ]
            
            for q in queries:
                images = SearchService.get_images(q)
                if images:
                    # SearchService already ranks these by quality/source/aspect-ratio
                    return {"url": images[0], "query": q, "success": True}
            
            return {"url": _get_fallback_image(f"{name} landscape"), "success": False, "error": "No images found"}
        except Exception as e:
            print(f"Hero image fetch error: {e}")
            return {"url": _get_fallback_image(name), "success": False, "error": str(e)}

    @staticmethod
    def _ensure_minimum_activities(plan, min_per_day=3):
        itinerary = plan.get('itinerary')
        if not isinstance(itinerary, list):
            return plan

        center = plan.get('center_coords') or {}
        base_lat = float(center.get('lat', 20.0))
        base_lng = float(center.get('lng', 0.0))

        for day_idx, day in enumerate(itinerary):
            activities = day.get('activities')
            if not isinstance(activities, list):
                activities = []
                day['activities'] = activities

            while len(activities) < min_per_day:
                slot = len(activities)
                slot_time = ["Morning", "Afternoon", "Evening"][slot] if slot < 3 else f"Stop {slot + 1}"
                offset = 0.01 * (slot + 1 + (day_idx * 0.3))
                activities.append({
                    "time": slot_time,
                    "name": f"{day.get('theme', 'Local')} Discovery {slot + 1}",
                    "description": "Recommended local experience aligned to your trip preferences.",
                    "icon": "place",
                    "image_query": f"{plan.get('destination', '')} travel destination",
                    "lat": base_lat + offset,
                    "lng": base_lng + offset,
                    "estimated_cost_usd": 25
                })

            for act_idx, act in enumerate(activities):
                try:
                    act_lat = float(act.get('lat'))
                    act_lng = float(act.get('lng'))
                    if not (math.isfinite(act_lat) and math.isfinite(act_lng)):
                        raise ValueError("non-finite coords")
                    act['lat'] = act_lat
                    act['lng'] = act_lng
                except Exception:
                    offset = 0.004 * (act_idx + 1 + day_idx)
                    act['lat'] = base_lat + offset
                    act['lng'] = base_lng - offset

        return plan

    @staticmethod
    def generate_plan_from_prompt(prompt):
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            system_prompt = """You are an expert travel planner Skupheon. 
Based on the user's prompt, generate a structured trip itinerary.
The output MUST be a JSON object with the following structure:
{
  "destination": "Main destination name",
  "country": "Full country name (e.g. 'Japan', 'Italy', 'Thailand')",
  "tagline": "A catchy tagline for the trip",
  "duration": "Duration in days",
  "center_coords": {"lat": 35.6762, "lng": 139.6503},
  "itinerary": [
    {
      "day": 1,
      "theme": "Day theme",
      "activities": [
        {
          "time": "Morning/Afternoon/Evening",
          "name": "Activity name",
          "description": "Short description",
          "icon": "A material design icon name suitable for the activity",
          "image_query": "Specific visual search query for this activity (e.g. 'Fushimi Inari shrine torii gates')",
          "lat": 35.6762,
          "lng": 139.6503
        }
      ]
    }
  ],
  "budget_summary": {
    "currency": "USD",
    "currency_symbol": "$",
    "total_estimated_expenditure": 2500,
    "accommodation_avg_per_day": 150,
    "food_avg_per_day": 50,
    "transport_avg_per_day": 30,
    "activities_total": 200
  },
  "travel_tips": ["Tip 1", "Tip 2", "Tip 3"]
}
Maintain a high-quality, professional, and inspiring tone.
Allocate time properly to time-consuming activities and plan realistically. Do NOT just hardcode 3 activities in a day. The number of activities per day should vary based on what makes sense for the destination and duration.
Be specific to the prompt provided. If the user asks for a long trip (e.g. 15-30 days), ensure you provide activities for EVERY day, keeping the JSON well-formed and complete. Do NOT truncate or skip days. For long trips, keep activity descriptions concise to stay within token limits. 
Always include a "hero_image_query" field which is a specific search term to find a stunning background image for this trip (e.g. 'Santorini sunset caldera' or 'Kyoto cherry blossoms in spring').
You MUST detect the country the user is asking about and use that country's currency in the budget. For example: Japan uses JPY, Italy uses EUR, Thailand uses THB, United States uses USD. Use realistic prices for the local currency.
"""

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_completion_tokens=4096
            )
            
            plan = json.loads(completion.choices[0].message.content)
            
            dest_name = plan.get('destination', '')
            dest_country = plan.get('country', '')
            
            if not plan.get('center_coords'):
                ctx = AIService._get_country_context(dest_name)
                plan['center_coords'] = ctx['center_coords']
            
            # Fetch ALL images in PARALLEL
            act_queries = []
            act_refs = []
            for day in plan.get('itinerary', []):
                for act in day.get('activities', []):
                    q = act.get('image_query') or f"{act.get('name')} {dest_name} {dest_country} tourist attraction"
                    act_queries.append(q)
                    act_refs.append(act)
            hero_query = plan.get('hero_image_query') or f"{dest_name} travel background"
            all_images = SearchService.get_images_parallel(act_queries + [hero_query])
            for i, act in enumerate(act_refs):
                imgs = all_images[i] if i < len(all_images) else []
                act['image_url'] = imgs[0] if imgs else _get_fallback_image(f"{act.get('name', '')} {dest_name}")
                if 'lat' not in act or 'lng' not in act:
                    act['lat'] = plan.get('center_coords', {}).get('lat', 20.0)
                    act['lng'] = plan.get('center_coords', {}).get('lng', 0.0)
            hero_imgs = all_images[-1] if all_images else []
            plan['hero_image'] = hero_imgs[0] if hero_imgs else "https://images.unsplash.com/photo-1548013146-72479768bbaa?auto=format&fit=crop&q=80&w=2000"
            
            return plan
        except Exception as e:
            print(f"AI Plan error: {e}")
            return {"error": "Failed to generate plan"}

class WeatherService:
    _cache = {}
    _cache_ttl_seconds = 15 * 60

    @staticmethod
    def _get_db_cache(city_key):
        try:
            from models import db, WeatherCache
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            record = WeatherCache.query.filter_by(city_key=city_key).first()
            if record and record.expires_at > now:
                return record.data
            if record:
                db.session.delete(record)
                db.session.commit()
        except Exception:
            pass
        return None

    @staticmethod
    def _set_db_cache(city_key, data):
        try:
            from models import db, WeatherCache
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            existing = WeatherCache.query.filter_by(city_key=city_key).first()
            if existing:
                existing.data = data
                existing.fetched_at = now
                existing.expires_at = now + timedelta(seconds=WeatherService._cache_ttl_seconds)
            else:
                record = WeatherCache(
                    city_key=city_key,
                    data=data,
                    fetched_at=now,
                    expires_at=now + timedelta(seconds=WeatherService._cache_ttl_seconds)
                )
                db.session.add(record)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Weather DB cache error: {e}")

    # WMO weather interpretation codes → (description, main category, icon code)
    _WMO_CODES = {
        0: ("Clear Sky", "Clear", "01d"),
        1: ("Mainly Clear", "Clouds", "02d"),
        2: ("Partly Cloudy", "Clouds", "03d"),
        3: ("Overcast", "Clouds", "04d"),
        45: ("Foggy", "Fog", "50d"),
        48: ("Rime Fog", "Fog", "50d"),
        51: ("Light Drizzle", "Drizzle", "09d"),
        53: ("Moderate Drizzle", "Drizzle", "09d"),
        55: ("Dense Drizzle", "Drizzle", "09d"),
        56: ("Freezing Drizzle", "Drizzle", "09d"),
        57: ("Heavy Freezing Drizzle", "Drizzle", "09d"),
        61: ("Slight Rain", "Rain", "10d"),
        63: ("Moderate Rain", "Rain", "10d"),
        65: ("Heavy Rain", "Rain", "10d"),
        66: ("Freezing Rain", "Rain", "10d"),
        67: ("Heavy Freezing Rain", "Rain", "10d"),
        71: ("Slight Snow", "Snow", "13d"),
        73: ("Moderate Snow", "Snow", "13d"),
        75: ("Heavy Snow", "Snow", "13d"),
        77: ("Snow Grains", "Snow", "13d"),
        80: ("Light Showers", "Rain", "09d"),
        81: ("Moderate Showers", "Rain", "09d"),
        82: ("Violent Showers", "Rain", "09d"),
        85: ("Light Snow Showers", "Snow", "13d"),
        86: ("Heavy Snow Showers", "Snow", "13d"),
        95: ("Thunderstorm", "Thunderstorm", "11d"),
        96: ("Thunderstorm with Hail", "Thunderstorm", "11d"),
        99: ("Severe Thunderstorm", "Thunderstorm", "11d"),
    }

    @staticmethod
    def _cache_key(city, lat=None, lon=None):
        city_key = (city or "").strip().lower()
        lat_key = round(float(lat), 4) if lat is not None else None
        lon_key = round(float(lon), 4) if lon is not None else None
        return (city_key, lat_key, lon_key)

    @staticmethod
    def _request_json(url, params, timeout=7, retries=2):
        last_error = None
        for attempt in range(retries + 1):
            try:
                resp = requests.get(url, params=params, timeout=timeout)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code in (429, 500, 502, 503, 504):
                    time.sleep(0.35 * (attempt + 1))
                    continue
                return None
            except requests.exceptions.RequestException as e:
                last_error = e
                time.sleep(0.35 * (attempt + 1))
        if last_error:
            print(f"[Weather] Request failed: {last_error}")
        return None

    @staticmethod
    def _wmo_to_condition(code):
        desc, main, icon_code = WeatherService._WMO_CODES.get(code, ("Unknown", "Clear", "01d"))
        return {
            "text": desc,
            "icon": f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
            "main": main,
        }

    @staticmethod
    def _geocode_city(city):
        """Resolve a city name to (lat, lon, display_name, country) using Open-Meteo geocoding."""
        clean = city.split(",")[0].strip()
        data = WeatherService._request_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            {"name": clean, "count": 1, "language": "en"},
        )
        if data and isinstance(data.get("results"), list) and data["results"]:
            r = data["results"][0]
            return r.get("latitude"), r.get("longitude"), r.get("name", clean), r.get("country_code")
        return None, None, None, None

    @staticmethod
    def get_forecast(city, lat=None, lon=None):
        try:
            import datetime
            if not city:
                return None

            cache_key = WeatherService._cache_key(city, lat=lat, lon=lon)
            now_ts = time.time()
            cached = WeatherService._cache.get(cache_key)
            if cached and (now_ts - cached.get("ts", 0) < WeatherService._cache_ttl_seconds):
                return cached.get("data")

            db_cache_key = f"{cache_key[0]}:{cache_key[1]}:{cache_key[2]}"
            db_cached = WeatherService._get_db_cache(db_cache_key)
            if db_cached:
                WeatherService._cache[cache_key] = {"ts": now_ts, "data": db_cached}
                return db_cached

            clean_city = city.split(",")[0].strip()

            # Resolve coordinates
            resolved_lat, resolved_lon, resolved_name, resolved_country = None, None, None, None
            if lat is not None and lon is not None:
                resolved_lat, resolved_lon = float(lat), float(lon)
                resolved_name = clean_city
                print(f"[Weather] Using provided coords ({lat}, {lon}) for {clean_city}")
            else:
                candidates = [clean_city, city.strip()]
                for q in candidates:
                    resolved_lat, resolved_lon, resolved_name, resolved_country = WeatherService._geocode_city(q)
                    if resolved_lat is not None:
                        break
                if resolved_lat is None:
                    print(f"[Weather] Could not geocode city: {city}")
                    return None
                print(f"[Weather] Geocoded {clean_city} → ({resolved_lat}, {resolved_lon})")

            # Fetch current + daily forecast from Open-Meteo
            weather_data = WeatherService._request_json(
                "https://api.open-meteo.com/v1/forecast",
                {
                    "latitude": resolved_lat,
                    "longitude": resolved_lon,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                    "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum,wind_speed_10m_max,relative_humidity_2m_mean",
                    "timezone": "auto",
                    "forecast_days": 7,
                },
            )
            if not weather_data:
                print(f"[Weather] Open-Meteo request failed for {clean_city}")
                return None

            today = datetime.date.today()
            forecast_days = []

            # Current weather → today
            current = weather_data.get("current", {})
            current_code = current.get("weather_code", 0)
            cond = WeatherService._wmo_to_condition(current_code)

            forecast_days.append({
                "date": today.strftime("%Y-%m-%d"),
                "date_label": "Today",
                "day": {
                    "avgtemp_c": round(current.get("temperature_2m", 0), 1),
                    "mintemp_c": round(current.get("temperature_2m", 0), 1),
                    "maxtemp_c": round(current.get("temperature_2m", 0), 1),
                    "humidity": current.get("relative_humidity_2m", 0),
                    "wind_kph": round(current.get("wind_speed_10m", 0), 1),
                    "condition": cond,
                },
            })

            # Daily forecast (skip today at index 0)
            daily = weather_data.get("daily", {})
            daily_dates = daily.get("time", [])
            for i, date_str in enumerate(daily_dates):
                if date_str == today.strftime("%Y-%m-%d"):
                    continue
                day_code = daily.get("weather_code", [0])[i] if i < len(daily.get("weather_code", [])) else 0
                day_cond = WeatherService._wmo_to_condition(day_code)
                day_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")

                forecast_days.append({
                    "date": date_str,
                    "date_label": day_dt.strftime("%a").upper(),
                    "day": {
                        "avgtemp_c": round(
                            (daily["temperature_2m_max"][i] + daily["temperature_2m_min"][i]) / 2, 1
                        ) if i < len(daily.get("temperature_2m_max", [])) else 0,
                        "mintemp_c": round(daily["temperature_2m_min"][i], 1) if i < len(daily.get("temperature_2m_min", [])) else 0,
                        "maxtemp_c": round(daily["temperature_2m_max"][i], 1) if i < len(daily.get("temperature_2m_max", [])) else 0,
                        "humidity": round(daily["relative_humidity_2m_mean"][i]) if i < len(daily.get("relative_humidity_2m_mean", [])) else 0,
                        "wind_kph": round(daily["wind_speed_10m_max"][i], 1) if i < len(daily.get("wind_speed_10m_max", [])) else 0,
                        "condition": day_cond,
                    },
                })

                if len(forecast_days) >= 7:
                    break

            print(f"[Weather] Success: {len(forecast_days)} day(s) of forecast for {clean_city}")

            payload = {
                "location": {
                    "name": resolved_name or clean_city,
                    "country": resolved_country or "",
                    "lat": resolved_lat,
                    "lon": resolved_lon,
                },
                "meta": {
                    "source": "Open-Meteo",
                    "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
                },
                "forecast": {
                    "forecastday": forecast_days,
                },
            }
            WeatherService._cache[cache_key] = {"ts": now_ts, "data": payload}
            WeatherService._set_db_cache(db_cache_key, payload)
            return payload

        except requests.exceptions.Timeout:
            print(f"[Weather] Timeout fetching weather for {city}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"[Weather] Connection error fetching weather for {city}")
            return None
        except Exception as e:
            print(f"[Weather] API Error: {e}")
            import traceback
            traceback.print_exc()
            return None
