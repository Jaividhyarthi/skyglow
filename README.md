# SKYGLOW — Evidence-First GitHub Repository Investigator

This package preserves the **seven original Google Stitch HTML screens** and layers a working FastAPI-backed investigation panel over them. The original static Stitch charts and figures are **illustrative**. The panel labelled **Live Evidence** is the authoritative source for actual GitHub data.

## Run on Windows (PowerShell + VS Code)

1. Install Python 3.11+ from python.org and check `py --version`.
2. Extract this ZIP. Open the `skyglow` folder in VS Code.
3. Open Terminal → New Terminal (PowerShell).
4. Run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn backend.main:app --reload --port 8000
```

If PowerShell blocks activation, run `.venv\Scripts\python.exe -m pip install -r requirements.txt` then `.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000` without activating.

5. Visit **http://127.0.0.1:8000**. Click **Live Evidence / Ask Skyglow**. Paste `https://github.com/psf/requests` and click **Investigate**.
6. Visit **http://127.0.0.1:8000/docs** to test all backend endpoints.

### Recommended credentials

Edit `.env`:

```env
GITHUB_TOKEN=your_personal_access_token
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
```

Do **not** include `.env` in Git or share it. A GitHub token is optional but increases API limits. ElevenLabs is optional for text analysis; **ElevenLabs spoken answers require a valid key**. The microphone question feature uses browser speech recognition (when supported); ElevenLabs is used for answer synthesis, not as a full ElevenLabs conversational agent.

### Optional Chrome extension

Chrome → `chrome://extensions` → enable Developer mode → Load unpacked → select `extension` directory. On a GitHub repository page, click the Skyglow extension icon. It opens the repository in your running local app.

### Test

```powershell
python -m pytest -q
```

## API

- `GET /api/health` — configuration health
- `POST /api/analyze` — `{ "url": "https://github.com/psf/requests" }`
- `GET /api/history` — saved local investigations
- `GET /api/report/{id}` — inspect report and evidence
- `POST /api/ask` — `{ "report_id": 1, "question": "Why suspicious?" }`
- `POST /api/voice` — `{ "text": "..." }` (ElevenLabs API key required)

## Important limitations / honest hackathon disclosures

- This is a **functional MVP**, not a validated fake-star detector, trained GNN, malware scanner, or full ElevenLabs Conversational AI agent.
- Live analysis uses GitHub REST repository metadata and sampled public commits/contributors/releases. It does **not** retrieve full individual-stargazer histories, claim real-world identity attribution, or assert fake-star guilt.
- Risk numbers are **unvalidated heuristics**, not calibrated probabilities. Network and code-security scores remain **N/A** when data is unavailable.
- The seven Stitch HTML pages contain **illustrative static sample data**. Use the **Live Evidence** panel for real backend results. This avoids passing sample metrics off as live evidence.
- Voice input uses the browser's SpeechRecognition API; output uses ElevenLabs TTS via server-side API. Full conversational ElevenLabs tool calling is future work.
- The extension connects to a local server at 127.0.0.1:8000.
- The app fetches public GitHub data on request; no mass scraping. Check GitHub API and hackathon prebuild rules.

## Project structure

- `frontend/stitch/` — original Stitch screens (preserved)
- `frontend/skyglow.js` / `.css` — navigation and live interaction overlay
- `backend/engine.py` — metadata, evidence heuristics, SQLite history
- `backend/main.py` — API, ElevenLabs server proxy, page server
- `extension/` — Chrome Manifest V3 popup
- `tests/` — parsing and evidence tests

## Next engineering milestones

1. Replace static Stitch report elements with data-bound React components, eliminating all illustrative content from live report screens.
2. Add a licensed labelled research dataset, true historical star events, fair baselines, and a graph model only if justified.
3. Add scoped security checks using OSV/Semgrep with explicit scan coverage.
4. Add ElevenLabs Conversational AI with authorized server-side tool calls and synchronized evidence highlighting.
5. Add user authentication, database migrations, rate limiting, and safe production deployment.
