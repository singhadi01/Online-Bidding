from django import template
from bidding.models import Bid

register = template.Library()

@register.filter
def get_item(highest_bids, item_id):
    """Retrieve the highest bid for a given item from a dictionary or QuerySet."""
    if isinstance(highest_bids, dict):  # If it's a dictionary, use .get()
        return highest_bids.get(item_id)
    
    if hasattr(highest_bids, "filter"):  # If it's a QuerySet, apply filter
        return highest_bids.filter(item__id=item_id).first()
    
    return None
@register.filter
def get_bid_amount(highest_bids, item_id):
    """Get the highest bid amount for an item."""
    bid_info = highest_bids.get(item_id)
    return f"Rs: {bid_info['amount']}" if bid_info else "No bids yet"

@register.filter
def get_bidder(highest_bids, item_id):
    """Get the highest bidder's username for an item."""
    bid_info = highest_bids.get(item_id)
    return bid_info['bidder'] if bid_info else "N/A"

@register.filter
def get_bidder_email(highest_bids, item_id):
    """Get the highest bidder's email for an item."""
    bid_info = highest_bids.get(item_id)
    return bid_info['email'] if bid_info else "N/A"