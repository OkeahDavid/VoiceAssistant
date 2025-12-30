"""
Main Voice Assistant Application
Integrates all modules to create a functional voice assistant
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

# Import modules
from src.asr import ASRModule
from src.tts import TTSModule
from src.weather_api import WeatherAPI
from src.calendar_api import CalendarAPI
from src.nlu import NLU
from src.dialogue_manager import DialogueManager


class VoiceAssistant:
    def __init__(
        self, 
        use_voice: bool = True,
        asr_model: str = "base",
        weather_api_url: str = "https://api.responsible-nlp.net/weather.php",
        calendar_api_url: str = "https://api.responsible-nlp.net/calendar.php"
    ):
        """
        Initialize Voice Assistant
        
        Args:
            use_voice: Whether to use voice input/output
            asr_model: Whisper model size for ASR
            weather_api_url: Weather API URL
            calendar_api_url: Calendar API URL
        """
        print("Initializing Voice Assistant...")
        
        self.use_voice = use_voice
        
        # Initialize modules
        if use_voice:
            print("Loading ASR module...")
            self.asr = ASRModule(model_name=asr_model)
            print("Loading TTS module...")
            self.tts = TTSModule()
        
        print("Initializing APIs...")
        self.weather_api = WeatherAPI(api_url=weather_api_url)
        self.calendar_api = CalendarAPI(api_url=calendar_api_url)
        
        print("Initializing NLU and Dialogue Manager...")
        self.nlu = NLU()
        self.dialogue_manager = DialogueManager()
        
        print("Voice Assistant ready!\n")
    
    def get_user_input(self, duration: int = 5) -> str:
        """
        Get user input (voice or text)
        
        Args:
            duration: Recording duration for voice input
            
        Returns:
            User input text
        """
        if self.use_voice:
            print("Listening... (speak now)")
            return self.asr.record_and_transcribe(duration=duration)
        else:
            return input("You: ")
    
    def respond(self, text: str):
        """
        Respond to user (voice or text)
        
        Args:
            text: Response text
        """
        print(f"Assistant: {text}")
        
        if self.use_voice:
            self.tts.text_to_speech(text)
    
    def handle_weather_query(self, entities: dict) -> str:
        """
        Handle weather-related queries
        
        Args:
            entities: Extracted entities
            
        Returns:
            Response text
        """
        location = entities.get("location")
        day = entities.get("day")
        
        if not location:
            location = self.dialogue_manager.get_last_location()
        
        if not location:
            return "I need to know the location. Which city are you asking about?"
        
        if day:
            # Specific day query
            weather = self.weather_api.get_weather_for_day(location, day)
            if weather:
                return self.weather_api.format_weather_response(weather)
            else:
                return f"I couldn't find weather information for {day} in {location}."
        else:
            # General weather query
            weather = self.weather_api.get_weather(location)
            if weather:
                # Return today's weather or first day in forecast
                if weather.get("forecast"):
                    today = weather["forecast"][0]
                    temp_min = today["temperature"]["min"]
                    temp_max = today["temperature"]["max"]
                    weather_desc = today["weather"]
                    day_name = today["day"].capitalize()
                    return f"The weather in {location} for {day_name} will be {weather_desc} with temperatures between {temp_min}°C and {temp_max}°C."
                return self.weather_api.format_weather_response(weather)
            else:
                return f"I couldn't find weather information for {location}."
    
    def handle_rain_query(self, entities: dict) -> str:
        """
        Handle rain-related queries
        
        Args:
            entities: Extracted entities
            
        Returns:
            Response text
        """
        location = entities.get("location")
        day = entities.get("day")
        
        if not location:
            location = self.dialogue_manager.get_last_location()
        
        if not location:
            return "I need to know the location. Where are you asking about?"
        
        will_rain = self.weather_api.will_it_rain(location, day)
        
        if day:
            if will_rain:
                return f"Yes, it will rain in {location} on {day}."
            else:
                return f"No, it won't rain in {location} on {day}."
        else:
            if will_rain:
                return f"Yes, rain is expected in {location} in the upcoming days."
            else:
                return f"No, no rain is expected in {location} in the upcoming days."
    
    def handle_appointment_query(self, entities: dict) -> str:
        """
        Handle appointment query
        
        Args:
            entities: Extracted entities
            
        Returns:
            Response text
        """
        next_apt = self.calendar_api.get_next_appointment()
        
        if next_apt:
            return self.calendar_api.format_appointment(next_apt)
        else:
            return "You don't have any upcoming appointments."
    
    def handle_appointment_create(self, entities: dict, original_text: str) -> str:
        """
        Handle appointment creation
        
        Args:
            entities: Extracted entities
            original_text: Original user input
            
        Returns:
            Response text
        """
        title = entities.get("title", "New Appointment")
        date = entities.get("date")
        time = entities.get("time", "09:00")
        location = entities.get("location")
        
        if not date:
            return "I need a date for the appointment. When would you like to schedule it?"
        
        # Create start and end times (1 hour duration by default)
        start_time = f"{date}T{time}"
        
        # Parse time to add 1 hour for end time
        hour, minute = map(int, time.split(":"))
        end_hour = (hour + 1) % 24
        end_time = f"{date}T{end_hour:02d}:{minute:02d}"
        
        # Create appointment
        apt = self.calendar_api.create_appointment(
            title=title,
            start_time=start_time,
            end_time=end_time,
            location=location
        )
        
        if apt:
            # Store appointment ID for future reference
            if "id" in apt:
                self.dialogue_manager.set_last_appointment_id(apt["id"])
            
            return f"I've created an appointment titled '{title}' for {date} at {time}."
        else:
            return "I couldn't create the appointment. Please try again."
    
    def handle_appointment_delete(self, entities: dict) -> str:
        """
        Handle appointment deletion
        
        Args:
            entities: Extracted entities
            
        Returns:
            Response text
        """
        appointment_id = entities.get("appointment_id")
        
        if not appointment_id:
            appointment_id = self.dialogue_manager.get_last_appointment_id()
        
        if not appointment_id:
            return "I need to know which appointment to delete. Can you be more specific?"
        
        success = self.calendar_api.delete_appointment(appointment_id)
        
        if success:
            return f"I've deleted the appointment."
        else:
            return "I couldn't delete the appointment. It may not exist."
    
    def handle_appointment_update(self, entities: dict, original_text: str) -> str:
        """
        Handle appointment update
        
        Args:
            entities: Extracted entities
            original_text: Original user input
            
        Returns:
            Response text
        """
        appointment_id = entities.get("appointment_id")
        
        if not appointment_id:
            appointment_id = self.dialogue_manager.get_last_appointment_id()
        
        if not appointment_id:
            # Try to get next appointment
            next_apt = self.calendar_api.get_next_appointment()
            if next_apt and "id" in next_apt:
                appointment_id = next_apt["id"]
            else:
                return "I need to know which appointment to update. Can you be more specific?"
        
        # Determine what to update
        text_lower = original_text.lower()
        
        update_data = {}
        
        if "place" in text_lower or "location" in text_lower:
            location = entities.get("location")
            # If no specific location mentioned, ask for it
            if not location:
                return "What location would you like to change it to?"
            update_data["location"] = location
        
        if "title" in text_lower or "name" in text_lower:
            title = entities.get("title")
            if title:
                update_data["title"] = title
        
        if "time" in text_lower or "when" in text_lower:
            date = entities.get("date")
            time = entities.get("time")
            if date and time:
                update_data["start_time"] = f"{date}T{time}"
        
        if not update_data:
            return "I'm not sure what you want to update. Can you be more specific?"
        
        apt = self.calendar_api.update_appointment(appointment_id, **update_data)
        
        if apt:
            return f"I've updated the appointment."
        else:
            return "I couldn't update the appointment."
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and generate response
        
        Args:
            user_input: User's input text
            
        Returns:
            System response
        """
        # Get last intent from dialogue manager for context
        last_intent = self.dialogue_manager.context.get("last_intent")
        
        # Parse input with NLU (with context)
        parsed_input = self.nlu.parse_input(user_input, last_intent)
        
        # Resolve references using dialogue manager
        parsed_input = self.dialogue_manager.resolve_reference(parsed_input)
        
        intent = parsed_input["intent"]
        entities = parsed_input.get("entities", {})
        
        # Generate response based on intent
        if intent == "weather_query":
            response = self.handle_weather_query(entities)
        elif intent == "rain_query":
            response = self.handle_rain_query(entities)
        elif intent == "appointment_query":
            response = self.handle_appointment_query(entities)
        elif intent == "appointment_create":
            response = self.handle_appointment_create(entities, user_input)
        elif intent == "appointment_delete":
            response = self.handle_appointment_delete(entities)
        elif intent == "appointment_update":
            response = self.handle_appointment_update(entities, user_input)
        else:
            response = "I'm not sure I understand. Can you rephrase that?"
        
        # Add turn to conversation history
        self.dialogue_manager.add_turn(user_input, parsed_input, response)
        
        return response
    
    def run(self):
        """Run the voice assistant"""
        self.respond("Hello! I'm your voice assistant. I can help you with weather information and calendar management. How can I assist you today?")
        
        while True:
            try:
                # Get user input
                user_input = self.get_user_input()
                
                if not user_input or user_input.strip() == "":
                    continue
                
                print(f"You: {user_input}")
                
                # Check for exit commands
                if user_input.lower() in ["exit", "quit", "goodbye", "bye"]:
                    self.respond("Goodbye! Have a great day!")
                    break
                
                # Process input and generate response
                response = self.process_input(user_input)
                
                # Respond to user
                self.respond(response)
                
            except KeyboardInterrupt:
                print("\n")
                self.respond("Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.respond("I encountered an error. Please try again.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Assistant")
    parser.add_argument("--no-voice", action="store_true", help="Use text input/output instead of voice")
    parser.add_argument("--asr-model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size for ASR")
    
    args = parser.parse_args()
    
    # Create and run assistant
    assistant = VoiceAssistant(
        use_voice=not args.no_voice,
        asr_model=args.asr_model
    )
    
    assistant.run()


if __name__ == "__main__":
    main()
