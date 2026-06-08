
<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white" alt="Flask 3.1"/>
  <img src="https://img.shields.io/badge/Groq_Llama_3.3-38B2AC?logo=groq&logoColor=white" alt="Groq Llama 3.3"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/>
  <img src="https://img.shields.io/badge/Google_OAuth-4285F4?logo=google&logoColor=white" alt="Google OAuth"/>
  <br/>
  <img src="https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white" alt="Tailwind CSS 4"/>
  <img src="https://img.shields.io/badge/Leaflet.js-199900?logo=leaflet&logoColor=white" alt="Leaflet.js"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/Dijkstra_TSP-FF6F00?logo=graphql&logoColor=white" alt="Dijkstra/TSP"/>
</div>

<h1 align="center">🧳 RoutheonSkups</h1>
<p align="center">
  <strong>AI-Powered Travel Planning &amp; Exploration Platform</strong>
  <br/>
  <em>Plan trips, explore destinations, optimise routes, get weather, chat with AI — all in one place</em>
</p>

---

## ✨ Features at a Glance

| Category | Features |
|---|---|
| **🤖 AI Trip Planner** | Generative itineraries via Groq (Llama 3.3), natural language prompts, daily inspiration prompts, multi-step wizard |
| **🗺️ Destination Explorer** | State/category filtered discovery, 4K image galleries, AI-generated stories with TTS narration, rich detail pages |
| **🧠 AI Travel Assistant** | "Skupheon" chatbot per destination, general travel chat with session history, image analysis (vision LLM), FAQ assistant |
| **📐 Route Optimization** | Dijkstra's algorithm (inter-city), Nearest Neighbor TSP (activity ordering), Haversine distance, Leaflet.js maps |
| **💰 Budget Tools** | Trip cost estimator with per-person/per-day breakdown, dynamic pricing |
| **🌤️ Live Weather** | 7-day forecast via OpenWeatherMap, integrated into trip views |
| **🔔 Smart Notifications** | Trip alerts (T-7/3/1/0), seasonal recommendations, AI suggestions, global pacing, email delivery |
| **📊 Personal Dashboard** | Trips library, calendar view, favorites, profile with image upload, settings |
| **🔐 Auth & Admin** | Email/password (bcrypt), Google OAuth, password reset, full admin panel with 10 management sections, AI assistant, CSV exports, data reset |
| **🎨 UI/UX** | Dark mode, glassmorphism, Tailwind CSS, Material icons, responsive design |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.10+
- API keys for Groq, Serper, OpenWeatherMap, and Google OAuth (optional)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd RoutheonSkups

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Create a .env file (see below) with your API keys

# Run the application
python app.py
```

Open **http://localhost:8000** in your browser.

### Environment Variables (`.env`)

```env
SECRET_KEY=your-secret-key
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
SERPER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WEATHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx

# Google OAuth (optional)
GOOGLE_CLIENT_ID=xxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxx

# Email (optional)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Gmail SMTP requires a valid Gmail App Password for MAIL_PASSWORD.
# If Gmail returns SMTPAuthenticationError 535, create a new App Password,
# update MAIL_PASSWORD, and restart the app.

# Admin
ADMIN_EMAIL=admin@example.com
```

### Scripts

| Command | Description |
|---|---|
| `python app.py` | Start development server (port 8000) |
| `python migrate_db.py` | Add missing columns to existing SQLite DB |
| `python migrate_admin.py` | Add `is_admin` column to user table |
| `python promote_admin.py <email>` | Promote a user to admin |
| `python promote_admin.py remove <email>` | Remove admin from a user |

---

## 🧠 AI Features

All AI features are powered by **Groq** via the Groq SDK. The API key is loaded from the `GROQ_API_KEY` environment variable. Groq provides extremely fast LLM inference using LPU technology.

### Models Used

| Model | Used For |
|---|---|
| `llama-3.3-70b-versatile` | Itinerary generation, destination details, attractions, chatbot (general & destination), admin AI, FAQ, stories, study guides, plan-from-prompt |
| `llama-3.2-11b-vision-preview` | Image analysis (upload travel photos for description & tips) |

### 🗺️ AI Trip Planner

Describe your trip in plain English — the AI generates a complete day-wise itinerary with:
- Activities with times, descriptions, and costs
- Real geo-coordinates for each activity
- Hero image + per-activity images (via Serper)
- Budget summary (accommodation, food, transport, activities)
- Travel tips

**Example prompt:** *"Plan a 5-day trip to Goa for a group of friends focusing on beaches and nightlife"*

### 🤖 Skupheon — AI Travel Assistant

A full-featured travel chatbot with:
- **Destination-specific** — knows local attractions, food, culture, timings, weather
- **General travel chat** — answers any travel question with session history
- **Image analysis** — upload a photo, AI describes it and gives travel tips
- **Chat history** — persistent sessions with search, rename, pin, delete
- **Markdown rendering** — formatted responses
- **Proactive tips** — AI suggests travel tips based on saved destinations

### 📝 AI Content Generation

| Feature | Description |
|---|---|
| **Destination Details** | Overview, highlights, best time, how to reach, local cuisine, nearby cities, travel guide |
| **Destination Stories** | Immersive 4-6 paragraph narratives with text-to-speech playback |
| **Attractions** | 6 curated attractions per destination with images, timings, entry fees, geo-coordinates |
| **Itineraries** | Multi-day plans with activities, weather notes, and route maps |
| **Explore Destinations** | Curated lists by state/category with AI-generated descriptions and icons |
| **Admin AI** | Platform metrics Q&A for admin users |

### 🌄 Smart Fallback System

When AI or external APIs are unavailable, the system gracefully degrades:
- **Fallback images** — curated Unsplash pool organized by category (beach, temple, mountain, desert, etc.)
- **Fallback itineraries** — minimum 3 activities per day with generated coordinates
- **Weather fallback** — graceful null response with `"available": false`
- **TTS fallback** — edge-tts → gTTS → error response

---

## 🗺️ Pages & Navigation

| Route | Page | Description |
|---|---|---|
| `/` | **Splash** | Brand animation → auto-redirects to second page |
| `/landing` | **Home** | Search bar, travel categories carousel, popular destinations, interactive India map |
| `/register` · `/login` | **Auth** | Email registration/login + Google OAuth |
| `/plan-trip` | **Trip Planner** | Multi-step wizard (destination → dates → styles → review) |
| `/ai-prompt` | **AI Planner** | Natural language prompt with daily inspiration suggestions |
| `/explore` | **Explorer** | Filter destinations by state, category, or search query |
| `/destination/<name>` | **Destination Detail** | Full info: overview, highlights, weather, gallery, map, story, chatbot |
| `/my-trips` | **My Trips** | Upcoming/past trips, saved destinations, explore feed |
| `/calendar` | **Calendar** | Visual timeline of all trips |
| `/favorites` | **Favorites** | Bookmarked favorite destinations |
| `/profile` | **Profile** | Personal info, preferences, profile image |
| `/profile-ai` | **AI Assistant** | Full chat interface with session management |
| `/settings` | **Settings** | Notification toggles, AI assistant settings |
| `/admin/dashboard` | **Admin Dashboard** | Platform overview, recent registrations, system health, Admin AI |
| `/admin/panel` | **Admin Panel** | Full admin panel with 10 sections: dashboard, users, trips, itineraries, saved, favorites, notifications, chat sessions, messages, activity |
| `/admin/users` | **Admin Users** | User list with per-user activity metrics, auth info, recent activity timestamps, CSV export |
| `/about` · `/contact` · `/faq` | **Static Pages** | Platform info, contact form, FAQ with AI assistant |

---

## 🏗️ Architecture

### Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask 3.1, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt, Flask-Mail |
| **AI** | Groq SDK (Llama 3.3-70B, Llama 3.2-11B Vision) |
| **Image Search** | Serper API (Google Image Search) |
| **Weather** | OpenWeatherMap API (current + 5-day forecast) |
| **Auth** | Flask-Login, bcrypt, Authlib (Google OAuth 2.0) |
| **Database** | SQLite via SQLAlchemy ORM |
| **Frontend** | HTML5, Tailwind CSS 4 (CDN), Vanilla JavaScript |
| **Icons** | Material Icons Round, Material Symbols Outlined |
| **Maps** | Leaflet.js |
| **TTS** | edge-tts (Microsoft Neural) with gTTS fallback |
| **Email** | SMTP (Gmail) via Flask-Mail |
| **Security** | Werkzeug ProxyFix, session hardening (HttpOnly, SameSite, Secure) |

### Data Flow

```
User Input (Browser)
      ↕
Flask Backend (routes.py)
      ↕
Services Layer (services.py)
  ├── AIService → Groq API (Llama 3.3)
  ├── SerperService → Google Image Search
  ├── WeatherService → OpenWeatherMap API
  └── GraphService → Dijkstra / TSP algorithms
      ↕
SQLite Database (models.py)
  ├── User, Trip, Destination, Itinerary
  ├── SavedDestination, FavoriteDestination
  ├── Notification, ChatSession, ChatMessage
  └── DestinationActivity
```

### Project Structure

```
RoutheonSkups/
├── app.py                    # Flask factory, extensions (bcrypt, login, oauth, mail)
├── config.py                 # Configuration from env vars
├── models.py                 # SQLAlchemy models (10 tables)
├── routes.py                 # All routes (web pages + REST API) — 2881 lines
├── services.py               # Business logic — AI, Graph, Weather, Serper — 1700 lines
├── graph_service.py          # Dijkstra's algorithm + Indian cities graph (50 nodes)
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project metadata
├── .env                      # Environment variables
├── database/
│   └── db.sqlite3            # SQLite database
├── static/
│   ├── img/                  # Logos, background images, map
│   ├── js/                   # JavaScript files
│   ├── popular destination/  # Hero images for destinations
│   └── uploads/              # User profile image uploads
├── templates/
│   ├── components/           # Navbar, reusable components
│   ├── firstpage.html        # Splash screen animation
│   ├── landing_page.html     # Main home page (687 lines)
│   ├── register.html, login.html, reset_token.html
│   ├── plan_trip_step[1-4].html  # Multi-step planner wizard
│   ├── aipromptplanatrip.html    # AI prompt planning
│   ├── explore.html              # Destination explorer
│   ├── destination.html          # Destination detail
│   ├── aichatbot.html            # Destination chatbot
│   ├── view_trip.html            # Saved trip view
│   ├── profile_page[1-5].html    # Profile, trips, calendar, settings, AI
│   ├── admin/
│   │   ├── inc_users.html, inc_trips.html, inc_itineraries.html
│   │   ├── inc_saved.html, inc_favorites.html, inc_notifications.html
│   │   ├── inc_chat_sessions.html, inc_chat_messages.html
│   │   └── inc_destination_activity.html, inc_destinations.html
│   ├── admin_dashboard.html, admin_panel.html, admin_users.html
│   ├── favorites.html, about.html, contact.html, faq.html
│   └── ... (35 templates total)
└── instance/                 # Flask instance folder
```

---

## 💾 Database Schema

**Database:** SQLite via SQLAlchemy ORM

| Table | Key Fields | Purpose |
|---|---|---|
| `user` | id, name, email, password, google_id, phone, city, image_url, preferences (JSON), is_admin | User accounts & profiles |
| `trip` | id, user_id (FK), destination, start_date, end_date, budget, interests, itinerary_text (JSON) | Saved trip plans |
| `destination` | id, name, category, season, age_group, description, location, weather_city | Curated destinations |
| `itinerary` | id, destination, start_date, duration_days, plan_json | Pre-generated plans |
| `saved_destination` | id, user_id (FK), name, description, tag, icon, image_url | User bookmarks |
| `favorite_destination` | id, user_id (FK), name, description, tag, icon, image_url | User favorites |
| `notification` | id, user_id (FK), message, type, is_read | Smart notifications |
| `chat_session` | id, user_id (FK), title | AI conversation groups |
| `chat_message` | id, session_id (FK), role (user/ai), content | Chat messages |
| `destination_activity` | id, user_id (FK), destination_name, action_type, extra_data (JSON) | User activity tracking |

### All tables include: `created_at`, `updated_at` (auto-managed)

---

## 🔌 API Endpoints

### Web Pages (14 routes)

| Route | Method | Description |
|---|---|---|
| `/` | GET | Splash screen |
| `/landing` | GET | Main home page |
| `/register`, `/login`, `/logout` | GET/POST | Authentication |
| `/auth/google`, `/auth/google/callback` | GET | Google OAuth |
| `/reset-password`, `/reset-password/<token>` | GET/POST | Password reset |
| `/plan-trip`, `/plan-trip-step[1-4]` | GET | Trip planner wizard |
| `/ai-prompt` | GET | AI prompt planner |
| `/explore` | GET | Destination explorer |
| `/destination/<name>` | GET | Destination detail |
| `/my-trips` | GET | User trips |
| `/profile`, `/profile-ai` | GET | Profile & AI assistant |
| `/calendar` | GET | Calendar view |
| `/favorites` | GET | Favorites |
| `/settings` | GET | Settings |
| `/admin/dashboard`, `/admin/panel`, `/admin/users` | GET | Admin panel (3 interfaces) |

### REST API (35+ endpoints)

| Endpoint | Method | Description |
|---|---|---|
| **Trip Planning** | | |
| `/api/ai-plan` | POST | Generate trip plan from natural language |
| `/api/trip-cost-estimate` | POST | Calculate budget breakdown |
| `/api/save-itinerary` | POST | Save completed trip |
| `/api/trip/<id>/update` | POST | Update trip details |
| `/api/trip/<id>/delete` | POST | Delete trip |
| `/api/trip/<id>/chat-sync` | POST | Sync trip chat |
| `/api/add-destination-to-calendar` | POST | Quick-add trip from destination |
| `/api/optimize-route` | POST | Optimize activity order (TSP) |
| **Destination Data** | | |
| `/api/explore-destinations` | GET | Filtered destinations list |
| `/api/destination-attractions` | GET | Attractions for destination |
| `/api/destination-itinerary` | GET | Multi-day itinerary |
| `/api/destination-gallery` | GET | Image gallery |
| `/api/destination-hero` | GET | Hero image |
| `/api/destination-weather` | GET | Live weather + forecast |
| `/api/get-destination-story` | GET | AI-generated narrative |
| `/api/get-story-voice` | GET | TTS audio (MP3) |
| **AI Chat** | | |
| `/api/destination-chat` | POST | Destination-specific chatbot |
| `/api/general-chat` | POST | General travel chat |
| `/api/faq-chat` | POST | FAQ assistant |
| `/api/chat/send` | POST | Send message (text + image) |
| `/api/chat/sessions` | GET | List sessions |
| `/api/chat/session/<id>` | GET/DELETE | Messages / delete session |
| `/api/chat/session/<id>/title` | PATCH | Rename session |
| `/api/chat/session/<id>/pin` | POST | Toggle pin |
| `/api/chat/sessions/clear` | POST | Clear all history |
| **Save/Favorite** | | |
| `/api/save-destination` | POST | Toggle save |
| `/api/unsave-destination` | POST | Remove saved |
| `/api/favorite-destination` | POST | Toggle favorite |
| `/api/check-saved`, `/api/check-favorite` | GET | Check status |
| **Notifications** | | |
| `/api/notifications` | GET | Get notifications |
| `/api/notifications/generate` | POST | Force generate |
| `/api/notifications/read-all` | POST | Mark all read |
| **Admin** | | |
| `/admin/panel` | GET | Full admin panel (10 sections) |
| `/admin/dashboard` | GET | Admin overview dashboard |
| `/admin/users` | GET | User management with metrics |
| `/admin/delete-user/<id>` | POST | Delete user + all related data |
| `/admin/update-user/<id>` | POST | Update user (name, email, phone, city) |
| `/admin/delete-trip/<id>` | POST | Delete trip |
| `/admin/add-destination` | POST | Add new destination |
| `/admin/delete-destination/<id>` | POST | Delete destination |
| `/admin/delete-itinerary/<id>` | POST | Delete itinerary |
| `/admin/delete-saved/<id>` | POST | Delete saved destination |
| `/admin/delete-favorite/<id>` | POST | Delete favorite |
| `/admin/delete-notification/<id>` | POST | Delete notification |
| `/admin/delete-chat-session/<id>` | POST | Delete chat session + messages |
| `/admin/delete-chat-message/<id>` | POST | Delete chat message |
| `/admin/delete-destination-activity/<id>` | POST | Delete activity entry |
| `/admin/generate-notifications` | POST | Generate notifications for all users |
| `/admin/ai-chat` | POST | Admin AI assistant (full platform data Q&A) |
| `/admin/users/export-csv` | GET | Export users CSV with activity metrics |
| `/admin/export/trips` | GET | Export trips CSV |
| `/admin/export/destinations` | GET | Export destinations CSV |
| `/admin/export/itineraries` | GET | Export itineraries CSV |
| `/admin/export/saved` | GET | Export saved destinations CSV |
| `/admin/export/favorites` | GET | Export favorites CSV |
| `/admin/export/notifications` | GET | Export notifications CSV |
| `/admin/export/chat-sessions` | GET | Export chat sessions CSV |
| `/admin/export/chat-messages` | GET | Export chat messages CSV |
| `/admin/export/destination-activity` | GET | Export destination activity CSV |
| `/admin/reset-data` | POST | Reset all platform data (destructive) |

---

## 🧮 Algorithms

### Dijkstra's Shortest Path

**Purpose:** Find minimum distance between two Indian cities.

**Implementation:** Priority queue (heapq), O((V+E) log V).

**Graph:** 50+ interconnected city nodes with road distances in km.

```python
# graph_service.py — 50-node graph connecting major Indian cities
graph = {
    "Delhi": {"Manali": 530, "Jaipur": 280, "Rishikesh": 240, "Agra": 230},
    "Mumbai": {"Goa": 590, "Jaipur": 1150, "Pune": 150},
    "Bangalore": {"Goa": 560, "Ooty": 270, "Mysore": 145, "Chennai": 345},
    # ... 46 more nodes
}
```

### Nearest Neighbor (TSP) + Haversine

**Purpose:** Optimize visiting order of daily activities to minimize travel distance.

**Algorithm:** Start at first activity, repeatedly visit the nearest unvisited one.

**Distance metric:** Haversine (great-circle) distance on Earth's surface.

```
a = sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2)
c = 2 · atan2(√a, √(1-a))
d = 6371 · c   (km)
```

**Used in:** `services.py:GraphService.optimize_route()` → `/api/optimize-route`

---

## 🔒 Security

- **Passwords** — hashed with bcrypt (never stored in plain text)
- **OAuth** — stale state parameters cleaned before each Google auth attempt to prevent `MismatchingStateError`
- **Session cookies** — HttpOnly, SameSite=Lax, Secure in production
- **ProxyFix** — correct URL generation behind reverse proxies (Render, Railway)
- **Proxy sanitization** — malicious proxy env vars (e.g., `127.0.0.1:9`) auto-removed
- **Admin guards** — `is_admin` check on every admin route
- **Ownership checks** — trip/user data verified before read/update/delete
- **User deletion** — disabled by policy (returns 403)
- **XSS prevention** — all contact form input HTML-escaped before email rendering
- **SQL injection** — mitigated via SQLAlchemy ORM and parameterized queries

---

## 🔔 Smart Notification Engine

Notifications are context-aware with pacing to avoid spam:

```
Trigger              │ Cooldown  │ Type
─────────────────────┼───────────┼────────
Trip starts today    │ 18h       │ trip
Trip in 1 day        │ 18h       │ trip
Trip in 3 days       │ 18h       │ trip
Trip in 7 days       │ 18h       │ trip
AI suggestion        │ 72h       │ info
Seasonal pick        │ 168h      │ info
System update        │ 720h      │ warning
Global limit         │ 3h        │ all types
```

Users can toggle: notifications, trip alerts, AI suggestions, system notifications, seasonal recommendations, and email notifications.

---

## 🛠️ Technical Details

### Key Implementation Notes

- **SQLite auto-schema patching** — `_apply_sqlite_schema_updates()` in `app.py` adds missing timestamp columns at startup for all 9 tables
- **Single admin enforcement** — `_enforce_single_admin()` demotes all admins except the configured `ADMIN_EMAIL`
- **Daily rotation** — inspiration prompts and popular destinations rotate daily based on IST date (stable throughout the day)
- **Smart fallback chain** — Serper API → curated Unsplash pool → hash-based image selection
- **Weather caching** — 15-minute TTL cache to reduce OpenWeatherMap API calls
- **Chat persistence** — every message saved to SQLite in real-time
- **Cascading deletes** — deleting a user removes all associated trips, saves, notifications, and chat sessions
- **Contact form** — dual email (admin notification + user acknowledgment) with inline logo attachment

### Rate Limiting & Safety

- Global notification pacing: max 1 notification batch per 3 hours
- Per-type cooldowns: trip alerts (18h), AI suggestions (72h), seasonal (168h), system (720h)
- Weather API: retries up to 2 times with exponential backoff
- Serper API: max 30 images per query, ranked scoring for quality
- Profile images: extension + MIME type validation, size through Werkzeug

---

## 📊 Admin System

Three admin interfaces are available for admin users:

### 1. Admin Dashboard (`/admin/dashboard`)
Quick platform overview with:
- **KPI Cards** — Total users, trips, destinations, saved places, itineraries, notifications, chat sessions, messages
- **Recent Registrations** — Last 5 users with join dates
- **System Health** — Database status, AI service status, user/admin counts, Google-only accounts, newest activity timestamps
- **Admin AI FAB** — Floating chatbot for quick data Q&A

### 2. Admin Panel (`/admin/panel`) — Full Management Console
Sidebar-navigated panel with **10 management sections**:

| Section | Features |
|---|---|
| **Dashboard** | KPI grid, recent users list, system health monitoring |
| **Users** | Search, filter by role (admin/user), batch delete, view details modal (all fields), delete, CSV export |
| **Trips** | Search, delete individual trips, CSV export |
| **Itineraries** | Search, delete itineraries, CSV export |
| **Saved** | Search, delete saved destinations, CSV export |
| **Favorites** | Search, delete favorites, CSV export |
| **Notifications** | Search, delete, generate notifications for all users, CSV export |
| **Chat Sessions** | Search, delete sessions (cascades messages), CSV export |
| **Chat Messages** | Search, delete messages, CSV export |
| **Destination Activity** | Search, delete activity entries, CSV export |

Each section includes: search, inline filtering, batch operations, detail modals (where applicable), and dedicated CSV export.

### 3. Admin Users (`/admin/users`)
Dedicated user table with per-user metrics:
- **Auth method** — Google vs Email, password status
- **Activity counts** — Trips, saved places, notifications, chat sessions
- **Recent activity timestamps** — Last trip, saved, and chat activity dates
- **CSV export** — Full user data with all metrics

### Admin AI Assistant
Embedded in both dashboard and panel. Has **full read access** to all platform data (users, trips, destinations, saved places, favorites, itineraries, notifications, chats, messages, activities). Answers natural language queries about platform metrics, user details, and data summaries.

### Admin API Endpoints (30+ routes)
Full CRUD operations on all data models plus:
- 8 dedicated CSV export endpoints (one per data type)
- Notification generation across all users
- Data reset (destructive)
- Admin AI chat with live platform snapshot injection

### Security
- `is_admin` guard on every admin route (server-side)
- Self-deletion prevention
- Cascading deletes maintain referential integrity

---

## 🌐 Deployment

### Recommended Platforms

| Platform | Notes |
|---|---|
| **Render** | Free tier, auto HTTPS, works with ProxyFix |
| **Railway** | Similar setup, easy env vars |
| **AWS EC2** | Full control, production-grade |
| **PythonAnywhere** | Quick deployment for demos |

### Production Checklist

- [ ] Set `SECRET_KEY` to a strong random value
- [ ] Enable `SESSION_COOKIE_SECURE=True`
- [ ] Configure `ADMIN_EMAIL` for admin access control
- [ ] Set up Google OAuth credentials for production domain
- [ ] Configure email credentials for password reset & notifications
- [ ] Consider migrating from SQLite to PostgreSQL for scale
- [ ] Set `PREFERRED_URL_SCHEME=https`

---

## 📄 License

MIT

---

<div align="center">
  <sub>Built with ❤️ for travellers everywhere</sub>
  <br/>
  <sub>© 2026 RoutheonSkups</sub>
</div>
