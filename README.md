# LUNA UI

React frontend for the LUNA companion project.

## Run

Frontend:

```powershell
.\run-frontend.cmd
```

Or manually:

```powershell
npm.cmd install
npm.cmd run dev
```

The UI runs on `http://127.0.0.1:5173`.

## Backend Pairing

This frontend expects the FastAPI backend from:

`C:\Users\sandh\OneDrive\Desktop\Projects\InnerVoice_Jelly`

Start it with:

```powershell
.\run-backend.cmd
```

That backend serves:

- `POST /chat`
- `POST /tts`
- `GET /wisdom`

## Notes

- Background music is served from `public/tracks`.
- The moon texture is served from `public/textures`.
- The login password is still local UI gating in `src/LoginScreen.jsx`.
