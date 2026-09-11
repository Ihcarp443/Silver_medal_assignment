# AI Farmer Assistant — Project Documentation
[Watch the video](https://raw.githubusercontent.com/Ihcarp443/Silver_medal_assignment/main/agri_with_voice.mp4)

[![Demo Video](https://raw.githubusercontent.com/Ihcarp443/Silver_medal_assignment/main/Screenshot%202026-09-10%20141202.png)](https://raw.githubusercontent.com/Ihcarp443/Silver_medal_assignment/main/agri_with_voice.mp4)

## Problem Statement
 
Farmers in India face three recurring, disconnected challenges: identifying crop diseases early enough to act, navigating a fragmented landscape of government schemes and subsidies they may be eligible for, and getting timely resolution when a payment or application issue occurs — all while language and digital literacy remain real barriers for many users. Existing tools typically solve only one of these problems in isolation (a disease-ID app, a scheme-lookup portal, a grievance helpline), forcing farmers to juggle multiple disconnected channels.
 
This project builds a single conversational assistant — accessible via both a web interface and WhatsApp — that unifies crop disease diagnosis, scheme/subsidy guidance, weather-aware advice, and grievance tracking into one multilingual (English/Hindi) chat experience.
 
## Objective
 
To design and build an AI-driven assistant that can:
- Diagnose crop diseases from a photo and provide actionable treatment guidance
- Answer questions about government farming schemes and subsidies using a curated knowledge base
- Incorporate real-time weather context into agronomic advice (e.g. spray/irrigation timing)
- Detect and formally track grievances (e.g. delayed subsidy payments) through a structured, multi-step intake flow
- Operate seamlessly across Website and WhatsApp, in the user's preferred language, with support for text, voice, and image input
## Key Features
 
- **Multilingual conversational interface** (English/Hindi) with speech-to-text and text-to-speech support for voice-based interaction
- **Crop disease detection from photos** — a CNN (transfer learning, EfficientNet backbone) trained on the PlantVillage dataset, covering major crops and diseases relevant to Indian farming
- **Retrieval-augmented answers** from two purpose-built knowledge bases: crop disease treatment/prevention, and government scheme eligibility/benefits
- **Weather-aware recommendations** — live forecast data factored into spray/irrigation guidance, with automatic city-to-coordinate resolution
- **Web search fallback** for information not covered by the internal knowledge bases (e.g. recently announced schemes)
- **Grievance intake and tracking** — a structured, multi-turn flow that collects required details (application ID, contact info), validates them, and returns a status/ticket, rather than a generic complaint form
- **Persistent conversational memory** — the assistant remembers user context (location, land size, soil type, crops grown) across sessions for increasingly personalized guidance
- **Feedback loop** — users can rate responses and request regeneration with a stated reason, feeding into response quality improvement
- **Dual-channel delivery** — the same backend and conversational logic serves both a web chat interface and WhatsApp (via Twilio), including image and voice input on both channels
- **Conversation history and threading** — users can revisit and continue past conversations

![Architecture](https://raw.githubusercontent.com/Ihcarp443/Silver_medal_assignment/main/Architecture%20(2).png)

## Architecture Approach
 
The system is built around a single LLM-driven agent that dynamically decides — via tool selection — whether to retrieve disease information, retrieve scheme information, check the weather, search the web, or escalate to a structured grievance flow. This avoids the rigidity of a fixed, hand-coded intent classifier and lets the assistant naturally handle queries that span multiple domains in one request (e.g. "how do I treat this and is there a subsidy for the fungicide?"). Image-based disease detection runs as a separate preprocessing step ahead of the conversational flow, keeping the CNN inference cleanly decoupled from the language/reasoning pipeline. Grievance handling is implemented as a stateful, interruptible sub-flow, since collecting structured information across multiple turns is a fundamentally different problem from single-shot question answering.
 
## Tools & Technologies
 
**Backend:** Python, FastAPI
 
**AI / Orchestration:** LangGraph (agent and conversation state management), LangChain (tool-calling agent framework), an LLM for reasoning and generation
 
**Machine Learning:** TensorFlow/Keras — transfer learning (EfficientNet) for crop disease classification, trained on the PlantVillage dataset
 
**Retrieval / Knowledge Base:** ChromaDB (vector database) with two dedicated collections — crop disease knowledge and government scheme knowledge — using multilingual sentence embeddings for retrieval
 
**Speech:** Sarvam AI — speech-to-text and text-to-speech for multilingual voice interaction
 
**External Data:** Open-Meteo (weather forecast and geocoding, free and key-less), DuckDuckGo Search (web search fallback)
 
**Messaging:** Twilio WhatsApp API for WhatsApp channel integration
 
**Persistence:** SQLite (conversation state checkpointing, chat thread history, user memory)
 
**Frontend:** Next.js / React
 
**Observability:** Langfuse (tracing and debugging of the agent's tool-calling behavior)


## Flow Chart

![Flow_chart](https://raw.githubusercontent.com/Ihcarp443/Silver_medal_assignment/main/Flow-chart-1.png)


## Repository

```
git clone https://github.com/Ihcarp443/Silver_medal_assignment.git
```

---

# Project Structure

```text
scheme-bot/
│
├── frontend/my_app          # Next.js Frontend
├── backend_main/main         # FastAPI Backend
├── README.md
└── ...
```

---

# Prerequisites

Before setting up the project, ensure you have the following installed:

* Python 3.10 or above
* Node.js (v18 or above recommended)
* npm
* Git

---

# Project Setup

## Step 1: Create a Virtual Environment

From the project root directory:

### Windows

```bash
python -m venv venv
```

### Linux / macOS

```bash
python3 -m venv venv
```

---

## Step 2: Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Step 3: Install Backend Dependencies

Navigate to the backend folder.

```bash
cd backend_main
```

Install the required Python packages.

```bash
pip install -r requirements.txt
```

---

## Step 4: Install Frontend Dependencies

Navigate to the frontend folder.

```bash
cd ..frontend/my-app
```

Install all Node.js dependencies.

```bash
npm install
```

---

## Step 5: Configure Environment Variables

### Backend

Inside the **backend_main** folder, create a file named:

```text
.env
```

Add the required backend environment variables.

Example:

```env
HF_TOKEN=

SARVAM_API_KEY=

```

---

### Frontend

Inside the **frontend/my-app** folder, create a file named:

```text
.env
```

Add the required frontend environment variables.

Example:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> Replace the values above with the appropriate environment variables for your setup.

---

## Step 6: Configure Database Files


Inside the **backend_main** directory, inside data folder :

```text
backend/
└── data/
```

Copy the **Scheme_DB folder provided separately** into this folder.

The final structure should look like:

```text
backend/
│
├── data/
│   ├── chroma_db
│   └── schemes
|   |___agri_kb.json
|    
| 
│
├── main.py
├── requirements.txt
└── ...
```

> **Note:** The required database folder is not included in the repository and must be copied manually before running the backend.

---

# Running the Application

## Start the Backend

Open a terminal.

```bash
cd backend
```

Activate the virtual environment if it is not already active.

Windows:

```bash
..\venv\Scripts\activate
```

Linux/macOS:

```bash
source ../venv/bin/activate
```

Run the FastAPI server.

```bash
uvicorn main:app
```

The backend will be available at:

```
http://localhost:8000
```

Swagger documentation(To check all the available APIs):

```
http://localhost:8000/docs (Directly paste this URL in your browser)
```

---

## Start the Frontend

Open another terminal.

```bash
cd frontend/my-app
```

Run:

```bash
npm run dev
```

The frontend will be available at:

```
http://localhost:3000
```

---

# Common Commands

### Install new Python packages

```bash
pip install <package_name>
pip freeze > requirements.txt
```

### Install new frontend packages

```bash
npm install <package_name>
```

---

# Notes

* Ensure all required environment variables are configured before starting the application.
* Ensure the required database files are copied into the `backend/DB` folder before running the backend.

---
