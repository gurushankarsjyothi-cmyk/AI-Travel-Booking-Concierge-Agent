"""
Booking Management Tool - Handles reservation creation and confirmation
"""

from langchain.tools import tool
import json
import os
from datetime import datetime
from typing import Dict


@tool
def create_booking(
    booking_type: str,
    booking_details: str,
    customer_name: str,
    customer_email: str
) -> str:
    """
    Create a new booking for flights or hotels.
    
    Args:
        booking_type: Type of booking - must be either 'flight' or 'hotel'
        booking_details: Details of the flight/hotel to book (as JSON string)
        customer_name: Customer's full name
        customer_email: Customer's email address
        
    Returns:
        JSON string with booking confirmation and reference number
    """
    try:
        # Validate booking type
        if booking_type.lower() not in ['flight', 'hotel']:
            return json.dumps({
                "success": False,
                "error": "Invalid booking type. Must be 'flight' or 'hotel'."
            })
        
        # Parse booking details if it's a string
        if isinstance(booking_details, str):
            try:
                booking_details = json.loads(booking_details)
            except:
                # If not JSON, treat as string description
                booking_details = {"description": booking_details}
        
        # Generate unique booking reference
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        booking_ref = f"{booking_type.upper()[:3]}-{timestamp}"
        
        # Create booking object
        booking = {
            "success": True,
            "booking_reference": booking_ref,
            "booking_type": booking_type.lower(),
            "status": "CONFIRMED",
            "booking_details": booking_details,
            "customer_info": {
                "name": customer_name,
                "email": customer_email
            },
            "created_at": datetime.now().isoformat(),
            "confirmation_message": f"Your {booking_type} booking has been confirmed!"
        }
        
        # Save booking to file
        bookings_dir = "data/bookings"
        os.makedirs(bookings_dir, exist_ok=True)
        
        booking_file = os.path.join(bookings_dir, f"{booking_ref}.json")
        with open(booking_file, "w") as f:
            json.dump(booking, f, indent=2)
        
        return json.dumps(booking, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Booking creation failed: {str(e)}"
        })
