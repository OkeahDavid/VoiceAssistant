"""
Test suite for the voice assistant
Run without voice to test functionality
"""
from main import VoiceAssistant


def test_assistant():
    """Test the voice assistant with predefined commands"""
    
    print("="*60)
    print("Testing Voice Assistant (Text Mode)")
    print("="*60)
    
    # Initialize assistant in text mode
    assistant = VoiceAssistant(use_voice=False)
    
    # Test commands
    test_commands = [
        "What will the weather be like today in Marburg?",
        "What will the weather be on Friday in Frankfurt?",
        "Will it rain there on Saturday?",
        "Where is my next appointment?",
        "Add an appointment titled Team Meeting for tomorrow at 2 PM.",
        "Change the place for my appointment tomorrow to Room 15.",
        "Delete the previously created appointment.",
    ]
    
    print("\nTesting required commands:\n")
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {command}")
        print(f"{'='*60}")
        
        response = assistant.process_input(command)
        print(f"Response: {response}")
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)


if __name__ == "__main__":
    test_assistant()
