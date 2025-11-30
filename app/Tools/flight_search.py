"""
Flight Search Tool - Integrates with Google Flights API via SerpAPI
"""

from langchain.tools import tool
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import json


@tool
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None
) -> str:
    """
    Search for available flights between two locations.
    
    Args:
        origin: Departure airport code or city name (e.g., 'JFK', 'New York', 'Delhi')
        destination: Arrival airport code or city name (e.g., 'CDG', 'Paris', 'Mumbai')
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Optional return date for round-trip in YYYY-MM-DD format
        
    Returns:
        JSON string containing flight options with prices, airlines, and schedules
    """
    try:
        api_key = os.getenv("SERPAPI_KEY")
        
        if not api_key:
            # Return mock data if no API key
            return _get_mock_flight_data(origin, destination, departure_date, return_date)
        
        # Build SerpAPI parameters
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": departure_date,
            "api_key": api_key,
            "currency": "USD",
            "hl": "en"
        }
        
        if return_date:
            params["return_date"] = return_date
            params["type"] = "1"  # Round trip
        else:
            params["type"] = "2"  # One way
        
        # Make API request
        response = requests.get(
            "https://serpapi.com/search",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract flight information
            flights = []
            if "best_flights" in data:
                for flight in data["best_flights"][:5]:  # Top 5 results
                    flights.append({
                        "price": flight.get("price", "N/A"),
                        "airline": flight["flights"][0].get("airline", "Unknown"),
                        "departure_time": flight["flights"][0].get("departure_airport", {}).get("time", "N/A"),
                        "arrival_time": flight["flights"][0].get("arrival_airport", {}).get("time", "N/A"),
                        "duration": flight.get("total_duration", "N/A"),
                        "layovers": len(flight.get("flights", [])) - 1
                    })
            
            result = {
                "success": True,
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "flights": flights,
                "count": len(flights)
            }
            
            return json.dumps(result, indent=2)
        else:
            return _get_mock_flight_data(origin, destination, departure_date, return_date)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Flight search failed: {str(e)}",
            "message": "Using sample data instead"
        })


def _get_mock_flight_data(origin: str, destination: str, departure_date: str, return_date: Optional[str] = None) -> str:
    """
    Generate mock flight data for demonstration purposes
    """
    flights = [
        {
            "price": "$450",
            "airline": "Air India",
            "departure_time": "10:30 AM",
            "arrival_time": "02:45 PM",
            "duration": "2h 15m",
            "layovers": 0
        },
        {
            "price": "$380",
            "airline": "IndiGo",
            "departure_time": "06:15 AM",
            "arrival_time": "10:30 AM",
            "duration": "2h 15m",
            "layovers": 0
        },
        {
            "price": "$520",
            "airline": "Vistara",
            "departure_time": "03:00 PM",
            "arrival_time": "07:20 PM",
            "duration": "2h 20m",
            "layovers": 0
        },
        {
            "price": "$340",
            "airline": "SpiceJet",
            "departure_time": "11:45 PM",
            "arrival_time": "04:00 AM (+1)",
            "duration": "2h 15m",
            "layovers": 0
        }
    ]
    
    result = {
        "success": True,
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "flights": flights,
        "count": len(flights),
        "note": "Sample data shown. Configure SERPAPI_KEY for live data."
    }
    
    return json.dumps(result, indent=2)
