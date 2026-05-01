# RoutheonSkups AI Travel Platform

An advanced, AI-powered travel planning and exploration platform that leverages Large Language Models (LLMs) to create personalized, cinematic itineraries and provides immersive destination insights.

## 🚀 Features

### 1. Smart Trip Planner
- **Generative Itineraries**: Create multi-day travel plans using Llama 3 (via Groq) tailored to your preferences (adventure, luxury, heritage, etc.).
- **Route Optimization**: Uses Dijkstra-style algorithms and Nearest Neighbor logic to optimize travel paths between attractions.
- **Dynamic Pricing**: Real-time estimation of activity and stay costs.
- **Interactive Maps**: Visualize your journey with Leaflet-based route maps.

### 2. Destination Explorer
- **State-wise Discovery**: Explore curated destinations across all Indian states.
- **4K Gallery**: High-resolution imagery for every landmark.
- **Interactive Lightbox**: Immersive photo viewing experience.
- **Category Filtering**: Filter by National Parks, Museums, Nature, etc.

### 3. AI Travel Assistant
- **Contextual Guidance**: Real-time chat assistance with destination-specific knowledge.
- **Suggestion Chips**: Quick-start queries for common travel questions.
- **Dynamic Image Integration**: Seamlessly fetches landmark photos during conversation.

### 4. Personal Dashboard
- **Profile Management**: Save your travel preferences and personal details.
- **Saved Trips**: Bookmark your favorite itineraries for later access.
- **Verified Status**: Earn badges as you explore more.

## 🛠️ Technology Stack

- **Backend**: Python (Flask)
- **Database**: SQLite (SQLAlchemy ORM)
- **AI Models**: Llama 3.3 (via Groq API)
- **Search**: Serper API (Google Search integration)
- **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS
- **Maps**: Leaflet.js
- **Auth**: Flask-Login, Flask-Bcrypt

## 🏁 Getting Started

1. **Environment Setup**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**:
   Create a `.env` file with your API keys:
   ```env
   GROQ_API_KEY=your_groq_key
   SERPER_API_KEY=your_serper_key
   SECRET_KEY=your_secret_key
   ```

3. **Initialize Database**:
   ```bash
   python migrate_db.py
   ```

4. **Run Application**:
   ```bash
   python run.py
   ```
---
© 2026 RoutheonSkups AI. Designed for the future of travel.
