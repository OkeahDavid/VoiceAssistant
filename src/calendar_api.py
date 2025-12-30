"""
Calendar API Integration
Handles CRUD operations for calendar entries
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime


class CalendarAPI:
    def __init__(self, api_url: str = "https://api.responsible-nlp.net/calendar.php", calendar_id: str = None):
        """
        Initialize Calendar API client
        
        Args:
            api_url: Base URL for the calendar API
            calendar_id: Calendar ID to use (generates one if not provided)
        """
        self.api_url = api_url
        # Use provided calendar_id or generate a simple one
        if calendar_id:
            self.calendar_id = calendar_id
        else:
            # Use a simple calendar ID for this session
            import hashlib
            import time
            session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
            self.calendar_id = f"voiceassistant_{session_id}"
        
        print(f"Using calendar ID: {self.calendar_id}")
        
    def create_appointment(
        self, 
        title: str, 
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create a new calendar appointment
        
        Args:
            title: Appointment title
            start_time: Start time in ISO format (YYYY-MM-DDTHH:MM)
            end_time: End time in ISO format
            description: Optional description
            location: Optional location
            
        Returns:
            Created appointment data or None if error
        """
        if not self.calendar_id:
            print("No calendar ID available")
            return None
            
        data = {
            "title": title,
            "start_time": start_time,
            "end_time": end_time
        }
        
        if description:
            data["description"] = description
        if location:
            data["location"] = location
        
        try:
            url = f"{self.api_url}?calenderid={self.calendar_id}"
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating appointment: {e}")
            return None
    
    def get_all_appointments(self) -> Optional[List[Dict]]:
        """
        Get all calendar appointments
        
        Returns:
            List of appointments or None if error
        """
        if not self.calendar_id:
            return None
            
        try:
            url = f"{self.api_url}?calenderid={self.calendar_id}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching appointments: {e}")
            return None
    
    def get_appointment(self, appointment_id: int) -> Optional[Dict]:
        """
        Get a single appointment by ID
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            Appointment data or None if error
        """
        if not self.calendar_id:
            return None
            
        try:
            url = f"{self.api_url}?calenderid={self.calendar_id}&id={appointment_id}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching appointment: {e}")
            return None
    
    def update_appointment(
        self,
        appointment_id: int,
        title: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update an existing appointment
        
        Args:
            appointment_id: Appointment ID
            title: New title (optional)
            start_time: New start time (optional)
            end_time: New end time (optional)
            description: New description (optional)
            location: New location (optional)
            
        Returns:
            Updated appointment data or None if error
        """
        if not self.calendar_id:
            return None
            
        data = {}
        if title:
            data["title"] = title
        if start_time:
            data["start_time"] = start_time
        if end_time:
            data["end_time"] = end_time
        if description:
            data["description"] = description
        if location:
            data["location"] = location
        
        try:
            url = f"{self.api_url}?calenderid={self.calendar_id}&id={appointment_id}"
            response = requests.put(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error updating appointment: {e}")
            return None
    
    def delete_appointment(self, appointment_id: int) -> bool:
        """
        Delete an appointment
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.calendar_id:
            return False
            
        try:
            url = f"{self.api_url}?calenderid={self.calendar_id}&id={appointment_id}"
            response = requests.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting appointment: {e}")
            return False
    
    def get_next_appointment(self) -> Optional[Dict]:
        """
        Get the next upcoming appointment
        
        Returns:
            Next appointment or None
        """
        appointments = self.get_all_appointments()
        if not appointments:
            return None
        
        # Handle case where API returns a string or error message
        if isinstance(appointments, str):
            return None
        
        # Handle case where API returns a dict with error
        if isinstance(appointments, dict) and "error" in appointments:
            return None
        
        now = datetime.now()
        upcoming = []
        
        for apt in appointments:
            # Skip if appointment is not a dict
            if not isinstance(apt, dict):
                continue
                
            try:
                start_time = datetime.fromisoformat(apt.get("start_time", ""))
                if start_time > now:
                    upcoming.append(apt)
            except (ValueError, TypeError):
                continue
        
        if not upcoming:
            return None
        
        # Sort by start time and return the first one
        upcoming.sort(key=lambda x: datetime.fromisoformat(x["start_time"]))
        return upcoming[0]
    
    def format_appointment(self, appointment: Dict) -> str:
        """
        Format appointment data into a human-readable string
        
        Args:
            appointment: Appointment data
            
        Returns:
            Formatted string
        """
        if not appointment:
            return "No appointment found."
        
        title = appointment.get("title", "Untitled")
        start = appointment.get("start_time", "")
        end = appointment.get("end_time", "")
        location = appointment.get("location", "")
        description = appointment.get("description", "")
        
        response = f"Appointment: {title}"
        if start:
            response += f"\nStart: {start}"
        if end:
            response += f"\nEnd: {end}"
        if location:
            response += f"\nLocation: {location}"
        if description:
            response += f"\nDescription: {description}"
        
        return response


if __name__ == "__main__":
    # Test Calendar API
    api = CalendarAPI()
    
    print("Testing Calendar API...\n")
    
    # Test 1: Create appointment
    print("1. Creating appointment...")
    apt = api.create_appointment(
        title="Team Meeting",
        description="Discuss project progress",
        start_time="2025-12-31T10:00",
        end_time="2025-12-31T11:00",
        location="Room 12"
    )
    if apt:
        print(api.format_appointment(apt))
    
    # Test 2: Get all appointments
    print("\n2. Getting all appointments...")
    all_apts = api.get_all_appointments()
    if all_apts:
        print(f"Found {len(all_apts)} appointments")
