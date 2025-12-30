"""
NLU Module - Natural Language Understanding
Extracts intents and entities from user input
"""
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dateutil import parser as date_parser


class NLU:
    def __init__(self):
        """Initialize NLU module"""
        self.intents = {
            "weather_query": [
                r"what.*(weather|temperature|forecast)",
                r"(weather|temperature|forecast).*be",
                r"how.*(weather|warm|cold|hot)",
                r"(tell|show).*weather",
                r"what about.*in\s+[a-z]",  # "what about in [location]"
                r"how about.*in\s+[a-z]"    # "how about in [location]"
            ],
            "rain_query": [
                r"will.*rain",
                r"is.*rain",
                r"rain.*forecast",
                r"going.*rain"
            ],
            "appointment_delete": [
                r"(delete|remove|cancel).*(appointment|meeting|event)",
                r"(appointment|meeting|event).*(delete|remove|cancel)"
            ],
            "appointment_update": [
                r"(change|update|modify|edit).*(appointment|meeting|event)",
                r"(move|reschedule).*(appointment|meeting|event)"
            ],
            "appointment_query": [
                r"(where|when|what).*(next|upcoming).*appointment",
                r"(show|tell|list).*(appointment|meeting|event)",
                r"do.*have.*(appointment|meeting)"
            ],
            "appointment_create": [
                r"(add|create|schedule|make).*(appointment|meeting|event)",
                r"(appointment|meeting|event).*(for|on|at)",
                r"book.*(appointment|meeting)"
            ]
        }
        
        self.days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
    def extract_intent(self, text: str, last_intent: Optional[str] = None) -> str:
        """
        Extract intent from user input
        
        Args:
            text: User input text
            last_intent: Previous intent for context
            
        Returns:
            Intent name or "unknown"
        """
        text_lower = text.lower()
        
        # Check for contextual queries (e.g., "what about in frankfurt" after weather query)
        if last_intent and "weather" in last_intent:
            # If user asks "what about" or similar with a location, assume same intent
            if re.search(r"(what|how)\s+(about|in)", text_lower):
                location = self.extract_location(text)
                if location:
                    return last_intent
        
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        return "unknown"
    
    def extract_location(self, text: str) -> Optional[str]:
        """
        Extract location/place from text
        
        Args:
            text: User input text
            
        Returns:
            Location name or None
        """
        # Common patterns for location (case-insensitive)
        patterns = [
            r"in\s+([a-zA-Z][a-zA-Z]+(?:\s+[a-zA-Z][a-zA-Z]+)*)",
            r"at\s+([a-zA-Z][a-zA-Z]+(?:\s+[a-zA-Z][a-zA-Z]+)*)",
            r"for\s+([a-zA-Z][a-zA-Z]+(?:\s+[a-zA-Z][a-zA-Z]+)*)",
            r"to\s+([a-zA-Z0-9\s]+?)(?:\.|,|$|\s+for|\s+at|\s+on)",  # for "to Room 15"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Check if it's a known city/location (not a common word)
                if location.lower() not in ["the", "a", "an", "my", "tomorrow", "today"]:
                    # Capitalize first letter of each word for consistency
                    return location.title()
        
        return None
    
    def extract_day(self, text: str) -> Optional[str]:
        """
        Extract day from text
        
        Args:
            text: User input text
            
        Returns:
            Day name or "today"/"tomorrow" or None
        """
        text_lower = text.lower()
        
        # Check for "today" or "tomorrow"
        if "today" in text_lower:
            return "today"
        if "tomorrow" in text_lower:
            return "tomorrow"
        
        # Check for day names
        for day in self.days:
            if day in text_lower:
                return day
        
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """
        Extract date from text and convert to ISO format
        
        Args:
            text: User input text
            
        Returns:
            Date in ISO format (YYYY-MM-DD) or None
        """
        text_lower = text.lower()
        
        # Handle "today"
        if "today" in text_lower:
            return datetime.now().strftime("%Y-%m-%d")
        
        # Handle "tomorrow"
        if "tomorrow" in text_lower:
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Handle day names (this week or next week)
        for day in self.days:
            if day in text_lower:
                target_day = self.days.index(day)
                current_day = datetime.now().weekday()
                
                days_ahead = target_day - current_day
                if days_ahead < 0:  # Target day already passed this week
                    days_ahead += 7
                elif days_ahead == 0 and "next" in text_lower:
                    days_ahead = 7
                
                target_date = datetime.now() + timedelta(days=days_ahead)
                return target_date.strftime("%Y-%m-%d")
        
        # Try to extract date patterns like "12th of January", "January 12", "12/01/2025"
        date_patterns = [
            r"(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([A-Z][a-z]+)",  # 12th of January
            r"([A-Z][a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?",  # January 12th
            r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})",  # 12/01/2025
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(0)
                    parsed_date = date_parser.parse(date_str, fuzzy=True)
                    
                    # If year not specified, use current year or next year if date has passed
                    if parsed_date.year == 1900:  # Default year from parser
                        parsed_date = parsed_date.replace(year=datetime.now().year)
                        if parsed_date < datetime.now():
                            parsed_date = parsed_date.replace(year=datetime.now().year + 1)
                    
                    return parsed_date.strftime("%Y-%m-%d")
                except:
                    continue
        
        return None
    
    def extract_time(self, text: str, default_hour: int = 9) -> str:
        """
        Extract time from text
        
        Args:
            text: User input text
            default_hour: Default hour if not specified
            
        Returns:
            Time in HH:MM format
        """
        # Look for time patterns
        time_patterns = [
            r"(\d{1,2}):(\d{2})\s*(am|pm)?",
            r"(\d{1,2})\s*(am|pm)",
            r"at\s+(\d{1,2})",
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                    
                    # Handle AM/PM
                    if len(match.groups()) > 2 and match.group(3):
                        if match.group(3) == "pm" and hour < 12:
                            hour += 12
                        elif match.group(3) == "am" and hour == 12:
                            hour = 0
                    
                    return f"{hour:02d}:{minute:02d}"
                except:
                    continue
        
        # Default time
        return f"{default_hour:02d}:00"
    
    def extract_title(self, text: str) -> Optional[str]:
        """
        Extract appointment title from text
        
        Args:
            text: User input text
            
        Returns:
            Title or None
        """
        # Look for patterns like "titled XYZ", "called XYZ", "named XYZ"
        patterns = [
            r"titled?\s+['\"]?([^'\"]+)['\"]?",
            r"called\s+['\"]?([^'\"]+)['\"]?",
            r"named\s+['\"]?([^'\"]+)['\"]?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
        
        return None
    
    def parse_input(self, text: str, last_intent: Optional[str] = None) -> Dict:
        """
        Parse user input and extract all relevant information
        
        Args:
            text: User input text
            last_intent: Previous intent for context
            
        Returns:
            Dictionary with intent and entities
        """
        intent = self.extract_intent(text, last_intent)
        
        result = {
            "intent": intent,
            "text": text,
            "entities": {}
        }
        
        # Extract entities based on intent
        if "weather" in intent or "rain" in intent:
            location = self.extract_location(text)
            day = self.extract_day(text)
            
            if location:
                result["entities"]["location"] = location
            if day:
                result["entities"]["day"] = day
        
        if "appointment" in intent:
            date = self.extract_date(text)
            time = self.extract_time(text)
            title = self.extract_title(text)
            location = self.extract_location(text)
            
            if date:
                result["entities"]["date"] = date
            if time:
                result["entities"]["time"] = time
            if title:
                result["entities"]["title"] = title
            if location:
                result["entities"]["location"] = location
        
        return result


if __name__ == "__main__":
    # Test NLU module
    nlu = NLU()
    
    test_inputs = [
        "What will the weather be like today in Marburg?",
        "What will the weather be on Friday in Frankfurt?",
        "Will it rain there on Saturday?",
        "Where is my next appointment?",
        "Add an appointment titled Team Meeting for the 12th of January.",
        "Delete the previously created appointment.",
        "Change the place for my appointment tomorrow."
    ]
    
    print("Testing NLU...\n")
    for text in test_inputs:
        result = nlu.parse_input(text)
        print(f"Input: {text}")
        print(f"Intent: {result['intent']}")
        print(f"Entities: {result['entities']}")
        print()
