# 🌍 Travel Assistant

An AI-powered travel planning assistant that provides intelligent recommendations, real-time weather information, and up-to-date travel insights through natural conversations.

![Demo](demo.mp4)

## Features

- **Smart Conversations**: Natural language travel planning with context memory
- **Weather Integration**: Real-time weather data for destinations worldwide  
- **Current Information**: Google Search integration for latest travel trends and updates
- **Multi-Platform**: Web interface and REST API
- **Docker Ready**: Easy deployment with containerization

## Quick Start

### Prerequisites
- Docker & Docker Compose
- API Keys: `GEMINI_API_KEY`, `OPENWEATHER_API_KEY`

### Running the Application

1. **Setup Environment**
   ```bash
   cd travel-assistant
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start Services**
   ```bash
   docker-compose up --build
   ```

3. **Access the App**
   - Web Interface: http://localhost:8501
   - API Endpoint: http://localhost:8000

### Example Usage

```bash
# Test the API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What should I pack for Tokyo in March?", "session_id": "test"}'
```

## Demo & Examples

- 🎬 **Preview GIF**: ![Demo](travel-assistant/demo.gif) - Preview of the assistant in action
- 📝 **Conversation Examples**: [transcripts.md](transcripts.md) - Real CLI interaction examples

## Architecture

Built with **LangChain** + **Google Gemini 2.5 Flash** + **FastAPI** + **Streamlit**

- **Backend**: FastAPI with LangChain agent framework
- **Frontend**: Streamlit web interface  
- **LLM**: Google Gemini 2.5 Flash with function calling
- **APIs**: OpenWeather API, Google Search grounding
- **Memory**: Conversation context preservation
- **Deployment**: Docker containerization

## Project Structure

```
travel-assistant/
├── backend/               # FastAPI + LangChain
│   ├── app/main.py       # API endpoints
│   ├── services/         # Agent & session management
│   ├── tools/            # Weather integration
│   └── prompts/          # Prompt engineering
├── frontend/app.py       # Streamlit interface
└── docker-compose.yml    # Container deployment
```

## Health Check

```bash
curl http://localhost:8000/health
# Returns: {"status":"healthy","framework":"LangChain","model":"gemini-2.5-flash"}
```
