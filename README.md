# Video Captioning Studio

Upload an MP4 → Gemini analyzes the audio **and** visuals → get Formal,
Sarcastic, Humorous-Tech, and Humorous-Non-Tech captions, summaries, and
four color-coded captioned video versions.

This guide assumes **zero experience**. Follow the steps top to bottom, in
order, and don't skip any. The app runs entirely inside **Docker**, so you
don't need to install Python, Node, or ffmpeg on your computer at all.

## What it does

1. You upload an `.mp4` file through the web page.
2. Gemini reads the video directly (both sound and picture) and writes a
   transcript, a description of what's happening, and all four caption
   styles.
3. You pick a style you like (and optionally tweak the tone/colors).
4. ffmpeg burns the chosen captions onto the video.
5. You can watch/download the result, and see all your past videos later.

```
Upload MP4  →  Gemini (audio + visual understanding)  →  captions + summaries
                                                       →  ffmpeg burns 4 styled videos
                                                       →  everything gets saved
```

## Step 1 — Open a terminal

- **Windows:** press the Start key, type `cmd`, press Enter. This opens
  Command Prompt.
- **Mac:** press `Cmd + Space`, type `Terminal`, press Enter.
- **Linux:** press `Ctrl + Alt + T`, or open "Terminal" from your app menu.

Everything below is typed into this window.

## Step 2 — Get the project

If you already have this folder (you're reading this file from inside it),
skip to Step 3. Otherwise:

```bash
git clone <this-repo>
cd "VIDEO-CAPTIONING-STUDIO-GEMMA"
```

(Windows: same two commands, typed the same way, in Command Prompt.)

## Step 3 — About the API key (optional to change)

The app needs a Gemini API key (like a password that lets it talk to
Google's Gemini AI) to work. **This project already ships with a working
default key in `backend/.env`, so you can skip straight to Step 4** — the
app will run out of the box.

If you'd rather use your own key (recommended if you're going to use this a
lot, so you have your own free quota instead of sharing the built-in one):

1. Go to https://aistudio.google.com/apikey
2. Sign in with a Google account.
3. Click **Create API key**.
4. Copy the long string of letters/numbers it gives you.
5. Open `backend/.env` in Notepad (Windows) or any text editor (Mac/Linux),
   replace the value after `GEMINI_API_KEY=` with your own key, and save.

## Step 4 — Build

You don't need to install Docker yourself first — this step checks for it,
and installs it automatically if it's missing.

**Windows:**
```bat
build_docker.bat
```

**Mac / Linux:**
```bash
./build_docker.sh
```

What this does:
- Checks if Docker is already installed. If yes, skips straight to
  building.
- If Docker is missing, installs it for you (Windows: via `winget`; Mac:
  via Homebrew — installs Homebrew first if needed; Linux: via `apt`).
- If it just installed Docker Desktop (Windows/Mac), it will ask you to
  open Docker Desktop once from the Start menu / Applications so it can
  finish first-time setup — then run the same command again.
- Once Docker is confirmed working, it builds the app image
  (`docker compose build`). This can take a couple of minutes the first
  time — that's normal.

## Step 5 — Start and open the app

| | Windows / Mac | Linux |
| - | -------------- | ----- |
| Start | `docker compose up -d` | `sudo docker compose up -d` |
| Stop | `docker compose down` | `sudo docker compose down` |

(Linux needs `sudo` in front because Docker there requires admin rights by
default; Docker Desktop on Windows/Mac doesn't need this.)

Open **http://localhost:8000** in your web browser — one container serves
everything (web page + server together, no second port to worry about).

To stop the app, run the **Stop** command above. Your uploaded/generated
videos and database are kept safely in a Docker volume even after
stopping — the next **Start** picks up right where you left off.

## Using the app

1. **Home** — upload an `.mp4` video.
2. **Select style** — pick Formal, Sarcastic, Humorous-Tech,
   Humorous-Non-Tech, or a combined style.
3. **Personalize** — optionally adjust tone/colors.
4. **Output** — watch or download your captioned video.
5. **History** — revisit past videos any time.

## What's inside the container

- `build_docker.sh` / `build_docker.bat` — checks whether Docker is
  installed; installs it automatically if not (via `apt`, Homebrew, or
  `winget` depending on your OS), then builds the image.
- `Dockerfile` — multi-stage build: Stage 1 builds the frontend with Node,
  Stage 2 is Python + ffmpeg + the backend, with the built frontend copied
  in. You never run Node/Python/ffmpeg yourself — Docker does it inside the
  image.
- `docker-compose.yml` — one service, port `8000`, a named volume so your
  data survives restarts, and `backend/.env` passed in for the API key.
- `.dockerignore` — keeps unnecessary local files out of the image.

## Project structure

```
.
├── Dockerfile                 # builds frontend + backend into one image
├── docker-compose.yml         # runs the built image
├── backend/
│   ├── main.py                # FastAPI app & routes
│   ├── config.py              # env vars, paths, style definitions
│   ├── database.py             # SQLAlchemy engine/session
│   ├── models.py               # ORM models (VideoJob)
│   ├── gemini_client.py        # Gemini Files API + structured generation
│   ├── combined_styles.py      # combined-style tone/color logic
│   ├── media.py                 # ffmpeg caption burning
│   ├── pipeline.py              # orchestrates Gemini → ffmpeg → DB
│   ├── requirements.txt         # pinned Python dependencies
│   ├── .env.example              # template — copy this to .env
│   ├── .env                      # your real secrets, never committed
│   └── data/                      # uploads, outputs, SQLite database
└── frontend/
    ├── vite.config.js            # dev server + /api proxy to :8000
    ├── package.json               # pinned Node dependencies
    └── src/
        ├── main.jsx                 # routes + app shell
        ├── api.js                   # backend API calls
        └── pages/                    # Home, StyleSelect, Personalize, Output, Archive
```

## Backend API reference

Served at http://localhost:8000/api:

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| POST   | `/api/upload` | Upload a video, creates a job |
| GET    | `/api/combined-styles` | List available combined styles |
| POST   | `/api/generate/{job_uuid}` | Run Gemini + ffmpeg for a job |
| GET    | `/api/status/{job_uuid}` | Poll job status |
| GET    | `/api/archive` | List past jobs |
| GET    | `/api/original/{job_uuid}` | Fetch the original upload |
| GET    | `/api/video/{job_uuid}` | Fetch a captioned output video |

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `GEMINI_API_KEY` | bundled default | Gemini API key — swap for your own in `backend/.env` if you want separate quota |
| `GEMINI_MODEL` | `gemini-flash-latest` | Multimodal model used throughout — a rolling alias to Google's current Flash model, so it won't get stuck on a deprecated dated version |

Both live in `backend/.env` — that's the only file you ever need to edit.
`backend/.env.example` is just a template for reference and isn't used by
the app.

## About the built-in API key

- `backend/.env` ships with a working default key so the app runs
  immediately with no setup. Everyone who gets a copy of this project
  shares that same key/quota unless they swap in their own (Step 3).
- If you're distributing this project to a lot of people, or expect heavy
  use, it's worth having each person set their own free key so nobody hits
  a shared quota limit.
- If you ever deploy this to a public hosting service (Railway, Render,
  Fly.io, etc.), use that service's own "environment variables" / "secrets"
  settings for `GEMINI_API_KEY` rather than relying on the bundled `.env`.

## Caption colors

| Style | Color |
| ----- | ----- |
| Formal | Blue |
| Sarcastic | Red |
| Humorous-Tech | Green |
| Humorous-Non-Tech | Orange |

## Troubleshooting

- **`build_docker.bat`/`build_docker.sh` says Docker was just installed,
  run again** — this is expected the first time. Open Docker Desktop once
  (Windows/Mac) so it finishes first-time setup (whale icon appears), or
  log out/in on Linux for group permissions to apply, then re-run the
  build script.
- **"docker: command not found" / Docker Desktop not starting** — make
  sure Docker Desktop is installed and running (whale icon visible), then
  open a **new** terminal window and try again.
- **Build fails with `open //./pipe/dockerDesktopLinuxEngine: The system
  cannot find the file specified` (Windows)** — Docker is installed but the
  Docker Desktop app itself isn't open. Open **Docker Desktop** from the
  Start menu and wait until the whale icon in the system tray stops
  animating (fully started, can take up to a minute), then run
  `build_docker.bat` again.
- **`docker compose` says permission denied (Linux)** — put `sudo` in
  front of the command, as shown in Step 5's table.
- **`GEMINI_API_KEY is not set`** — this only happens if `backend/.env` is
  missing or its key got blanked out. Open `backend/.env` and make sure
  `GEMINI_API_KEY=` has a real value (paste your own from
  https://aistudio.google.com/apikey if needed), then run the Start command
  again.
- **Video stuck "processing"** — large files take longer; the app waits up
  to 5 minutes before giving up.
- **Upload rejected** — only `.mp4` files are accepted.
- **Port 8000 already in use** — stop whatever else is using it, or change
  the left-hand side of `"8000:8000"` in `docker-compose.yml` (e.g.
  `"9000:8000"`) and open that port instead.

## Where to extend

- **Timestamped captions:** ask Gemini to return `{start, end, text}`
  segments per style so captions follow the frames instead of showing one
  persistent caption.
- **Postgres:** change `DATABASE_URL` in `config.py`.
- **Real job queue:** swap the background task for Celery + Redis for
  concurrent processing under load.
- **Cloud storage:** move the `data/` folder to S3-style storage for
  deployment.
- **Auth + per-user archives.**
