# Azure Deployment

This project is ready for a simple Azure setup that keeps the diary content after restarts.

## Recommended Azure Services

- Azure Container Apps: runs the app publicly from the included `Dockerfile`
- Azure Storage Account: stores diary data in Blob Storage by user account
- Azure Container Registry: optional, but convenient for storing the built image

## Why This Setup

- one public URL for both frontend and backend
- diary survives restarts because it is stored in Azure instead of local files
- works well with the repo's existing Docker-based deployment path

## Backend Env Vars

Set these in your Azure container app:

```env
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_API_VERSION=2025-01-01-preview
HF_TOKEN=
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=
AZURE_SPEECH_VOICE=en-IN-NeerjaNeural
AZURE_TRANSLATOR_KEY=
AZURE_TRANSLATOR_REGION=
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
USE_AZURE_TRANSLATOR=true
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=6ZZR4JY6rOriLSDtV54M
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_CONTAINER=luna-data
LUNA_USERNAME=
LUNA_PASSWORD=
```

## Azure Storage Layout

When Azure Blob Storage is enabled, diaries are stored like this:

- `diary/<normalized-user-name>.json`

That means each user account gets its own persistent diary file.

## Portal Flow

1. Create a Storage Account.
2. In the storage account, create or reuse a blob container named `luna-data`.
3. Copy the storage account connection string from `Access keys`.
4. Build the image from this repo and push it to Azure Container Registry or another registry.
5. Create an Azure Container App from that image.
6. Turn on external ingress and use port `8000`.
7. Add the environment variables listed above.
8. Open `/health` after deploy to verify the backend sees the frontend build and Azure diary storage.

## Fastest Azure Path

If you want the quickest path in the Azure portal:

1. Create `Storage account`.
2. Copy its connection string from `Access keys`.
3. Create `Container Registry`.
4. Build and push this repo's Docker image to that registry.
5. Create `Container App` from that image.
6. Set ingress to `External` and target port to `8000`.
7. Add `AZURE_STORAGE_CONNECTION_STRING` and your existing AI/API secrets as environment variables.
8. Open `https://<your-app-url>/health` and check that `azure_diary_enabled` is `true`.

## Health Check

After deployment, this should return JSON:

```text
GET /health
```

The response includes:

- `ok`
- `frontend_ready`
- `azure_diary_enabled`

## Local Fallback

If `AZURE_STORAGE_CONNECTION_STRING` is not set, the app still works locally and stores diary data in local files.
