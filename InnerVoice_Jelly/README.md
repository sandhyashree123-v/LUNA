# InnerVoice Jelly Backend

Primary backend for the current LUNA app, plus the older Streamlit prototype.

## First Time Setup

Install dependencies:

```powershell
.\install-backend.cmd
```

The backend auto-loads local values from `.env`.

## Run

FastAPI backend for the React app:

```powershell
.\run-backend.cmd
```

This starts the API on `http://127.0.0.1:8000`.

Optional older Streamlit prototype:

```powershell
.\run-streamlit-prototype.cmd
```

## Files

- `backend.py`: active FastAPI backend used by `luna-ui`
- `app.py`: older Streamlit prototype
- `.env`: local runtime secrets and credentials
- `.env.example`: env variable template
- `luna_memory.txt`: active long-term memory for LUNA
- `mood_data.json`: saved conversation diary

## Required Env Vars

- `HF_TOKEN`
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`
- `LUNA_USERNAME`
- `LUNA_PASSWORD`

## Frontend Pairing

The matching React frontend lives at:

`C:\Users\sandh\luna-ui`

Run it with:

```powershell
.\run-frontend.cmd
```
