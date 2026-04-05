# AI Call Center

A production-ready, multilingual AI voice agent that handles customer calls automatically.
Supports English + 9 Indian languages. Integrates with any customer database.

## ✅ **LIVE DEMO**
**Deployed on Vercel**: https://ai-call-center-git-main-atharbilals-projects.vercel.app

### Test Endpoints:
- **Health Check**: https://ai-call-center-git-main-atharbilals-projects.vercel.app/health
- **API Docs**: https://ai-call-center-git-main-atharbilals-projects.vercel.app/docs
- **Test Agent**: https://ai-call-center-git-main-atharbilals-projects.vercel.app/test-agent

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
- **GROQ_API_KEY** — from console.groq.com (FREE, fast)
- **TWILIO_ACCOUNT_SID** — from console.twilio.com
- **TWILIO_AUTH_TOKEN** — from console.twilio.com
- **TWILIO_PHONE_NUMBER** — your Twilio phone number
- **LANGSMITH_API_KEY** — from smith.langchain.com (optional, for tracing)
- **OPENAI_API_KEY** — from platform.openai.com (for speech services)

## Architecture
Customer Call → Twilio → FastAPI → LangGraph Agent → LLM + Tools → TTS → Customer

## Adding a New Client (Swiggy, Flipkart, etc.)
1. Replace database/mock_db.py with real DB connection
2. Add their policy PDFs to sample_docs/
3. Re-run: python -m knowledge.ingest
4. Update prompts in core/prompts.py with company name
5. Point Twilio to your deployed server URL

## Deployment (Production)

### ✅ **Vercel (Recommended)**
- **URL**: https://ai-call-center-git-main-atharbilals-projects.vercel.app
- **Unlimited size** (no 4GB limits)
- **Free tier available**
- **Global CDN**
- **Automatic HTTPS**

**Setup**:
1. Push to GitHub
2. Connect to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy automatically

### Railway.app
- Limited to 4GB image size
- Free tier available
- Good for simple deployments

### AWS / Google Cloud
- Full control
- Scalable
- Requires more setup

## Environment Variables for Production
Set these in your hosting platform:
```bash
GROQ_API_KEY=your_groq_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
LANGSMITH_API_KEY=your_langsmith_key
OPENAI_API_KEY=your_openai_key
APP_HOST=0.0.0.0
APP_PORT=8000
CHROMA_DB_PATH=./chroma_db
```

## Twilio Configuration
1. Go to Twilio Console → Phone Numbers → Your Number
2. Set "Webhook URL" to: `https://your-domain.com/incoming-call`
3. Set "Method" to: HTTP POST
4. Accept media: audio/x-mulaw

## Current Status
- ✅ **Deployed on Vercel**
- ✅ **Core API working**
- ✅ **Health check functional**
- ✅ **Free API keys configured**
- ✅ **Ready for Twilio integration**

## Next Steps
- [ ] Configure Twilio webhook
- [ ] Make test calls
- [ ] Add client-specific knowledge base
- [ ] Set up monitoring
