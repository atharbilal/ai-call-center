"""
FastAPI main server for AI Call Center.
"""

import os
from fastapi import FastAPI, WebSocket, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import modules from parent directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from telephony.twilio_handler import (
    generate_incoming_call_twiml,
    generate_error_twiml,
    handle_call_websocket,
    active_calls,
)
from core.agent import call_agent
from core.state import get_initial_state

load_dotenv()

NGROK_URL = os.getenv("NGROK_URL", "http://localhost:8000")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

app = FastAPI(
    title="AI Call Center",
    description="Multilingual AI-powered customer care system",
    version="1.0.0"
)

# CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# TWILIO ENDPOINTS
# ─────────────────────────────────────────

@app.post("/incoming-call")
async def incoming_call(request: Request):
    """
    Twilio calls this endpoint when someone calls our phone number.
    We respond with TwiML that tells Twilio to open a WebSocket stream.
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid", "UNKNOWN")
        caller = form_data.get("From", "Unknown")
        
        print(f"\n{'='*50}")
        print(f"Incoming call from {caller}")
        print(f"Call SID: {call_sid}")
        print(f"{'='*50}\n")
        
        # Build WebSocket URL (WSS for production, WS for local)
        ws_url = NGROK_URL.replace("https://", "wss://").replace("http://", "ws://")
        
        twiml = generate_incoming_call_twiml(ws_url, call_sid)
        
        return HTMLResponse(content=twiml, media_type="application/xml")
        
    except Exception as e:
        print(f"Error handling incoming call: {e}")
        return HTMLResponse(content=generate_error_twiml(), media_type="application/xml")

@app.websocket("/ws/call/{call_sid}")
async def websocket_call_handler(websocket: WebSocket, call_sid: str):
    """WebSocket endpoint for real-time audio streaming with Twilio."""
    await handle_call_websocket(websocket, call_sid)

# ─────────────────────────────────────────
# TESTING ENDPOINT (no phone needed)
# ─────────────────────────────────────────

@app.post("/test-agent")
async def test_agent(request: Request):
    """
    Test AI agent with text input — no phone required.
    Use this to test the agent during development.
    
    Request body: {"message": "my number is 9876543210", "call_sid": "TEST001", "language": "english"}
    """
    body = await request.json()
    message = body.get("message", "")
    call_sid = body.get("call_sid", "TEST001")
    
    # Get or create call state
    if call_sid not in active_calls:
        state = get_initial_state(call_sid)
        # For new calls, only run greeting node
        from core.agent import greeting_node
        state = greeting_node(state)
        active_calls[call_sid] = state
        
        # Only process as customer input if there's actually a message
        if message:
            state["raw_customer_input"] = message
            state["transcript"].append({"role": "user", "content": message})
            
            from telephony.twilio_handler import process_customer_input
            state = await process_customer_input(state, call_sid)
            active_calls[call_sid] = state
        
        return JSONResponse({
            "call_sid": call_sid,
            "stage": state["call_stage"].value,
            "ai_response": state["messages"][-1]["content"] if state["messages"] else "",
            "language": state["language"],
        })
    
    # Existing call — process customer message
    state = active_calls[call_sid]
    state["raw_customer_input"] = message
    state["transcript"].append({"role": "user", "content": message})
    
    from telephony.twilio_handler import process_customer_input
    state = await process_customer_input(state, call_sid)
    active_calls[call_sid] = state
    
    last_response = state["messages"][-1]["content"] if state["messages"] else ""
    
    return JSONResponse({
        "call_sid": call_sid,
        "stage": state["call_stage"].value,
        "customer_input": message,
        "ai_response": last_response,
        "language": state["language"],
        "customer_identified": state["customer_identified"],
        "customer_name": state.get("customer_data", {}).get("name") if state.get("customer_data") else None,
    })

@app.delete("/test-agent/{call_sid}")
async def end_test_call(call_sid: str):
    """End a test call session."""
    if call_sid in active_calls:
        del active_calls[call_sid]
    return JSONResponse({"status": "ended", "call_sid": call_sid})

# ─────────────────────────────────────────
# MONITORING ENDPOINTS
# ─────────────────────────────────────────

@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "ok",
        "active_calls": len(active_calls),
        "version": "1.0.0"
    })

@app.get("/calls")
async def list_active_calls():
    """List all active calls with their current state."""
    calls = []
    for sid, state in active_calls.items():
        calls.append({
            "call_sid": sid,
            "stage": state["call_stage"].value,
            "language": state["language"],
            "customer_identified": state["customer_identified"],
            "customer_name": state.get("customer_data", {}).get("name") if state.get("customer_data") else None,
        })
    return JSONResponse({"active_calls": calls, "count": len(calls)})

@app.get("/transcripts")
async def list_transcripts():
    """List all saved call transcripts."""
    from pathlib import Path
    import json
    
    logs_dir = Path("./call_logs")
    if not logs_dir.exists():
        return JSONResponse({"transcripts": [], "count": 0})
    
    transcripts = []
    for file in sorted(logs_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
        with open(file) as f:
            data = json.load(f)
            transcripts.append({
                "call_sid": data.get("call_sid"),
                "language": data.get("language"),
                "customer_name": data.get("customer_name"),
                "resolved": data.get("issue_resolved"),
                "turns": len(data.get("transcript", [])),
            })
    
    return JSONResponse({"transcripts": transcripts, "count": len(transcripts)})
