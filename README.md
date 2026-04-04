# AI Call Center

A production-ready, multilingual AI voice agent that handles customer calls automatically.
Supports English + 9 Indian languages. Integrates with any customer database.

## Features
- Real-time voice conversations via Twilio
- Supports: English, Hindi, Tamil, Telugu, Bengali, Marathi, Kannada, Malayalam, Gujarati, Punjabi
- Customer identification by phone number or account ID
- Automatic database lookup
- RAG-powered knowledge base (upload any policy PDF)
- LangSmith observability and call tracing
- Live monitoring dashboard
- Human escalation when needed

## Quick Start

### 1. Install dependencies
pip install -r requirements.txt

### 2. Configure environment
cp .env.example .env
# Fill in API keys in .env

### 3. Ingest knowledge base
python -m knowledge.ingest

### 4. Start the server
uvicorn api.main:app --reload

### 5. Start the dashboard
streamlit run dashboard/app.py

### 6. Test without a phone
curl -X POST http://localhost:8000/test-agent \
  -H "Content-Type: application/json" \
  -d '{"message": "", "call_sid": "TEST1"}'

## API Keys Required
- ANTHROPIC_API_KEY — from console.anthropic.com
- DEEPGRAM_API_KEY — from console.deepgram.com  
- ELEVENLABS_API_KEY — from elevenlabs.io
- TWILIO credentials — from console.twilio.com
- LANGSMITH_API_KEY — from smith.langchain.com

## Architecture
Customer Call → Twilio → FastAPI → LangGraph Agent → LLM + Tools → TTS → Customer

## Adding a New Client (Swiggy, Flipkart, etc.)
1. Replace database/mock_db.py with real DB connection
2. Add their policy PDFs to sample_docs/
3. Re-run: python -m knowledge.ingest
4. Update prompts in core/prompts.py with company name
5. Point Twilio to your deployed server URL

## Deployment (Production)
Deploy the FastAPI server to:
- Railway.app (easiest, free tier available)
- AWS EC2 / DigitalOcean Droplet
- Google Cloud Run (serverless)

Make sure to set all .env variables as environment variables in production.
