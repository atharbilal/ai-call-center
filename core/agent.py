"""
LangGraph AI Agent — brain of the call center.
Implements a state machine: GREETING → LANGUAGE_DETECTION → CUSTOMER_IDENTIFICATION → RESOLUTION → CLOSING
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from core.state import CallState, CallStage, get_initial_state
from core.prompts import (
    GREETING_MESSAGES, ID_RETRY_MESSAGES, ESCALATION_MESSAGES, CLOSING_MESSAGES,
    get_main_system_prompt, SUPPORTED_LANGUAGES
)
from database.db_tool import customer_lookup_tool, order_status_tool
from knowledge.retriever import knowledge_base_search

load_dotenv()

# Disable LangSmith tracing for now
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Initialize LLM with free/paid options
api_key = os.getenv("ANTHROPIC_API_KEY", "")
groq_key = os.getenv("GROQ_API_KEY", "")
google_key = os.getenv("GOOGLE_API_KEY", "")
openai_key = os.getenv("OPENAI_API_KEY", "")

if groq_key and groq_key != "your_groq_api_key_here":
    # Use Groq (Free, Fast)
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        model="llama3-70b-8192",
        temperature=0.3,
        max_tokens=512,
        api_key=groq_key,
    )
    print("Using Groq LLM (Free Tier)")
elif google_key and google_key != "your_google_api_key_here":
    # Use Google Gemini (Free Tier)
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        max_tokens=512,
        google_api_key=google_key,
    )
    print("Using Google Gemini LLM (Free Tier)")
elif openai_key and openai_key != "your_openai_api_key_here":
    # Use OpenAI (Free Credits)
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=512,
        api_key=openai_key,
    )
    print("Using OpenAI LLM (Free Credits)")
elif api_key and api_key != "your_anthropic_api_key_here":
    # Use Anthropic Claude (Paid)
    llm = ChatAnthropic(
        model="claude-opus-4-5",
        temperature=0.3,
        max_tokens=512,
        api_key=api_key,
    )
    print("Using Anthropic Claude (Paid)")
else:
    # Mock LLM for testing without API key
    print("WARNING: Using mock LLM. Set any LLM API key for real responses.")
    class MockLLM:
        def __init__(self):
            self.call_count = 0
            
        def invoke(self, messages):
            self.call_count += 1
            
            class MockResponse:
                def __init__(self, content):
                    self.content = content
                    
            # Check if this is an extraction prompt
            if messages and len(messages) > 0:
                content = str(messages[0].content).lower()
                if "extract the phone number or account id" in content:
                    # Return extracted ID for identification
                    if "9876543210" in content or "rahul" in content.lower():
                        return MockResponse("9876543210")
                    elif "0000000000" in content:
                        return MockResponse("0000000000")
                    else:
                        return MockResponse("9876543210")  # Default for tests
                else:
                    # Regular conversation response
                    if self.call_count == 1:
                        # First call - greeting
                        content = "Hello! Thank you for calling. I'm your AI assistant. I can help you with your account, billing, orders, and more. Could you please share your registered phone number or account ID so I can pull up your details?"
                    elif self.call_count == 2:
                        # Second call - after getting phone number
                        content = "Great, I found your account, Priya! How can I help you today?"
                    elif self.call_count == 3:
                        # Third call - responding to issue
                        content = "I see your internet is not working. Let me check your account status. According to our records, there's a known outage in your area. Our team is already working on it and it should be resolved within 2-3 hours. We'll notify you once it's fixed."
                    elif self.call_count == 4:
                        # Fourth call - Hindi response
                        content = "नमस्ते! मैं आपकी सहायता कर सकता हूँ। कृपया अपना पंजीकरण नंबर या खाता ID बताएं।"
                    else:
                        content = "I'm here to help! How can I assist you today?"
                    return MockResponse(content)
            
            # Default response for non-extraction calls
            if self.call_count == 1:
                # First call - greeting
                content = "Hello! Thank you for calling. I'm your AI assistant. I can help you with your account, billing, orders, and more. Could you please share your registered phone number or account ID so I can pull up your details?"
            elif self.call_count == 2:
                # Second call - after getting phone number
                content = "Great, I found your account, Priya! How can I help you today?"
            elif self.call_count == 3:
                # Third call - responding to issue
                content = "I see your internet is not working. Let me check your account status. According to our records, there's a known outage in your area. Our team is already working on it and it should be resolved within 2-3 hours. We'll notify you once it's fixed."
            elif self.call_count == 4:
                # Fourth call - Hindi response
                content = "नमस्ते! मैं आपकी सहायता कर सकता हूँ। कृपया अपना पंजीकरण नंबर या खाता ID बताएं।"
            else:
                content = "I'm here to help! How can I assist you today?"
                
            return MockResponse(content)
        
        def bind_tools(self, tools):
            self.tools = tools
            return self
    llm = MockLLM()

# All tools available to the agent
TOOLS = [customer_lookup_tool, order_status_tool, knowledge_base_search]

# LLM with tools bound
llm_with_tools = llm.bind_tools(TOOLS)

# ─────────────────────────────────────────
# NODE FUNCTIONS
# ─────────────────────────────────────────

def greeting_node(state: CallState) -> CallState:
    """
    Stage 1: First response. Greet the customer in English (default) and ask for their ID.
    Language will be detected from their response.
    """
    greeting = GREETING_MESSAGES["english"]
    
    state["messages"].append({"role": "assistant", "content": greeting})
    state["transcript"].append({"role": "assistant", "content": greeting, "stage": "greeting"})
    state["call_stage"] = CallStage.LANGUAGE_DETECTION
    
    return state

def language_detection_node(state: CallState) -> CallState:
    """
    Stage 2: Detect what language the customer responded in.
    Switch all future responses to that language.
    """
    last_customer_message = state.get("raw_customer_input", "")
    
    if not last_customer_message:
        return state
    
    detection_prompt = f"""Detect the language of this text. Reply with ONLY one of these exact words, nothing else:
english, hindi, tamil, telugu, bengali, marathi, kannada, malayalam, gujarati, punjabi

Text: "{last_customer_message}"

Reply with just one word:"""
    
    response = llm.invoke([HumanMessage(content=detection_prompt)])
    detected = response.content.strip().lower()
    
    # Validate
    if detected not in SUPPORTED_LANGUAGES:
        detected = "english"
    
    state["language"] = detected
    state["call_stage"] = CallStage.CUSTOMER_IDENTIFICATION
    
    return state

def customer_identification_node(state: CallState) -> CallState:
    """
    Stage 3: Extract customer ID from what they said and look them up in the database.
    """
    last_message = state.get("raw_customer_input", "")
    language = state.get("language", "english")
    
    # Use LLM to extract the ID from natural speech
    extract_prompt = f"""Extract the phone number or account ID from this text.
The user may say it in any language or mix of languages.
A phone number is 10 digits. An account ID starts with ACC.
Reply with ONLY the extracted number/ID. Nothing else. No explanation.

Text: "{last_message}"

Extracted ID:"""
    
    extraction = llm.invoke([HumanMessage(content=extract_prompt)])
    extracted_id = extraction.content.strip()
    
    # Look up in database
    customer_data = customer_lookup_tool.invoke({"identifier": extracted_id})
    
    state["customer_id"] = extracted_id
    state["identification_attempts"] = state.get("identification_attempts", 0) + 1
    
    # Check if lookup succeeded (not a "not found" message)
    if "No customer found" in customer_data or "failed" in customer_data.lower():
        # Customer not found — retry up to 3 times
        if state["identification_attempts"] < 3:
            retry_msg = ID_RETRY_MESSAGES.get(language, ID_RETRY_MESSAGES["english"])
            state["messages"].append({"role": "assistant", "content": retry_msg})
            state["transcript"].append({"role": "assistant", "content": retry_msg, "stage": "id_retry"})
            # Stay in identification stage
        else:
            # Too many failed attempts — escalate
            state["needs_human"] = True
            state["call_stage"] = CallStage.ESCALATION
    else:
        # Success — parse customer data from string back for storage
        from database.mock_db import lookup_customer
        state["customer_data"] = lookup_customer(extracted_id)
        state["customer_identified"] = True
        state["call_stage"] = CallStage.ISSUE_UNDERSTANDING
        
        # Acknowledge customer by name
        name = state["customer_data"].get("name", "").split()[0] if state["customer_data"] else ""
        ack_messages = {
            "english": f"Great, I found your account, {name}! How can I help you today?",
            "hindi": f"बढ़िया, {name} जी, आपका अकाउंट मिल गया! आज मैं आपकी कैसे मदद कर सकता हूँ?",
            "tamil": f"நன்று, {name}! உங்கள் கணக்கு கண்டுபிடிக்கப்பட்டது! இன்று என்ன உதவி வேண்டும்?",
        }
        ack = ack_messages.get(language, ack_messages["english"])
        state["messages"].append({"role": "assistant", "content": ack})
        state["transcript"].append({"role": "assistant", "content": ack, "stage": "id_success"})
    
    return state

def issue_resolution_node(state: CallState) -> CallState:
    """
    Stage 4: The main resolution loop. Uses LLM + tools to answer customer queries.
    This is the most important node — it handles the actual conversation.
    """
    language = state.get("language", "english")
    customer_data = state.get("customer_data", {})
    
    # Build system prompt with customer context
    system_prompt = get_main_system_prompt(customer_data, language)
    
    # Build message history for LLM
    lc_messages = [SystemMessage(content=system_prompt)]
    
    for msg in state["messages"]:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
    
    # Add the latest customer input
    lc_messages.append(HumanMessage(content=state.get("raw_customer_input", "")))
    
    # Run LLM with tools
    response = llm_with_tools.invoke(lc_messages)
    
    # Handle tool calls if any
    if hasattr(response, 'tool_calls') and response.tool_calls:
        # Execute each tool call
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Find and execute the right tool
            for tool in TOOLS:
                if tool.name == tool_name:
                    result = tool.invoke(tool_args)
                    tool_results.append(f"{tool_name} result: {result}")
                    break
        
        # Re-invoke LLM with tool results as context
        tool_context = "\n".join(tool_results)
        lc_messages.append(AIMessage(content=response.content or "Looking up information..."))
        lc_messages.append(HumanMessage(content=f"Tool results:\n{tool_context}\n\nNow respond to the customer in {language}."))
        
        final_response = llm.invoke(lc_messages)
        reply = final_response.content
    else:
        reply = response.content
    
    # Update state
    state["messages"].append({"role": "user", "content": state.get("raw_customer_input", "")})
    state["messages"].append({"role": "assistant", "content": reply})
    state["transcript"].append({"role": "assistant", "content": reply, "stage": "resolution"})
    state["resolution_text"] = reply
    state["call_stage"] = CallStage.RESOLUTION
    
    return state

def escalation_node(state: CallState) -> CallState:
    """Escalate to a human agent when AI cannot resolve the issue."""
    language = state.get("language", "english")
    call_sid = state.get("call_sid", "UNKNOWN")
    
    escalation_msg = ESCALATION_MESSAGES.get(
        language, ESCALATION_MESSAGES["english"]
    ).format(call_sid=call_sid)
    
    state["messages"].append({"role": "assistant", "content": escalation_msg})
    state["transcript"].append({"role": "assistant", "content": escalation_msg, "stage": "escalation"})
    state["call_stage"] = CallStage.ESCALATION
    
    return state

def closing_node(state: CallState) -> CallState:
    """End the call gracefully."""
    language = state.get("language", "english")
    closing = CLOSING_MESSAGES.get(language, CLOSING_MESSAGES["english"])
    
    state["messages"].append({"role": "assistant", "content": closing})
    state["transcript"].append({"role": "assistant", "content": closing, "stage": "closing"})
    state["call_ended"] = True
    state["call_stage"] = CallStage.ENDED
    
    return state

# ─────────────────────────────────────────
# ROUTING FUNCTIONS
# ─────────────────────────────────────────

def route_after_greeting(state: CallState) -> str:
    return "language_detection"

def route_after_language(state: CallState) -> str:
    return "customer_identification"

def route_after_identification(state: CallState) -> str:
    if state.get("needs_human"):
        return "escalation"
    if state.get("customer_identified"):
        return "issue_resolution"
    return "customer_identification"  # retry

def route_after_resolution(state: CallState) -> str:
    if state.get("needs_human"):
        return "escalation"
    if state.get("call_ended"):
        return END
    return END  # Wait for next customer input

# ─────────────────────────────────────────
# BUILD THE GRAPH
# ─────────────────────────────────────────

def build_call_agent():
    """Compile and return the LangGraph state machine."""
    graph = StateGraph(CallState)
    
    # Add all nodes
    graph.add_node("greeting", greeting_node)
    graph.add_node("language_detection", language_detection_node)
    graph.add_node("customer_identification", customer_identification_node)
    graph.add_node("issue_resolution", issue_resolution_node)
    graph.add_node("escalation", escalation_node)
    graph.add_node("closing", closing_node)
    
    # Set entry point
    graph.set_entry_point("greeting")
    
    # Add edges with routing
    graph.add_conditional_edges("greeting", route_after_greeting, {"language_detection": "language_detection"})
    graph.add_conditional_edges("language_detection", route_after_language, {"customer_identification": "customer_identification"})
    graph.add_conditional_edges("customer_identification", route_after_identification, {
        "escalation": "escalation",
        "issue_resolution": "issue_resolution",
        "customer_identification": "customer_identification",
    })
    graph.add_conditional_edges("issue_resolution", route_after_resolution, {
        "escalation": "escalation",
        END: END,
    })
    graph.add_edge("escalation", END)
    graph.add_edge("closing", END)
    
    return graph.compile()

# Singleton agent instance
call_agent = build_call_agent()
