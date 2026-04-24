# InnerVoice Jelly Backend

FastAPI backend for LUNA.

## Local Run

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend:app --reload --host 127.0.0.1 --port 8000
```

## Key Runtime Behavior

- serves the LUNA API
- can serve the built frontend when `dist/` is present
- exposes `GET /health`
- stores diary data in Azure Blob Storage when configured

## Azure Diary Storage

Set these env vars to make diary entries persistent across restarts:

```env
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER=luna-data
```

Diary blobs are stored per user as:

```text
diary/<normalized-user-name>.json
```

If Azure storage is not configured, the backend falls back to local files.

## Important Files

- `backend.py`: active API
- `.env.example`: backend env template
- `requirements.txt`: Python dependencies
