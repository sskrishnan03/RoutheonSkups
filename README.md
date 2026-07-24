<p align="center">
  <img src="static/img/RoutheonSkups image.png" alt="RoutheonSkups" width="100%" />
</p>

<h1 align="center">RoutheonSkups</h1>

<p align="center">
  An intelligent travel planning platform that transforms the way you discover destinations, build itineraries, and experience the world.
</p>

<p align="center">
  <a href="#overview">Overview</a> &nbsp;&middot;&nbsp;
  <a href="#key-features">Features</a> &nbsp;&middot;&nbsp;
  <a href="#how-it-works">How It Works</a> &nbsp;&middot;&nbsp;
  <a href="#installation">Installation</a> &nbsp;&middot;&nbsp;
  <a href="#usage">Usage</a> &nbsp;&middot;&nbsp;
  <a href="#license">License</a>
</p>

<br/>

## Overview

RoutheonSkups is an AI-powered travel platform built to replace scattered planning across search engines, spreadsheets, and messaging threads with one unified experience. From discovering destinations to optimizing routes and generating full itineraries, everything happens inside a single, beautifully designed application.

The platform combines generative AI, real-time data, and intelligent algorithms to handle the heavy lifting of travel planning. You describe what you want in plain language, and the system produces a complete day-wise plan with activities, budgets, maps, weather, and travel guidance — all personalized to your preferences.

Whether you are planning a weekend getaway, a multi-week international trip, or simply exploring new places, RoutheonSkups gives you the tools to plan with confidence and travel with clarity.

<br/>

## Project Overview

RoutheonSkups is designed around one core idea: travel planning should feel effortless, not overwhelming. The platform takes you from inspiration to a fully structured trip plan in minutes, not hours.

The experience begins on the home page, where you can search for destinations, browse curated categories, and explore an interactive map. From there, you can dive into any destination to find AI-generated guides, photo galleries, weather forecasts, nearby attractions, and local recommendations.

When you are ready to plan, the platform offers two paths. You can walk through a guided multi-step wizard that collects your destination, dates, travel style, and group size, or you can simply describe your dream trip in a sentence and let the AI generate everything for you. Either way, you receive a detailed itinerary with timed activities, cost estimates, optimized routes, and a visual map of your entire journey.

Beyond planning, the platform includes a personal dashboard for managing all your trips, a favorites system for saving destinations you love, a calendar view for visualizing your travel timeline, and an AI travel assistant that can answer questions, provide recommendations, and help you refine your plans through natural conversation.

<br/>

## Key Features

**AI Trip Planning**

Describe your trip in natural language and receive a complete day-wise itinerary with activities, descriptions, timing, costs, and real geographic coordinates. The AI understands destinations, seasons, budgets, group sizes, and travel styles to produce plans that are both inspiring and practical.

**Destination Discovery**

Explore a rich catalog of destinations filtered by state, category, season, or search query. Each destination includes an AI-generated overview, curated highlights, best time to visit, how to reach there, local food recommendations, nearby cities, and a travel guide — all presented in an immersive, cinematic layout.

**Intelligent Route Optimization**

The platform uses Dijkstra's algorithm for inter-city routing and a Nearest Neighbor approach for daily activity ordering. These algorithms work together to minimize travel time and distance, ensuring your itinerary flows logically from one point to the next.

**AI Travel Assistant**

A full-featured conversational assistant named Skupheon is available on every destination page. Ask about local attractions, weather, food, culture, or any travel question. The assistant maintains session history, supports image analysis, and provides contextual recommendations based on your saved destinations.

**Live Weather Integration**

Every destination page and trip plan includes real-time weather data with a 7-day forecast. Temperature, humidity, wind, and conditions are displayed alongside your itinerary so you can pack and plan accordingly.

**Smart Notification System**

The platform generates context-aware notifications for upcoming trips, seasonal destination suggestions, and AI-powered recommendations. Notifications are paced intelligently to avoid spam and can be delivered both in-app and via email.

**Interactive Maps**

Leaflet.js-powered maps display destination markers, activity locations, optimized routes, and nearby points of interest. Every activity in your itinerary is pinned with real coordinates for seamless navigation.

**Trip Cost Estimation**

A built-in cost estimator breaks down your trip budget by accommodation, food, transport, and activities. Estimates adapt based on your travel style, group size, and destination.

**Personal Dashboard**

Manage all your trips from a central hub. View upcoming and past itineraries, access your calendar timeline, browse saved and favorite destinations, and keep track of your travel history.

**Gallery and Visual Content**

Every destination features an AI-curated photo gallery, a hero image, and a map view. Destination stories are generated as immersive narratives with text-to-speech playback for an audio-guided experience.

**Contact and Communication**

A fully integrated contact form sends styled HTML emails to both the administrator and the user with confirmation. Every submission is stored in the database for follow-up.

<br/>

## How It Works

**1. Discover and Explore**

Open the application and land on the home page. Browse travel categories, search for destinations by name or region, and explore the interactive map. Every destination you click opens a rich detail page with everything you need to know.

**2. Plan Your Trip**

Choose between two planning modes. The multi-step wizard walks you through destination selection, date picking, travel style, and group size before generating your plan. The AI prompt mode lets you describe your trip in a single sentence and receive a complete itinerary in seconds.

**3. Review and Optimize**

Your generated itinerary appears with a day-by-day breakdown of activities, timing, costs, and a map showing your route. Use the route optimization feature to reorder activities for minimal travel distance. Adjust the plan as needed.

**4. Save and Manage**

Save your completed trips to your personal dashboard. Access them anytime from the trips library or the calendar view. Bookmark destinations you want to visit later and add favorites to build your personal travel collection.

**5. Chat with the AI Assistant**

Open the travel assistant on any destination page or from your profile. Ask questions about local attractions, food, weather, culture, or logistics. Upload photos for AI-powered image analysis and travel tips.

**6. Stay Notified**

Receive smart notifications about your upcoming trips, new destination suggestions based on the season, and personalized AI recommendations. Configure which notifications you want and how they are delivered.

<br/>

## Installation

**Prerequisites**

- Python 3.10 or higher
- A Neon PostgreSQL database (free tier available at neon.tech)
- API keys for Groq and Serper
- Google OAuth credentials (optional, for Google Sign-In)
- Gmail SMTP credentials (optional, for email notifications)

**Setup**

```bash
git clone https://github.com/your-username/RoutheonSkups.git
cd RoutheonSkups

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Configuration**

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require
GROQ_API_KEY=your_groq_api_key
SERPER_API_KEY=your_serper_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
ADMIN_EMAIL=your_admin_email
MAIL_USERNAME=your_gmail
MAIL_PASSWORD=your_gmail_app_password
MAIL_DEFAULT_SENDER=your_gmail
```

**Initialize the Database**

```bash
python migrate_to_neon.py
```

**Start the Application**

```bash
python app.py
```

The application will be available at `http://localhost:8000`.

<br/>

## Usage

Once the application is running, you will land on the splash screen which transitions to the home page.

**Create an Account**

Register with your email and password or sign in with Google. This gives you access to the full platform — trip planning, saved destinations, notifications, and the AI assistant.

**Explore Destinations**

Navigate to the Explore page to browse destinations by state, category, or search. Click any destination to open its detail page with an overview, highlights, gallery, weather, attractions, map, and a dedicated AI chatbot.

**Plan a Trip**

Open the Trip Planner for a guided multi-step experience, or visit the AI Prompt page to describe your trip in natural language. Both paths produce a complete itinerary with activities, costs, maps, and weather notes.

**Manage Your Dashboard**

Visit My Trips to see all saved itineraries. Check the Calendar for a visual timeline. Browse Favorites and Saved Destinations for places you want to revisit.

**Use the AI Assistant**

Open the AI Chat from your profile to have a conversation about any travel topic. The assistant maintains session history and can help with planning, recommendations, and general travel questions.

**Configure Settings**

Visit Settings to manage notification preferences, toggle email delivery, and adjust your AI assistant configuration.

<br/>

## License

This project is provided for personal and educational use.

<br/>

<div align="center">
  <sub>RoutheonSkups</sub>
  <br/>
  <sub>&copy; 2026</sub>
</div>
