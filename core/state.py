from typing import TypedDict, Optional, List, Dict, Any
from enum import Enum

class CallStage(str, Enum):
    GREETING = "greeting"
    LANGUAGE_DETECTION = "language_detection"
    CUSTOMER_IDENTIFICATION = "customer_identification"
    ISSUE_UNDERSTANDING = "issue_understanding"
    RESOLUTION = "resolution"
    ESCALATION = "escalation"
    CLOSING = "closing"
    ENDED = "ended"

class CallState(TypedDict):
    # Call metadata
    call_sid: str                        # Twilio call ID
    call_stage: CallStage                # Current stage of the call
    
    # Customer info
    raw_customer_input: str              # Last thing customer said (raw)
    language: str                        # Detected language code: "english", "hindi", "tamil", etc.
    customer_id: Optional[str]           # Phone number or reference ID given by customer
    customer_data: Optional[Dict]        # Full record fetched from database
    
    # Conversation
    messages: List[Dict[str, str]]       # Full conversation history [{"role": "user"/"assistant", "content": "..."}]
    transcript: List[Dict[str, str]]     # Same but saved for logging
    
    # Issue handling
    issue_category: Optional[str]        # "billing", "delivery", "account", "technical", "other"
    issue_description: Optional[str]     # Summary of what the customer wants
    resolution_text: Optional[str]       # Final resolution given to customer
    
    # Flags
    customer_identified: bool            # True once DB lookup succeeded
    issue_resolved: bool                 # True once resolution is given
    needs_human: bool                    # True if AI cannot handle — escalate
    call_ended: bool                     # True when call is finished
    
    # Retry tracking
    identification_attempts: int         # How many times we asked for ID
    resolution_attempts: int             # How many times we tried to resolve

def get_initial_state(call_sid: str) -> CallState:
    """Returns a fresh CallState for a new incoming call."""
    return CallState(
        call_sid=call_sid,
        call_stage=CallStage.GREETING,
        raw_customer_input="",
        language="english",
        customer_id=None,
        customer_data=None,
        messages=[],
        transcript=[],
        issue_category=None,
        issue_description=None,
        resolution_text=None,
        customer_identified=False,
        issue_resolved=False,
        needs_human=False,
        call_ended=False,
        identification_attempts=0,
        resolution_attempts=0,
    )
