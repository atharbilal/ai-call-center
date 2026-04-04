"""
Mock customer database.
In production this gets replaced with real DB calls (MySQL / PostgreSQL / MongoDB).
The lookup_customer() function signature stays the same — only the internals change.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import random

# Simulated customer records
MOCK_CUSTOMERS: Dict[str, Dict[str, Any]] = {
    "9876543210": {
        "name": "Rahul Sharma",
        "phone": "9876543210",
        "email": "rahul.sharma@email.com",
        "account_id": "ACC001",
        "status": "active",
        "plan": "Premium - ₹499/month",
        "balance_due": 0,
        "data_remaining": "12.5 GB",
        "last_recharge": "2024-06-01",
        "recharge_expiry": "2024-07-01",
        "last_order_id": "ORD89234",
        "last_order_status": "Delivered",
        "last_order_item": "Samsung Galaxy Buds",
        "last_order_date": "2024-06-10",
        "open_tickets": [],
        "company": "TelecomCo",
    },
    "8765432109": {
        "name": "Priya Menon",
        "phone": "8765432109",
        "email": "priya.menon@email.com",
        "account_id": "ACC002",
        "status": "suspended",
        "plan": "Basic - ₹199/month",
        "balance_due": 398,
        "data_remaining": "0 GB",
        "last_recharge": "2024-04-01",
        "recharge_expiry": "2024-05-01",
        "last_order_id": "ORD77712",
        "last_order_status": "Out for delivery",
        "last_order_item": "OnePlus Nord CE4",
        "last_order_date": "2024-06-14",
        "open_tickets": ["TKT003 - Refund request pending"],
        "company": "TelecomCo",
    },
    "7654321098": {
        "name": "Arun Patel",
        "phone": "7654321098",
        "email": "arun.patel@email.com",
        "account_id": "ACC003",
        "status": "active",
        "plan": "Gold - ₹999/month",
        "balance_due": 0,
        "data_remaining": "45 GB",
        "last_recharge": "2024-06-05",
        "recharge_expiry": "2024-07-05",
        "last_order_id": "ORD90011",
        "last_order_status": "Shipped",
        "last_order_item": "Noise ColorFit Pro 5",
        "last_order_date": "2024-06-13",
        "open_tickets": [],
        "company": "TelecomCo",
    },
}

def lookup_customer(identifier: str) -> Optional[Dict[str, Any]]:
    """
    Look up a customer by phone number or account ID.
    Returns customer dict if found, None if not found.
    
    In production: replace with actual DB query.
    Example production code:
        result = db.query("SELECT * FROM customers WHERE phone = %s OR account_id = %s", (identifier, identifier))
        return result.fetchone()
    """
    # Clean the identifier — remove spaces, dashes, +91 prefix
    clean_id = identifier.replace(" ", "").replace("-", "").replace("+91", "").strip()
    
    # Try phone number lookup
    if clean_id in MOCK_CUSTOMERS:
        return MOCK_CUSTOMERS[clean_id]
    
    # Try account ID lookup
    for customer in MOCK_CUSTOMERS.values():
        if customer.get("account_id") == identifier.upper():
            return customer
    
    return None

def get_order_status(order_id: str) -> Optional[Dict[str, Any]]:
    """Look up a specific order. In production: query orders table."""
    mock_orders = {
        "ORD89234": {"status": "Delivered", "item": "Samsung Galaxy Buds", "date": "2024-06-10", "tracking": "TRK123456"},
        "ORD77712": {"status": "Out for delivery", "item": "OnePlus Nord CE4", "date": "2024-06-14", "tracking": "TRK789012", "eta": "Today by 8 PM"},
        "ORD90011": {"status": "Shipped", "item": "Noise ColorFit Pro 5", "date": "2024-06-13", "tracking": "TRK345678", "eta": "June 16"},
    }
    return mock_orders.get(order_id)
