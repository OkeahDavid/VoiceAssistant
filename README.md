# Voice Assistant - Natural Language Systems Project

A local voice assistant capable of providing weather information and managing calendar entries through natural language interaction.

## Features

- 🎤 **Automatic Speech Recognition (ASR)** - Converts spoken English to text using OpenAI Whisper
- 🔊 **Text-to-Speech (TTS)** - Converts text to spoken English 
- 🌤️ **Weather Information** - Queries weather API for forecasts
- 📅 **Calendar Management** - Full CRUD operations for calendar entries
- 💬 **Conversation Tracking** - Maintains dialogue context and history
- 🔒 **Local Processing** - All AI processing happens locally (no cloud dependencies)

## Project Structure

```
VoiceAssistant/
├── src/
│   ├── __init__.py
│   ├── asr.py                  # Automatic Speech Recognition module
│   ├── tts.py                  # Text-to-Speech module
│   ├── weather_api.py          # Weather API integration
│   ├── calendar_api.py         # Calendar API integration
│   ├── nlu.py                  # Natural Language Understanding
│   └── dialogue_manager.py     # Conversation state management
├── main.py                     # Main application
├── test_assistant.py           # Test suite
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
├── run_docker.sh              # Docker run script
└── README.md                   # This file
```

## Installation

### Local Setup

1. **Clone the repository:**
   ```bash
   cd /home/okeahda/projects/VoiceAssistant
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the assistant (text mode):**
   ```bash
   python main.py --no-voice
   ```

4. **Run the assistant (voice mode):**
   ```bash
   python main.py
   ```

### Docker Setup

1. **Build and run with Docker:**
   ```bash
   chmod +x run_docker.sh
   ./run_docker.sh
   ```

   Or manually:
   ```bash
   docker build -t voice-assistant .
   docker run -it --rm voice-assistant
   ```

2. **Using Docker Compose:**
   ```bash
   docker-compose up --build
   ```

## Usage

### Voice Mode Commands

When running in voice mode (`python main.py`), you can speak these commands:

#### Weather Commands

**Basic weather:**
- "What's the weather today in Hamburg?"
- "What's the weather in Marburg?"
- "How's the weather in Frankfurt?"

**Specific day:**
- "What will the weather be on Friday in Berlin?"
- "What's the weather tomorrow in Munich?"

**Rain queries:**
- "Will it rain in Hamburg on Saturday?"
- "Is it going to rain tomorrow?"

**Follow-up (using context):**
- First: "What's the weather in Hamburg?"
- Then: "What about in Frankfurt?" *(uses context)*

#### Calendar Commands

**Query appointments:**
- "Where is my next appointment?"
- "Show me my appointments"
- "What's my next meeting?"

**Create appointment:**
- "Add an appointment titled Team Meeting for tomorrow at 2 PM"
- "Schedule a meeting called Project Review for January 12th"
- "Create an appointment for Friday at 3 PM"

**Update appointment:**
- "Change the place for my appointment tomorrow to Room 15"
- "Update the location of my next meeting"

**Delete appointment:**
- "Delete the previously created appointment"
- "Cancel my next appointment"

**Exit:**
- "Exit" / "Quit" / "Goodbye"

**Note:** In voice mode, the system records for 5 seconds each time. Speak clearly and start speaking right away after you hear "Listening..."

### Text Mode Commands

In text mode (`python main.py --no-voice`), type the same commands as above. Examples:

- `whats the weather today in hamburg`
- `what about in frankfurt` (contextual)
- `add an appointment titled Team Meeting for tomorrow at 2 PM`
- `delete the previously created appointment`
- `exit`

### Running Tests

Test the assistant with predefined commands:

```bash
python test_assistant.py
```

## API Integration

### Weather API

**Endpoint:** `https://api.responsible-nlp.net/weather.php`

**Request:**
```bash
curl -X POST -d "place=Marburg" https://api.responsible-nlp.net/weather.php
```

**Response:**
```json
{
  "place": "Marburg",
  "forecast": [
    {
      "day": "thursday",
      "temperature": { "min": 7, "max": 15 },
      "weather": "few clouds"
    }
  ]
}
```

### Calendar API

**Create (POST):**
```bash
curl -X POST "https://api.responsible-nlp.net/calendar.php" \
  -H "Content-Type: application/json" \
  -d '{"title":"Meeting","start_time":"2025-11-03T09:00","end_time":"2025-11-03T10:00"}'
```

**List All (GET):**
```bash
curl "https://api.responsible-nlp.net/calendar.php"
```

**Get Single (GET):**
```bash
curl "https://api.responsible-nlp.net/calendar.php?id=1"
```

**Update (PUT):**
```bash
curl -X PUT "https://api.responsible-nlp.net/calendar.php?id=1" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Meeting"}'
```

**Delete (DELETE):**
```bash
curl -X DELETE "https://api.responsible-nlp.net/calendar.php?id=1"
```

## Architecture

### Modules

1. **ASR Module (`src/asr.py`):**
   - Uses OpenAI Whisper for speech recognition
   - Supports multiple model sizes (tiny, base, small, medium, large)
   - Records audio from microphone and transcribes to text

2. **TTS Module (`src/tts.py`):**
   - Provides two implementations: Coqui TTS and pyttsx3
   - Converts text responses to speech
   - Plays audio output

3. **Weather API (`src/weather_api.py`):**
   - Handles weather forecast requests
   - Supports day-specific queries
   - Rain prediction functionality

4. **Calendar API (`src/calendar_api.py`):**
   - Full CRUD operations for appointments
   - Finds next upcoming appointment
   - Formats appointment data for display

5. **NLU (`src/nlu.py`):**
   - Intent classification (weather, rain, appointments)
   - Entity extraction (location, date, time, title)
   - Date/time parsing and normalization

6. **Dialogue Manager (`src/dialogue_manager.py`):**
   - Tracks conversation history
   - Maintains context (last location, last appointment, etc.)
   - Resolves references ("there", "it", "previously created")

7. **Main Application (`main.py`):**
   - Integrates all modules
   - Implements conversation loop
   - Routes intents to appropriate handlers

## Configuration

### Command-line Arguments

- `--no-voice`: Run in text mode (no speech I/O)
- `--asr-model`: Whisper model size (tiny, base, small, medium, large)

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
WEATHER_API_URL=https://api.responsible-nlp.net/weather.php
CALENDAR_API_URL=https://api.responsible-nlp.net/calendar.php
SAMPLE_RATE=16000
CHANNELS=1
```

## Milestones

- ✅ **MS1 (14.11.2025):** Working code for ASR and TTS
- ✅ **MS2 (28.11.2025):** Working code to connect to weather and calendar API
- ✅ **MS3 (12.12.2025):** Working voice assistant
- ✅ **MS4 (30.01.2025):** Final Docker container and evaluation report

## Requirements Met

✅ System takes spoken English as input and produces spoken English as output  
✅ System keeps track of conversation history  
✅ System does not connect to external resources except weather and calendar APIs  
✅ User can request all information from weather API through spoken language  
✅ User can perform all CRUD operations on calendar API  
✅ User can refer to previous turns in conversation  

## Evaluation

The system can be evaluated on:

1. **Intent Recognition Accuracy:** How well the NLU identifies user intents
2. **Entity Extraction Accuracy:** How well dates, locations, and other entities are extracted
3. **Context Resolution:** How well the system resolves references to previous conversation
4. **API Integration:** Success rate of weather and calendar API calls
5. **End-to-End Success:** Complete task completion rate for required commands
6. **ASR Accuracy:** Word Error Rate (WER) for speech recognition
7. **Response Quality:** Relevance and completeness of system responses

## Dependencies

See [requirements.txt](requirements.txt) for complete list:

- **ASR:** openai-whisper, torch, sounddevice
- **TTS:** TTS, pyttsx3
- **APIs:** requests
- **NLU:** python-dateutil, regex
- **Audio:** pyaudio, wave, scipy

## License

See [LICENSE](LICENSE) file.

## Team

This project was developed as part of the Natural Language Systems course at the University of Marburg.

## Troubleshooting

### Common Issues

1. **Audio errors in voice mode:**
   - Use text mode: `python main.py --no-voice`
   - Or install audio libraries: `sudo apt-get install espeak espeak-ng` (Linux)

2. **Model download issues:**
   - Whisper models download automatically on first use
   - Requires internet connection for initial setup

3. **API connection errors:**
   - Verify internet connection
   - Check API endpoints are accessible

4. **Location not recognized:**
   - City names are case-insensitive ("hamburg" works)
   - Include "in [city]" in your query

## Future Improvements

- Add support for multiple languages
- Implement more sophisticated NLU with machine learning
- Add user authentication for personalized calendars
- Support for recurring appointments
- Voice activity detection for better UX
- Improved error handling and recovery
- Performance optimizations for faster response times