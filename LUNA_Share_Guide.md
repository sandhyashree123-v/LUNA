# LUNA Share Guide

## What to share

Share these two project folders:

- `luna-ui`
- `InnerVoice_Jelly`

## What NOT to share

Do not share:

- `.env`
- `venv`
- `node_modules`
- any personal API keys
- any private tokens or passwords you do not want others to use

If you are making a zip, remove these before zipping:

- `InnerVoice_Jelly\venv`
- `luna-ui\node_modules`
- `InnerVoice_Jelly\.env`

## Best folder structure for your friend

Ask your friend to keep the folders like this:

```text
Projects/
  luna-ui/
  InnerVoice_Jelly/
```

This is important because the frontend is currently built to call the backend at:

`http://127.0.0.1:8000`

and the project docs assume both folders are kept together locally.

## What your friend needs installed

- Python 3.10 or newer
- Node.js 18 or newer
- npm

## Backend setup for your friend

Inside `InnerVoice_Jelly`, your friend should:

1. Open terminal in the backend folder
2. Create a virtual environment
3. Install dependencies
4. Create a `.env` file
5. Run the backend

### Commands

```powershell
cd InnerVoice_Jelly
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Frontend setup for your friend

Inside `luna-ui`, your friend should:

```powershell
cd luna-ui
npm install
npm run dev
```

The frontend should open at:

`http://127.0.0.1:5173`

## Backend run command

From `InnerVoice_Jelly`:

```powershell
venv\Scripts\activate
python -m uvicorn backend:app --reload --host 127.0.0.1 --port 8000
```

The backend should run at:

`http://127.0.0.1:8000`

## Minimum `.env` file for your friend

Create `InnerVoice_Jelly\.env`

Use this template:

```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_here
AZURE_OPENAI_API_VERSION=2025-01-01-preview

HF_TOKEN=your_huggingface_token_here

AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=your_region_here
AZURE_SPEECH_VOICE=en-IN-NeerjaNeural

AZURE_TRANSLATOR_KEY=your_translator_key_here
AZURE_TRANSLATOR_REGION=your_translator_region_here
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
USE_AZURE_TRANSLATOR=true

ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=6ZZR4JY6rOriLSDtV54M

LUNA_USERNAME=sandy
LUNA_PASSWORD=jelly
```

## Which keys are really important

### Required for full project

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`

### Optional / fallback

- `HF_TOKEN`
- `ELEVENLABS_API_KEY`
- `AZURE_TRANSLATOR_KEY`
- `AZURE_TRANSLATOR_REGION`

## If your friend does not have your API keys

There are 3 safe options:

1. You temporarily put your own keys in `.env` and share only for demo use with someone you trust.
2. Your friend creates her own Azure/OpenAI/other service keys.
3. You record a demo video if you do not want to share keys.

## How your friend should run it

Open two terminals.

### Terminal 1

```powershell
cd InnerVoice_Jelly
venv\Scripts\activate
python -m uvicorn backend:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2

```powershell
cd luna-ui
npm install
npm run dev
```

Then open:

`http://127.0.0.1:5173`

## Login details

If you keep the current values:

- Username: `sandy`
- Password: `jelly`

Change them in `.env` if needed.

## Common issues

### Frontend opens but chat does not work

Reason:

- backend is not running
- wrong API keys
- backend failed to start

### Voice input/output does not work

Reason:

- Azure Speech keys are missing
- browser microphone permission is blocked
- speech services are not configured

### `npm install` fails

Reason:

- Node.js is not installed
- internet/dependency issue

### Python dependency errors

Reason:

- wrong Python version
- virtual environment not activated

## Easiest sharing method

The easiest method is:

1. Copy `luna-ui` and `InnerVoice_Jelly`
2. Delete `node_modules`, `venv`, and `.env`
3. Zip both folders
4. Share the zip plus this run guide
5. Send the `.env` values separately only if you trust the person

## Best judge-safe explanation

If your friend asks what to say while running it:

This is a working full-stack prototype. The frontend is built in React, the backend is built in FastAPI, mood-aware conversational logic is handled in Python, and Azure Speech is used for speech-to-text and text-to-speech. The system combines voice, chat, wisdom flow, and sonotherapy into one emotional companion experience.
