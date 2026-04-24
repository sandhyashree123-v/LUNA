# LUNA

LUNA is a public-facing companion app with:

- a React + Vite frontend at the repo root
- a FastAPI backend in `InnerVoice_Jelly`

## Local Run

Frontend:

```powershell
npm.cmd install
npm.cmd run dev
```

Backend:

```powershell
cd .\InnerVoice_Jelly
python -m pip install -r requirements.txt
python -m uvicorn backend:app --reload --host 127.0.0.1 --port 8000
```

The frontend runs on `http://127.0.0.1:5173` and talks to the backend on `http://127.0.0.1:8000`.

## Public Deployment

This repo now includes a root `Dockerfile` that:

- builds the Vite frontend
- packages it into the Python container
- serves both the UI and API from one public URL

The backend also exposes `GET /health` for hosting checks.

## Persistent Diary Storage

Diary entries can now persist in Azure Blob Storage per user account when these backend env vars are set:

```env
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER=luna-data
```

If those vars are missing, the backend falls back to local files.

## Azure

For an Azure student subscription, the cleanest setup is:

- Azure Container Apps for the public app
- Azure Storage Account (Blob Storage) for diary persistence

Detailed steps are in [AZURE_DEPLOY.md](/c:/Users/sandh/luna-ui/AZURE_DEPLOY.md).
