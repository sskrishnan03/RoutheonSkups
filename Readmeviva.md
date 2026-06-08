# 🧳 RoutheonSkups AI Travel Platform — Viva README

> A comprehensive guide covering architecture, algorithms, AI models, database design, and key concepts for your viva presentation.

---

## 📌 Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [AI Model](#3-ai-model)
4. [Route Optimization Algorithms](#4-route-optimization-algorithms)
5. [Dynamic Pricing System](#5-dynamic-pricing-system)
6. [Map System](#6-map-system)
7. [Search Integration](#7-search-integration)
8. [AI Travel Assistant (Chatbot)](#8-ai-travel-assistant-chatbot)
9. [Database Design](#9-database-design)
10. [Authentication System](#10-authentication-system)
11. [Server & Deployment](#11-server--deployment)
12. [Complete Workflow (End-to-End)](#12-complete-workflow-end-to-end)
13. [Limitations](#13-limitations)

---

## 1. Project Overview

**RoutheonSkups AI Travel Platform** is an intelligent, AI-powered travel system that:

- Generates **personalized itineraries** using Large Language Models (LLMs)
- Optimizes **travel routes** using graph algorithms
- Provides **real-time travel assistance** with dynamic data integration

---

## 2. System Architecture

The project follows a **3-Layer Architecture**:

### 🔹 Layer 1 — Frontend (User Interface)
- **Technologies:** HTML5 + Tailwind CSS + JavaScript
- **Displays:** Travel plans, maps, images, and chat UI

### 🔹 Layer 2 — Backend (Core Logic)
- **Technologies:** Python + Flask
- **Handles:** API calls, AI processing, route optimization, database operations

### 🔹 Layer 3 — Database Layer
- **Technologies:** SQLite + SQLAlchemy ORM
- **Stores:** Users, trips, and preferences

### 👉 Data Flow

```
User Input → Flask Backend → AI Model / Algorithms → Database → Frontend Output
```

---

## 3. AI Model

### Model Used
- **Groq API** with **Llama 3.3**

### What It Does
- Takes user inputs: destination, budget, and interests (adventure, luxury, etc.)
- Sends a structured prompt to the LLM
- LLM generates a **day-wise itinerary** with activities and travel suggestions

### Example Prompt (Internal)
```
"Create a 3-day travel itinerary for Goa for a budget traveler interested in beaches and nightlife"
```

### Example Output
```
Day 1: Beaches
Day 2: Water sports
Day 3: Nightlife
```

### Key Concepts
- **Generative AI (NLP-based)**
- Uses **prompt engineering** + **contextual generation**

---

## 4. Route Optimization Algorithms

The system uses **Graph Algorithms** to optimize travel routes.

### 🔹 Algorithm 1: Dijkstra's Algorithm

**Purpose:** Find the shortest path between locations.

**Concept:**
- Treat places as **nodes**
- Roads/distances as **edges (weights)**

**Formula:**

```
d(v) = min( d(v), d(u) + w(u, v) )
```

**How It Works:**
1. Start from the source node
2. Update shortest distances iteratively
3. Select the minimum cost path at each step

**Example:**
```
Hotel → Beach → Museum → Restaurant
(System finds the minimum distance route)
```

---

### 🔹 Algorithm 2: Nearest Neighbor Algorithm

**Purpose:** Visit the closest unvisited place first (Greedy TSP approach).

**Logic:**
1. Start at the current location
2. Visit the nearest unvisited place
3. Repeat until all places are covered

**Why Used?**
- Faster than solving the exact Travelling Salesman Problem (TSP)
- Suitable for real-time systems where speed matters

---

## 5. Dynamic Pricing System

### What It Does
Estimates costs for:
- Hotel stays
- Activities
- Travel/transport

### How It Works
- Uses predefined price ranges and available API data
- Applies budget filters based on user preferences

### Example Price Ranges

| Travel Style | Estimated Cost/Day |
|---|---|
| Luxury | ₹5,000+ |
| Budget | ₹1,500 |

---

## 6. Map System

### Library Used
- **Leaflet.js**

### Features
- Marker placement for destinations
- Route drawing between locations
- Interactive navigation

### How It Works
1. Coordinates are fetched for each location
2. Route is plotted dynamically using JavaScript

---

## 7. Search Integration

### API Used
- **Serper API**

### Purpose
Fetch real-time data including:
- Latest travel information
- Place details
- Images

### Example
```
Search: "Best places in Kerala"
→ Returns live, real-time results
```

---

## 8. AI Travel Assistant (Chatbot)

### Powered By
- **LLM (Llama 3)**

### Features
- Context-aware conversational responses
- Suggestion chips for quick actions
- Dynamic images based on context

### How It Works
1. User asks a question (e.g., *"Best time to visit Goa?"*)
2. Backend sends the query to the LLM with added context
3. LLM responds with smart, contextual travel advice

> 💡 Similar to **ChatGPT-style** conversational AI

---

## 9. Database Design

### Database: SQLite
### ORM: SQLAlchemy

### Tables

#### 1. Users
| Column | Type |
|---|---|
| id | Integer (PK) |
| username | String |
| email | String |
| password | String (hashed) |

#### 2. Trips
| Column | Type |
|---|---|
| trip_id | Integer (PK) |
| user_id | Integer (FK) |
| destination | String |
| itinerary | Text |
| budget | Float |

#### 3. Preferences
| Column | Type |
|---|---|
| user_id | Integer (FK) |
| interests | String |
| travel_style | String |

### Relationship
```
One User → Many Trips
```

---

## 10. Authentication System

### Libraries Used
- **Flask-Login** — Session management
- **Flask-Bcrypt** — Password hashing

### Functions
- User login and logout
- Secure session handling
- Password encryption (hashing with Bcrypt)

> 🔐 Passwords are never stored as plain text

---

## 11. Server & Deployment

### Web Server
- **Flask** (Python)

### How to Run
```bash
python run.py
```

### Key Flask Routes
| Route | Purpose |
|---|---|
| `/plan_trip` | Generate itinerary |
| `/chat` | AI assistant chatbot |
| `/dashboard` | User dashboard |

### Deployment Options
- AWS
- Render
- Railway

---

## 12. Complete Workflow (End-to-End)

```
1. User enters travel details (destination, budget, interests)
        ↓
2. Flask backend receives the request
        ↓
3. LLM generates a personalized itinerary
        ↓
4. Route optimization algorithm finds the best path
        ↓
5. Dynamic pricing calculates estimated costs
        ↓
6. Data is stored in the SQLite database
        ↓
7. Results are displayed on the frontend
        ↓
8. Map renders the complete journey visually
```

---

---
## 13. Homework:-
> 📝 **Tip for Viva:** Be ready to explain the difference between **Dijkstra's Algorithm** (shortest path) and the **Nearest Neighbor Algorithm** (greedy TSP), and why both are used together in this system.