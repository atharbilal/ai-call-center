"""
Twilio Voice WebSocket handler.
Handles real-time bidirectional audio streaming between Twilio and our AI agent.

Flow:
1. Customer calls Twilio number
2. Twilio sends webhook to /incoming-call
3. We respond with TwiML telling Twilio to open a WebSocket stream
4. Twilio streams audio chunks to /ws/call/{call_sid}
5. We process audio → STT → Agent → TTS → send audio back
"""

import os
import json
import base64
import asyncio
from typing import Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream

from core.agent import call_agent
from core.state import get_initial_state, CallState, CallStage
from speech.stt import UniversalSTT
from speech.tts import UniversalTTS

# Active call sessions: call_sid → CallState
active_calls: Dict[str, CallState] = {}

stt = UniversalSTT()
tts = UniversalTTS()

def generate_incoming_call_twiml(websocket_url: str, call_sid: str) -> str:
    """
    Generate TwiML response for incoming call.
    This tells Twilio to connect the call to our WebSocket for audio streaming.
    
    Args:
        websocket_url: Full WSS URL of our WebSocket endpoint
        call_sid: Twilio call SID
    
    Returns:
        TwiML XML string
    """
    response = VoiceResponse()
    
    # Small pause to let connection establish
    response.pause(length=1)
    
    # Connect to our media stream
    connect = Connect()
    stream = Stream(url=f"{websocket_url}/ws/call/{call_sid}")
    connect.append(stream)
    response.append(connect)
    
    return str(response)

def generate_error_twiml() -> str:
    """TwiML for when something goes wrong."""
    response = VoiceResponse()
    response.say(
        "We're sorry, our systems are temporarily unavailable. Please try again in a few minutes.",
        voice="Polly.Aditi",  # Indian English voice
        language="en-IN"
    )
    return str(response)

async def handle_call_websocket(websocket: WebSocket, call_sid: str):
    """
    Main WebSocket handler for a live call.
    
    Twilio sends JSON messages over WebSocket with these events:
    - connected: WebSocket opened
    - start: Stream started, contains metadata
    - media: Audio chunk (base64-encoded mulaw audio)
    - stop: Call ended
    """
    await websocket.accept()
    
    # Initialize state for this call
    state = get_initial_state(call_sid)
    active_calls[call_sid] = state
    
    # Audio buffer — accumulate chunks before processing
    audio_buffer = bytearray()
    buffer_duration_ms = 0
    PROCESS_EVERY_MS = 800  # Process audio every 800ms
    
    print(f"[{call_sid}] Call connected. Starting AI agent.")
    
    try:
        # Send greeting immediately
        state = call_agent.invoke(state)
        greeting_text = state["messages"][-1]["content"] if state["messages"] else ""
        
        if greeting_text:
            audio_bytes = await tts.synthesize(greeting_text, state["language"])
            await send_audio_to_twilio(websocket, audio_bytes, call_sid)
        
        # Listen for audio from customer
        async for message in websocket.iter_text():
            try:
                data = json.loads(message)
                event = data.get("event", "")
                
                if event == "media":
                    # Decode incoming audio chunk (Twilio sends mulaw 8kHz audio)
                    payload = data.get("media", {}).get("payload", "")
                    chunk = base64.b64decode(payload)
                    audio_buffer.extend(chunk)
                    buffer_duration_ms += 100  # each chunk ≈ 100ms
                    
                    # Process accumulated audio every PROCESS_EVERY_MS
                    if buffer_duration_ms >= PROCESS_EVERY_MS:
                        audio_chunk = bytes(audio_buffer)
                        audio_buffer.clear()
                        buffer_duration_ms = 0
                        
                        # Transcribe audio to text
                        transcript_text = await stt.transcribe_audio_bytes(
                            audio_chunk, 
                            language=state.get("language", "english")
                        )
                        
                        if transcript_text and len(transcript_text) > 2:
                            print(f"[{call_sid}] Customer said: {transcript_text}")
                            
                            # Update state with customer input
                            state["raw_customer_input"] = transcript_text
                            state["transcript"].append({
                                "role": "user",
                                "content": transcript_text,
                                "stage": state["call_stage"].value
                            })
                            
                            # Run through appropriate agent node
                            state = await process_customer_input(state, call_sid)
                            
                            # Send AI response back as audio
                            if state["messages"] and state["messages"][-1]["role"] == "assistant":
                                response_text = state["messages"][-1]["content"]
                                print(f"[{call_sid}] AI says: {response_text}")
                                
                                audio_bytes = await tts.synthesize(
                                    response_text, 
                                    state.get("language", "english")
                                )
                                await send_audio_to_twilio(websocket, audio_bytes, call_sid)
                            
                            # Check if call ended
                            if state.get("call_ended"):
                                break
                
                elif event == "stop":
                    print(f"[{call_sid}] Call ended by Twilio.")
                    break
                    
            except json.JSONDecodeError:
                continue
                
    except WebSocketDisconnect:
        print(f"[{call_sid}] WebSocket disconnected.")
    except Exception as e:
        print(f"[{call_sid}] Error in call handler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if call_sid in active_calls:
            active_calls[call_sid]["call_ended"] = True
            print(f"[{call_sid}] Call session closed. Saving transcript.")
            save_transcript(call_sid, active_calls[call_sid])
            del active_calls[call_sid]

async def process_customer_input(state: CallState, call_sid: str) -> CallState:
    """
    Route customer input to the correct agent node based on current call stage.
    """
    stage = state.get("call_stage", CallStage.GREETING)
    
    if stage == CallStage.LANGUAGE_DETECTION:
        # Run language detection then identification
        from core.agent import language_detection_node, customer_identification_node
        state = language_detection_node(state)
        
    elif stage == CallStage.CUSTOMER_IDENTIFICATION:
        from core.agent import customer_identification_node
        state = customer_identification_node(state)
        
    elif stage in [CallStage.ISSUE_UNDERSTANDING, CallStage.RESOLUTION]:
        from core.agent import issue_resolution_node
        state = issue_resolution_node(state)
        
    elif stage == CallStage.ESCALATION:
        from core.agent import escalation_node
        state = escalation_node(state)
    
    return state

async def send_audio_to_twilio(websocket: WebSocket, audio_bytes: bytes, call_sid: str):
    """
    Send TTS audio back to Twilio over WebSocket.
    Twilio expects base64-encoded mulaw 8kHz audio.
    """
    try:
        # Encode audio to base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        message = {
            "event": "media",
            "streamSid": call_sid,
            "media": {
                "payload": audio_b64
            }
        }
        
        await websocket.send_text(json.dumps(message))
        
    except Exception as e:
        print(f"Error sending audio to Twilio: {e}")

def save_transcript(call_sid: str, state: CallState):
    """Save call transcript to a JSON file for review."""
    import json
    from pathlib import Path
    
    logs_dir = Path("./call_logs")
    logs_dir.mkdir(exist_ok=True)
    
    log_data = {
        "call_sid": call_sid,
        "language": state.get("language", "unknown"),
        "customer_id": state.get("customer_id"),
        "customer_name": state.get("customer_data", {}).get("name") if state.get("customer_data") else None,
        "issue_resolved": state.get("issue_resolved", False),
        "needs_human": state.get("needs_human", False),
        "transcript": state.get("transcript", []),
    }
    
    with open(logs_dir / f"{call_sid}.json", "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    print(f"Transcript saved to call_logs/{call_sid}.json")
