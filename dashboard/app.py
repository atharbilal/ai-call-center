"""
Streamlit dashboard for monitoring AI Call Center.
Shows active calls, past transcripts, call stats.
Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import httpx
import json
from pathlib import Path
from datetime import datetime

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="AI Call Center Dashboard",
    page_icon="📞",
    layout="wide"
)

st.title("📞 AI Call Center — Live Dashboard")

# ─── Sidebar ───────────────────────────────
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Live Monitor", "Test Agent", "Call Transcripts", "Knowledge Base"])

# ─── Live Monitor ──────────────────────────
if page == "Live Monitor":
    st.header("Live Calls")
    
    col1, col2, col3 = st.columns(3)
    
    try:
        resp = httpx.get(f"{API_BASE}/health", timeout=3)
        health = resp.json()
        
        with col1:
            st.metric("Active Calls", health.get("active_calls", 0))
        with col2:
            st.metric("Server Status", "Online" if resp.status_code == 200 else "Offline")
        with col3:
            st.metric("Version", health.get("version", "N/A"))
        
        calls_resp = httpx.get(f"{API_BASE}/calls", timeout=3)
        calls = calls_resp.json().get("active_calls", [])
        
        if calls:
            for call in calls:
                with st.expander(f"📱 {call['call_sid']} — {call['stage'].upper()}"):
                    st.write(f"Language: {call['language']}")
                    st.write(f"Customer identified: {call['customer_identified']}")
                    if call.get('customer_name'):
                        st.write(f"Customer: {call['customer_name']}")
        else:
            st.info("No active calls right now.")
            
    except Exception as e:
        st.error(f"Cannot connect to server at {API_BASE}. Make sure it is running.")
    
    if st.button("Refresh"):
        st.rerun()

# ─── Test Agent ────────────────────────────
elif page == "Test Agent":
    st.header("Test AI Agent (No Phone Required)")
    st.info("Use this to test the full conversation flow without making a real phone call.")
    
    if "test_call_sid" not in st.session_state:
        st.session_state.test_call_sid = "TEST_" + datetime.now().strftime("%H%M%S")
        st.session_state.test_history = []
        st.session_state.test_started = False
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"Session ID: `{st.session_state.test_call_sid}`")
    with col2:
        if st.button("New Session"):
            st.session_state.test_call_sid = "TEST_" + datetime.now().strftime("%H%M%S")
            st.session_state.test_history = []
            st.session_state.test_started = False
            st.rerun()
    
    # Start call
    if not st.session_state.test_started:
        if st.button("📞 Start Call"):
            try:
                resp = httpx.post(
                    f"{API_BASE}/test-agent",
                    json={"message": "", "call_sid": st.session_state.test_call_sid},
                    timeout=15
                )
                data = resp.json()
                st.session_state.test_history.append({
                    "role": "assistant",
                    "content": data["ai_response"],
                    "stage": data["stage"]
                })
                st.session_state.test_started = True
                st.rerun()
            except Exception as e:
                st.error(f"Error starting call: {e}")
    
    # Show conversation
    for msg in st.session_state.test_history:
        if msg["role"] == "assistant":
            st.chat_message("assistant").write(f"🤖 {msg['content']}")
        else:
            st.chat_message("user").write(f"👤 {msg['content']}")
    
    # Input
    if st.session_state.test_started:
        user_input = st.chat_input("Type what the customer says...")
        if user_input:
            st.session_state.test_history.append({"role": "user", "content": user_input})
            try:
                resp = httpx.post(
                    f"{API_BASE}/test-agent",
                    json={"message": user_input, "call_sid": st.session_state.test_call_sid},
                    timeout=15
                )
                data = resp.json()
                st.session_state.test_history.append({
                    "role": "assistant",
                    "content": data["ai_response"],
                    "stage": data["stage"]
                })
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ─── Call Transcripts ──────────────────────
elif page == "Call Transcripts":
    st.header("Past Call Transcripts")
    
    logs_dir = Path("./call_logs")
    if not logs_dir.exists() or not list(logs_dir.glob("*.json")):
        st.info("No call transcripts yet. Make some test calls first.")
    else:
        files = sorted(logs_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        for file in files[:20]:
            with open(file) as f:
                data = json.load(f)
            
            resolved_icon = "✅" if data.get("issue_resolved") else ("🔴" if data.get("needs_human") else "🟡")
            
            with st.expander(f"{resolved_icon} {data.get('call_sid')} — {data.get('customer_name', 'Unknown')} — {data.get('language', '?')}"):
                for turn in data.get("transcript", []):
                    if turn["role"] == "assistant":
                        st.markdown(f"**🤖 AI:** {turn['content']}")
                    else:
                        st.markdown(f"**👤 Customer:** {turn['content']}")

# ─── Knowledge Base ────────────────────────
elif page == "Knowledge Base":
    st.header("Knowledge Base Management")
    
    st.subheader("Indexed Documents")
    docs_dir = Path("./sample_docs")
    if docs_dir.exists():
        for f in docs_dir.glob("*"):
            st.write(f"📄 {f.name} ({f.stat().st_size // 1024} KB)")
    
    st.subheader("Add New Document")
    uploaded = st.file_uploader("Upload a PDF or TXT policy document", type=["pdf", "txt"])
    if uploaded:
        save_path = docs_dir / uploaded.name
        with open(save_path, "wb") as f:
            f.write(uploaded.read())
        st.success(f"Saved {uploaded.name}. Now re-run ingestion.")
        if st.button("Re-run Knowledge Base Ingestion"):
            import subprocess
            result = subprocess.run(["python", "-m", "knowledge.ingest"], capture_output=True, text=True)
            st.code(result.stdout)
    
    st.subheader("Test Search")
    query = st.text_input("Search knowledge base")
    if query:
        try:
            from knowledge.retriever import knowledge_base_search
            result = knowledge_base_search.invoke({"query": query})
            st.write(result)
        except Exception as e:
            st.error(f"Search error: {e}. Make sure you've run ingestion first.")
