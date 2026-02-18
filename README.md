# AI Voice Customer Support Agent (Twilio + Gemini)

## Overview
This project is a Flask-based voice customer support agent that handles real-time phone calls through Twilio and generates responses using Google Gemini.

The agent supports:
- Natural conversational support for e-commerce queries
- Intent detection and context-aware responses via Gemini (`gemini-2.0-flash`)
- Session management across a live call
- Authentication flow for order-specific requests
- Refund initiation simulation for authenticated users
- Input safety checks using Guardrails validators with fallback checks

The repository includes Twilio webhook handlers, LLM and guardrails modules, authentication/session logic, and a dummy data store for POC testing.

## Technologies
- API / Webhooks: Flask
- Telephony: Twilio Voice + TwiML
- LLM: Google Gemini (`google-genai`)
- Safety / Validation: Guardrails AI (`guardrails`) with hub validators
- Speech utilities: Google Cloud Text-to-Speech + Whisper helpers (`speech_handler.py`)
- Utilities: `python-dotenv`, `numpy`, `sounddevice`, `soundfile`, `pydub`

## Project Structure
- `twilio_app.py`: Main Flask app and Twilio voice flow (`/incoming_call`, `/process_speech`, `/call_status`)
- `llm_handler.py`: Gemini initialization, intent detection, response generation
- `guardrails_handler.py`: Toxicity, profanity, and malicious-intent checks
- `auth_handler.py`: Order authentication flow
- `session_manager.py`: Session and conversation state
- `data_store.py`: Dummy order/customer data and refund simulation
- `.env.example`: Environment variable template
- `google-credentials.json.example`: Google service account JSON template

## Prerequisites
- Python 3.9+
- pip
- Twilio account + voice-enabled Twilio phone number
- `ngrok` (or equivalent tunnel) to expose local webhook endpoints
- Google Gemini API key
- (Optional, for local TTS helpers) Google Cloud service account JSON with TTS access

## Setup
1. Clone and enter the repository.

```bash
git clone <your-repository-url>
cd "Voice Agent POC - GL"
```

2. Create and activate a virtual environment.

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/macOS
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Install any missing runtime packages if needed (imports used by the app).

```bash
pip install twilio guardrails-ai
```

5. (Optional) Install Guardrails hub validators.

```bash
guardrails hub install hub://guardrails/toxic_language
guardrails hub install hub://guardrails/profanity_free
```

6. Create your environment file.

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/macOS
cp .env.example .env
```

7. Update `.env` with your values:
- `GEMINI_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS` (optional for `speech_handler.py` TTS use)
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`

## Running the App
1. Start the Flask app:

```bash
python twilio_app.py
```

2. Start ngrok in a separate terminal:

```bash
ngrok http 5000
```

3. In Twilio Console, set your number's voice webhook URL to:

```text
https://<your-ngrok-domain>/incoming_call
```

4. Call your Twilio number and interact with the agent.

## Test Data (POC)
Dummy orders in `data_store.py`:
- Order `123` (phone last digits: `10`)
- Order `456` (phone last digits: `25`)
- Order `789` (phone last digits: `47`)

Use these values to test authentication and order-specific flows.

## API Endpoints
- `POST /incoming_call`: Starts a new call session and greeting
- `POST /process_speech`: Processes recognized speech and generates next response
- `POST /call_status`: Receives Twilio status callbacks

## Notes
- The app is designed as a POC and uses in-memory session state.
- `data_store.py` is mock data only; replace with your real backend integrations for production.
- Keep secrets out of version control (`.env`, real credential JSON files).
