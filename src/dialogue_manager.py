"""
Dialogue Manager
Manages conversation state and context
"""
from typing import Dict, List, Optional
from datetime import datetime


class DialogueManager:
    def __init__(self):
        """Initialize dialogue manager"""
        self.conversation_history: List[Dict] = []
        self.context: Dict = {
            "last_location": None,
            "last_day": None,
            "last_appointment_id": None,
            "last_intent": None
        }
        
    def add_turn(self, user_input: str, parsed_input: Dict, system_response: str):
        """
        Add a conversation turn to history
        
        Args:
            user_input: User's original input
            parsed_input: Parsed input from NLU
            system_response: System's response
        """
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "parsed_input": parsed_input,
            "system_response": system_response
        }
        self.conversation_history.append(turn)
        
        # Update context
        self._update_context(parsed_input)
    
    def _update_context(self, parsed_input: Dict):
        """
        Update conversation context based on parsed input
        
        Args:
            parsed_input: Parsed input from NLU
        """
        entities = parsed_input.get("entities", {})
        intent = parsed_input.get("intent")
        
        # Update location context
        if "location" in entities:
            self.context["last_location"] = entities["location"]
        
        # Update day context
        if "day" in entities:
            self.context["last_day"] = entities["day"]
        
        # Update intent context
        if intent:
            self.context["last_intent"] = intent
    
    def set_last_appointment_id(self, appointment_id: int):
        """
        Set the last created/modified appointment ID
        
        Args:
            appointment_id: Appointment ID
        """
        self.context["last_appointment_id"] = appointment_id
    
    def get_last_location(self) -> Optional[str]:
        """Get the last mentioned location"""
        return self.context.get("last_location")
    
    def get_last_day(self) -> Optional[str]:
        """Get the last mentioned day"""
        return self.context.get("last_day")
    
    def get_last_appointment_id(self) -> Optional[int]:
        """Get the last appointment ID"""
        return self.context.get("last_appointment_id")
    
    def resolve_reference(self, parsed_input: Dict) -> Dict:
        """
        Resolve references like "there", "it", "previously created"
        
        Args:
            parsed_input: Parsed input from NLU
            
        Returns:
            Updated parsed input with resolved references
        """
        text = parsed_input.get("text", "").lower()
        entities = parsed_input.get("entities", {})
        
        # Resolve location references
        if "there" in text or "that place" in text:
            if "location" not in entities and self.context["last_location"]:
                entities["location"] = self.context["last_location"]
        
        # Resolve "it" for weather queries
        if ("it" in text or "that" in text) and "rain" in text:
            if "location" not in entities and self.context["last_location"]:
                entities["location"] = self.context["last_location"]
        
        # Resolve "previously created" or "that appointment"
        if ("previous" in text or "that" in text or "it" in text) and "appointment" in text:
            if self.context["last_appointment_id"] is not None:
                entities["appointment_id"] = self.context["last_appointment_id"]
        
        parsed_input["entities"] = entities
        return parsed_input
    
    def get_conversation_history(self, n: int = 5) -> List[Dict]:
        """
        Get last n conversation turns
        
        Args:
            n: Number of turns to retrieve
            
        Returns:
            List of conversation turns
        """
        return self.conversation_history[-n:] if self.conversation_history else []
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.context = {
            "last_location": None,
            "last_day": None,
            "last_appointment_id": None,
            "last_intent": None
        }


if __name__ == "__main__":
    # Test Dialogue Manager
    dm = DialogueManager()
    
    print("Testing Dialogue Manager...\n")
    
    # Simulate conversation
    turn1 = {
        "intent": "weather_query",
        "text": "What's the weather in Marburg?",
        "entities": {"location": "Marburg"}
    }
    dm.add_turn("What's the weather in Marburg?", turn1, "The weather in Marburg is sunny.")
    
    turn2 = {
        "intent": "rain_query",
        "text": "Will it rain there on Saturday?",
        "entities": {"day": "saturday"}
    }
    turn2_resolved = dm.resolve_reference(turn2)
    print(f"Resolved reference: {turn2_resolved}")
    print(f"Location resolved to: {turn2_resolved['entities'].get('location')}")
