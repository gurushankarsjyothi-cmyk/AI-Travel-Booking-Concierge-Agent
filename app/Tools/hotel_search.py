"""
Hotel Search Tool - Integrates with Amadeus Hotel API
"""

from langchain.tools import tool
import requests
import os
from typing import List, Dict
import json


@tool
def search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    guests: int = 1,
    max_results: int = 5
) -> str:
    """
    Search for available hotels in a specified city.
    
    Args:
        city: City name or airport code (e.g., 'Paris', 'BLR', 'Mumbai')
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        guests: Number of guests (default: 1)
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        JSON string containing list of hotel options with details and pricing
    """
    try:
        api_key = os.getenv("AMADEUS_API_KEY")
        api_secret = os.getenv("AMADEUS_API_SECRET")
        
        if not api_key or not api_secret:
            # Return mock data if no API credentials
            return _get_mock_hotel_data(city, check_in, check_out, guests, max_results)
        
        # Get access token
        token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": api_secret
        }
        
        token_response = requests.post(token_url, data=token_data, timeout=10)
        
        if token_response.status_code != 200:
            return _get_mock_hotel_data(city, check_in, check_out, guests, max_results)
        
        access_token = token_response.json()["access_token"]
        
        # Search hotels by city
        search_url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "cityCode": city[:3].upper() if len(city) == 3 else city,
            "radius": 5,
            "radiusUnit": "KM",
            "hotelSource": "ALL"
        }
        
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            hotels = []
            
            for hotel in data.get("data", [])[:max_results]:
                hotels.append({
                    "name": hotel.get("name", "Unknown Hotel"),
                    "hotel_id": hotel.get("hotelId", "N/A"),
                    "address": hotel.get("address", {}).get("cityName", city),
                    "rating": "4.5",  # Mock rating
                    "price_per_night": f"${100 + (len(hotels) * 25)}",
                    "amenities": ["WiFi", "Pool", "Gym", "Restaurant"]
                })
            
            result = {
                "success": True,
                "city": city,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "hotels": hotels,
                "count": len(hotels)
            }
            
            return json.dumps(result, indent=2)
        else:
            return _get_mock_hotel_data(city, check_in, check_out, guests, max_results)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Hotel search failed: {str(e)}",
            "message": "Using sample data instead"
        })


def _get_mock_hotel_data(city: str, check_in: str, check_out: str, guests: int, max_results: int) -> str:
    """
    Generate mock hotel data for demonstration purposes
    """
    hotels = [
        {
            "name": "Grand Plaza Hotel",
            "hotel_id": "H001",
            "address": f"{city} City Center",
            "rating": "4.5",
            "price_per_night": "$120",
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant", "Spa"]
        },
        {
            "name": "City View Inn",
            "hotel_id": "H002",
            "address": f"{city} Downtown",
            "rating": "4.2",
            "price_per_night": "$95",
            "amenities": ["WiFi", "Breakfast", "Parking", "Airport Shuttle"]
        },
        {
            "name": "Luxury Suites",
            "hotel_id": "H003",
            "address": f"{city} Business District",
            "rating": "4.8",
            "price_per_night": "$180",
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant", "Bar", "Spa", "Conference Rooms"]
        },
        {
            "name": "Budget Stay Hotel",
            "hotel_id": "H004",
            "address": f"{city} Airport Area",
            "rating": "3.9",
            "price_per_night": "$65",
            "amenities": ["WiFi", "Breakfast", "24/7 Reception"]
        },
        {
            "name": "Boutique Heritage Hotel",
            "hotel_id": "H005",
            "address": f"{city} Old Town",
            "rating": "4.6",
            "price_per_night": "$145",
            "amenities": ["WiFi", "Restaurant", "Rooftop Terrace", "Heritage Tours"]
        }
    ]
    
    result = {
        "success": True,
        "city": city,
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "hotels": hotels[:max_results],
        "count": min(len(hotels), max_results),
        "note": "Sample data shown. Configure AMADEUS_API_KEY for live data."
    }
    
    return json.dumps(result, indent=2)
