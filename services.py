import heapq
import json
import requests
import re
import base64
from groq import Groq
from config import Config

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
    # Find matching category
    for keyword, images in _FALLBACK_IMAGES.items():
        if keyword in query_lower:
            # Use hash of query for consistent but varied selection
            idx = hash(query) % len(images)
            return images[idx]
    
    # Default: use hash for variety
    idx = hash(query) % len(_DEFAULT_IMAGES)
    return _DEFAULT_IMAGES[idx]


class SerperService:
    @staticmethod
    def _tokenize_query(text):
        stop = {
            'india', 'tourism', 'tourist', 'travel', 'sightseeing', 'landmark', 'landmarks',
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
            'cdn.pixabay.com', 'flickr.com', 'staticflickr.com'
        ]
        if any(h in url.lower() for h in trusted_hosts):
            score += 5

        for tok in required_tokens[:4]:
            if tok in hay:
                score += 3
        for tok in required_tokens[4:8]:
            if tok in hay:
                score += 1

        # Prefer landscape-ish dimensions when available
        w = img_obj.get('imageWidth') or img_obj.get('width') or 0
        h = img_obj.get('imageHeight') or img_obj.get('height') or 0
        try:
            w = int(w)
            h = int(h)
            if w >= 800 and h >= 500:
                score += 2
            if w > h:
                score += 1
        except Exception:
            pass

        return score

    @staticmethod
    def get_images(query):
        api_key = Config.SERPER_API_KEY
        if not api_key:
            return []
            
        api_url = "https://google.serper.dev/images"
        payload = json.dumps({
            "q": query,
            "num": 30,
            "gl": "in",
            "hl": "en"
        })
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request("POST", api_url, headers=headers, data=payload, timeout=5)
            if response.status_code == 200:
                results = response.json()
                ranked = []
                required_tokens = SerperService._tokenize_query(query)
                for img in results.get('images', []):
                    url = str(img.get('imageUrl') or '')
                    if not SerperService._looks_like_real_photo(url, img):
                        continue
                    score = SerperService._score_image_candidate(img, required_tokens)
                    ranked.append((score, url))

                ranked.sort(key=lambda x: x[0], reverse=True)
                images = []
                seen = set()
                for _, url in ranked:
                    if url and url not in seen:
                        seen.add(url)
                        images.append(url)
                    if len(images) >= 12:
                        break

                if images:
                    return images

                # Secondary stricter query pass for relevance
                strict_query = f"\"{query}\" travel photography"
                strict_payload = json.dumps({
                    "q": strict_query,
                    "num": 20,
                    "gl": "in",
                    "hl": "en"
                })
                strict_resp = requests.request("POST", api_url, headers=headers, data=strict_payload, timeout=5)
                if strict_resp.status_code == 200:
                    strict_results = strict_resp.json()
                    fallback = []
                    for img in strict_results.get('images', []):
                        img_url = str(img.get('imageUrl') or '')
                        if SerperService._looks_like_real_photo(img_url, img):
                            fallback.append(img_url)
                        if len(fallback) >= 8:
                            break
                    return fallback
                return []
            print(f"Serper API returned status {response.status_code}")
            return []
        except Exception as e:
            print(f"Serper API Error: {e}")
            return []

    @staticmethod
    def get_search_results(query):
        api_key = Config.SERPER_API_KEY
        if not api_key:
            return {}
            
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": query,
            "num": 5,
            "gl": "in",
            "hl": "en"
        })
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Serper Search API Error: {e}")
            return {}

class AIService:
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
    def general_chat(message, history=None):
        """
        Generic chat for the Profile AI Assistant with history support.
        history: list of dicts like [{"role": "user", "content": "..."}, {"role": "ai", "content": "..."}]
        """
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            system_msg = """
            You are Skupheon, the intelligent travel assistant for RoutheonSkups. 
            You are helpful, friendly, and expert in all things travel.
            Your goal is to assist the user with their travel queries, provide destination insights, help with budgets, or just chat about their upcoming trips.
            Keep your responses concise but insightful. 
            """
            
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
            You are a smart travel assistant. Your goal is to help users plan trips.
            if the user asks to plan a trip or gives enough details (destination, days), 
            extract the following information in a JSON block at the END of your response (after your natural language reply).
            
            JSON Structure:
            {{
                "intent": "plan_trip",
                "destination": "Paris",
                "days": 3,
                "preferences": "museums, food"
            }}
            
            If the user is just asking general questions, just reply normally.
            If the user mentions a place but doesn't explicitly ask for a full plan yet, verify if they want images.
            
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
                images = SerperService.get_images(f"{destination} India tourist attractions sightseeing high quality")
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
            
            prompt = f"""
            Create a highly detailed cinematic {days}-day itinerary for a trip to {destination}, India.
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
                    "currency": "USD"
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
            
            # Enrich with real images and robust coordinates
            dest_name = itinerary.get('destination', destination)
            if not itinerary.get('center_coords'):
                itinerary['center_coords'] = {"lat": 20.5937, "lng": 78.9629} # Center of India fallback
                
            for day in itinerary.get('days', []):
                for act in day.get('activities', []):
                    # Fetch real image for the activity
                    query = f"{act.get('title')} {dest_name} India sightseeing"
                    images = SerperService.get_images(query)
                    if images:
                        act['image_url'] = images[0]
                    else:
                        act['image_url'] = _get_fallback_image(f"{act.get('title', '')} {dest_name}")
                    
                    # Ensure coords
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
            
            # Add images using Serper
            place_images = SerperService.get_images(f"{place} India travel destination tourism high resolution")
            data['images'] = place_images if place_images else [_get_fallback_image(f"{place} landscape")]
            for attr in data['attractions']:
                attr_images = SerperService.get_images(f"{attr['name']} {place} India tourist attraction")
                attr['images'] = attr_images if attr_images else [_get_fallback_image(f"{attr['name']} {place}")]
            
            # Calculate shortest path between first and last attraction as a showcase
            if len(data['attractions']) >= 2:
                start = data['attractions'][0]['name']
                end = data['attractions'][-1]['name']
                data['shortest_path'] = GraphService.get_shortest_path(data['graph'], start, end)
            
            return data
        except Exception as e:
            print(f"Error exploring place: {e}")
            return {"error": "Failed to explore place", "details": str(e)}
            
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
                stop['images'] = SerperService.get_images(f"{stop['place']} sightseeing India travel")
                
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
                    "greeting": "Namaste! I am Skupheon, your personal guide to {place}. I can help you plan your entry, suggest the best photography angles, or explain the history of this wonder. What's on your mind today?"
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
        """Generate destination list for explore page using Groq + Serper."""
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            # Build the prompt based on filters.
            # Supports: state-only, category-only, search-only, and all combinations.
            location_scope = f'in the Indian state of "{state}"' if state else "across India"
            category_filter = f' belonging to any of these categories: "{category}"' if category else ''
            search_filter = f' strongly matching this destination name/keyword query: "{search_query}"' if search_query else ''
            page_context = f" This is page {page} of results, so ensure you provide 9 unique destinations that haven't been listed on previous pages." if page > 1 else ""
            
            prompt = f"""
            List exactly 9 popular and high-quality travel destinations {location_scope}{category_filter}{search_filter}.
            {page_context}
             
            Format the output strictly as a JSON object:
            {{
                "state": "{state or 'India'}",
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
            
            # Enrich each destination with an image from Serper (with Unsplash fallback)
            for dest in data.get('destinations', []):
                geo_context = state if state else "India"
                images = SerperService.get_images(f"{dest['name']} {geo_context} tourist sightseeing iconic")
                dest['image'] = images[0] if images else _get_fallback_image(f"{dest['name']} {geo_context}")
             
            return data
        except Exception as e:
            print(f"Error exploring destinations: {e}")
            import traceback
            traceback.print_exc()
            return {"error": "Failed to fetch destinations", "details": str(e)}

    @staticmethod
    def get_destination_detail(name):
        """Generate comprehensive destination detail using Groq + Serper."""
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            prompt = f"""
            Provide a comprehensive travel overview for the destination "{name}" in India.
            
            Format the output strictly as a JSON object:
            {{
                "name": "{name}",
                "state": "The Indian state this destination is in",
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
                "center_coords": {{"lat": 28.6139, "lng": 77.2090}},
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
            
            # Fetch hero image
            hero_images = SerperService.get_images(f"{name} {data.get('state', 'India')} tourism landscape cinematic 4K")
            data['hero_image'] = hero_images[0] if hero_images else _get_fallback_image(f"{name} landscape")
            
            # Fetch images for highlights
            for h in data.get('highlights', []):
                imgs = SerperService.get_images(f"{h.get('keyword', h['name'])} {name} India")
                h['image'] = imgs[0] if imgs else _get_fallback_image(f"{h.get('keyword', h['name'])} {name}")
            
            # Fetch map image
            map_images = SerperService.get_images(f"{name} India terrain satellite aerial view")
            data['map_image'] = map_images[0] if map_images else _get_fallback_image(f"{name} aerial")
            
            return data
        except Exception as e:
            print(f"Error getting destination detail: {e}")
            import traceback
            traceback.print_exc()
            return {
                "name": name,
                "state": "India",
                "tagline": f"Discover the beauty of {name}",
                "tag": "Destination",
                "coordinates": "",
                "overview_p1": f"{name} is a beautiful destination in India worth exploring.",
                "overview_p2": "",
                "center_coords": {"lat": 28.6139, "lng": 77.2090},
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
        """Generate attractions list for a destination using Groq + Serper."""
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            prompt = f"""
            List 6 must-visit attractions/landmarks in "{name}", India.
            
            Format the output strictly as a JSON object:
            {{
                "destination": "{name}",
                "center_coords": {{"lat": 28.6139, "lng": 77.2090}},
                "attractions": [
                    {{
                        "name": "Attraction Name",
                        "location": "Specific area/neighborhood within {name}",
                        "description": "A compelling 1-2 sentence description of this attraction for travelers.",
                        "tag": "Category (e.g. National Park, Temple, Beach, Museum, Viewpoint, Fort, Dam & Lake, Waterfall, Garden, etc.)",
                        "entry_fee": "Entry fee (e.g. ₹125+, Free, ₹50, etc.)",
                        "icon": "A Google Material Symbol icon name (e.g. park, temple_hindu, water_drop, museum, visibility, castle, waves, forest, etc.)",
                        "lat": 12.3456,
                        "lng": 78.9012
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
            
            # Enrich each attraction with a Serper image and timing
            for attr in data.get('attractions', []):
                try:
                    attr_name = (attr.get('name') or '').strip()
                    if not attr_name:
                        attr_name = f"{name} Attraction"
                        attr['name'] = attr_name

                    # Fetch image
                    images = SerperService.get_images(f"{attr_name} {name} {data.get('state', 'India')} tourism landmark sightseeing")
                    attr['image'] = images[0] if images else _get_fallback_image(f"{attr_name} {name}")

                    # Fetch timing using Serper Search
                    search_query = f"{attr_name} {name} India opening closing hours timings"
                    search_results = SerperService.get_search_results(search_query)

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
            # Get map image
            map_images = SerperService.get_images(f"{name} India aerial satellite terrain view")
            data['map_image'] = map_images[0] if map_images else _get_fallback_image(f"{name} aerial")
            
            return data
        except Exception as e:
            print(f"Error getting attractions: {e}")
            import traceback
            traceback.print_exc()
            return {"destination": name, "attractions": [], "map_image": "", "error": str(e)}

    @staticmethod
    def get_itinerary(name, days=3):
        """Generate a multi-day itinerary for a destination using Groq + Serper."""
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            
            prompt = f"""
            Create a detailed {days}-day travel itinerary for "{name}" in India.
            
            Format the output strictly as a JSON object:
            {{
                "destination": "{name}",
                "center_coords": {{"lat": 28.6139, "lng": 77.2090}},
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
                                "estimated_cost_inr": 500
                            }}
                        ]
                    }}
                ],
                "budget_summary": {{
                    "accommodation_avg_per_day": 3000,
                    "food_avg_per_day": 1500,
                    "transport_avg_per_day": 1000,
                    "currency": "INR"
                }}
            }}
            
            Each day should have exactly 3 activities at different times of day (morning, midday, afternoon/evening).
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
                    images = SerperService.get_images(f"{keyword} {name} India")
                    act['image'] = images[0] if images else _get_fallback_image(f"{keyword} {name}")
            
            # Fetch route map image
            map_images = SerperService.get_images(f"{name} India map route tourist trail")
            data['route_map'] = map_images[0] if map_images else _get_fallback_image(f"{name} panorama")
            
            return data
        except Exception as e:
            print(f"Error generating itinerary: {e}")
            import traceback
            traceback.print_exc()
            return {"destination": name, "total_days": days, "days": [], "route_map": "", "error": str(e)}

    @staticmethod
    def get_gallery(name, count=20):
        """Fetch a gallery of images for a destination using Serper."""
        try:
            queries = [
                f"\"{name}\" India tourism landmarks travel photography",
                f"\"{name}\" India famous tourist attractions photography",
                f"\"{name}\" India scenic viewpoint travel photo",
                f"\"{name}\" India culture heritage travel image",
                f"\"{name}\" India destination gallery",
            ]
            all_images = []
            seen = set()
            for q in queries:
                images = SerperService.get_images(q)
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
                    f"\"{name}\" India lake mountain landscape",
                    f"\"{name}\" India temple fort architecture",
                    f"\"{name}\" India aerial destination photo",
                ]
                for q in booster_queries:
                    for img in SerperService.get_images(q):
                        if img not in seen:
                            seen.add(img)
                            all_images.append(img)
                        if len(all_images) >= max(4, count):
                            break
                    if len(all_images) >= max(4, count):
                        break

            # If no images from Serper, generate Unsplash fallbacks
            if not all_images:
                fallback_keywords = [name, f"{name} beach", f"{name} temple", f"{name} landscape",
                                     f"{name} architecture", f"{name} nature", f"{name} sunset",
                                     f"{name} mountain", f"{name} culture", f"{name} heritage"]
                all_images = [_get_fallback_image(kw) for kw in fallback_keywords[:count]]
            
            return {"destination": name, "images": all_images[:count]}
        except Exception as e:
            print(f"Error getting gallery: {e}")

    @staticmethod
    def _ensure_minimum_activities(plan, min_per_day=3):
        itinerary = plan.get('itinerary')
        if not isinstance(itinerary, list):
            return plan

        center = plan.get('center_coords') or {}
        base_lat = float(center.get('lat', 28.6139))
        base_lng = float(center.get('lng', 77.2090))

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
                    "image_query": f"{plan.get('destination', 'India')} travel destination",
                    "lat": base_lat + offset,
                    "lng": base_lng + offset,
                    "estimated_cost_inr": 400
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
  "tagline": "A catchy tagline for the trip",
  "duration": "Duration in days",
  "center_coords": {"lat": 28.6139, "lng": 77.2090},
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
          "image_query": "Specific visual search query for this activity (e.g. 'Golden Temple Amritsar morning view')",
          "lat": 28.6139,
          "lng": 77.2090,
          "estimated_cost_inr": 500
        }
      ]
    }
  ],
  "budget_summary": {
    "total_estimated_expenditure_inr": 25000,
    "accommodation_avg_per_day": 3000,
    "food_avg_per_day": 1500,
    "transport_avg_per_day": 1000,
    "activities_total": 5000
  },
  "travel_tips": ["Tip 1", "Tip 2", "Tip 3"]
}
Maintain a high-quality, professional, and inspiring tone.
Be specific to the prompt provided. If the user asks for a long trip (e.g. 15-30 days), ensure you provide activities for EVERY day, keeping the JSON well-formed and complete. Do NOT truncate or skip days. For long trips, keep activity descriptions concise to stay within token limits. 
Always include a "hero_image_query" field which is a specific search term to find a stunning background image for this trip (e.g. 'Santorini sunset caldera' or 'Kyoto cherry blossoms in spring').
Finally, add a "is_international" boolean field: true if the destination is outside India, false otherwise.
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
            
            # Enrich with real images and robust coordinates
            dest_name = plan.get('destination', 'India')
            
            # Fallback center coords if missing
            if not plan.get('center_coords'):
                plan['center_coords'] = {"lat": 28.6139, "lng": 77.2090}
            
            is_intl = plan.get('is_international', False)
            location_suffix = "" if is_intl else " India"
            
            for day in plan.get('itinerary', []):
                for act in day.get('activities', []):
                    # Fetch real image for the activity using AI generated query
                    query = act.get('image_query') or f"{act.get('name')} {dest_name}{location_suffix} tourist attraction"
                    
                    images = SerperService.get_images(query)
                    if images:
                        act['image_url'] = images[0]
                    else:
                        act['image_url'] = _get_fallback_image(f"{act.get('name', '')} {dest_name}")
                    
                    # Ensure coordinates are present
                    if 'lat' not in act or 'lng' not in act:
                        act['lat'] = plan.get('center_coords', {}).get('lat', 28.6139)
                        act['lng'] = plan.get('center_coords', {}).get('lng', 77.2090)

            plan = AIService._ensure_minimum_activities(plan, min_per_day=3)
            
            # Fetch hero image
            hero_query = plan.get('hero_image_query') or f"{dest_name} travel background"
            hero_images = SerperService.get_images(hero_query)
            if hero_images:
                plan['hero_image'] = hero_images[0]
            else:
                plan['hero_image'] = "https://images.unsplash.com/photo-1548013146-72479768bbaa?auto=format&fit=crop&q=80&w=2000"
            
            return plan
        except Exception as e:
            print(f"AI Plan error: {e}")
            return {"error": "Failed to generate plan"}

class WeatherService:
    @staticmethod
    def get_forecast(city, lat=None, lon=None):
        if not Config.WEATHER_API_KEY:
            print("[Weather] No API key configured")
            return None
            
        try:
            import datetime
            # Sanitize city name (remove state/region if present like "Ooty, Tamil Nadu")
            clean_city = city.split(',')[0].strip()
            
            # Use coordinates if available, otherwise fallback to city name
            if lat is not None and lon is not None:
                current_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={Config.WEATHER_API_KEY}&units=metric"
                forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={Config.WEATHER_API_KEY}&units=metric&cnt=40"
                print(f"[Weather] Fetching weather for {clean_city} using coords ({lat}, {lon})")
            else:
                current_url = f"http://api.openweathermap.org/data/2.5/weather?q={clean_city},IN&appid={Config.WEATHER_API_KEY}&units=metric"
                forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={clean_city},IN&appid={Config.WEATHER_API_KEY}&units=metric&cnt=40"
                print(f"[Weather] Fetching weather for {clean_city} using city name")
                
            current_resp = requests.get(current_url, timeout=5)
            print(f"[Weather] Current weather status: {current_resp.status_code}")
            
            if current_resp.status_code != 200:
                print(f"[Weather] API error body: {current_resp.text[:200]}")
                return None
            
            current_data = current_resp.json()
            today = datetime.date.today()
            
            # --- 5-day forecast ---

            forecast_resp = requests.get(forecast_url, timeout=5)
            
            forecast_days = []
            
            # Add today from current weather
            forecast_days.append({
                "date": today.strftime("%Y-%m-%d"),
                "date_label": "Today",
                "day": {
                    "avgtemp_c": round(current_data["main"]["temp"], 1),
                    "mintemp_c": round(current_data["main"].get("temp_min", current_data["main"]["temp"]), 1),
                    "maxtemp_c": round(current_data["main"].get("temp_max", current_data["main"]["temp"]), 1),
                    "humidity": current_data["main"].get("humidity", 0),
                    "wind_kph": round(current_data.get("wind", {}).get("speed", 0) * 3.6, 1),
                    "condition": {
                        "text": current_data["weather"][0]["description"].title(),
                        "icon": f"https://openweathermap.org/img/wn/{current_data['weather'][0]['icon']}@2x.png",
                        "main": current_data["weather"][0]["main"]
                    }
                }
            })
            
            # Parse 5-day forecast (group by day, pick noon entry)
            if forecast_resp.status_code == 200:
                forecast_data = forecast_resp.json()
                day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                seen_dates = {today.strftime("%Y-%m-%d")}
                
                for item in forecast_data.get("list", []):
                    dt = datetime.datetime.fromtimestamp(item["dt"])
                    date_str = dt.strftime("%Y-%m-%d")
                    
                    if date_str in seen_dates:
                        continue
                    
                    # Pick the midday reading (closest to 12:00)
                    if dt.hour < 10 or dt.hour > 16:
                        continue
                    
                    seen_dates.add(date_str)
                    day_name = day_labels[dt.weekday()]
                    
                    forecast_days.append({
                        "date": date_str,
                        "date_label": day_name,
                        "day": {
                            "avgtemp_c": round(item["main"]["temp"], 1),
                            "mintemp_c": round(item["main"].get("temp_min", item["main"]["temp"]), 1),
                            "maxtemp_c": round(item["main"].get("temp_max", item["main"]["temp"]), 1),
                            "humidity": item["main"].get("humidity", 0),
                            "wind_kph": round(item.get("wind", {}).get("speed", 0) * 3.6, 1),
                            "condition": {
                                "text": item["weather"][0]["description"].title(),
                                "icon": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                                "main": item["weather"][0]["main"]
                            }
                        }
                    })
                    
                    if len(forecast_days) >= 5:
                        break
            
            print(f"[Weather] Success: {len(forecast_days)} day(s) of forecast for {clean_city}")
            
            return {
                "forecast": {
                    "forecastday": forecast_days
                }
            }
            
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
