from langchain.tools import tool
from database.mock_db import lookup_customer, get_order_status
from typing import Optional

@tool
def customer_lookup_tool(identifier: str) -> str:
    """
    Look up a customer's complete account details using their phone number or account ID.
    Use this tool whenever the customer provides their phone number, mobile number, account ID, or reference number.
    Input: a phone number (like 9876543210) or account ID (like ACC001)
    Output: Complete customer information as a formatted string.
    """
    customer = lookup_customer(identifier)
    
    if not customer:
        return f"No customer found with identifier '{identifier}'. Please ask the customer to double-check their number or ID."
    
    result = f"""Customer found:
- Name: {customer['name']}
- Phone: {customer['phone']}
- Account ID: {customer['account_id']}
- Status: {customer['status'].upper()}
- Plan: {customer['plan']}
- Balance Due: ₹{customer['balance_due']}
- Data Remaining: {customer['data_remaining']}
- Last Recharge: {customer['last_recharge']}
- Recharge Expiry: {customer['recharge_expiry']}
- Last Order: {customer['last_order_id']} — {customer['last_order_item']} ({customer['last_order_status']})
- Open Tickets: {', '.join(customer['open_tickets']) if customer['open_tickets'] else 'None'}"""
    
    return result

@tool
def order_status_tool(order_id: str) -> str:
    """
    Get the current status of a specific order using the order ID.
    Use this when a customer asks about their order status and you have an order ID.
    Input: order ID like ORD89234
    Output: Order status details.
    """
    order = get_order_status(order_id)
    
    if not order:
        return f"No order found with ID '{order_id}'."
    
    result = f"""Order {order_id}:
- Item: {order['item']}
- Status: {order['status']}
- Date: {order['date']}
- Tracking Number: {order.get('tracking', 'N/A')}"""
    
    if 'eta' in order:
        result += f"\n- Estimated Delivery: {order['eta']}"
    
    return result
