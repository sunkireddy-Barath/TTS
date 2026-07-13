# OmniVoice Studio

> Production-quality multilingual Text-to-Speech platform powered by **OmniVoice** AI.

## Features

| Feature | Description |
|---|---|
| 🎨 Voice Design | Generate speech with language, gender, age, emotion controls |
| Cross-Lingual Cloning | Clone any voice across 100+ languages |
| Emotion Engine | 10 emotions mapped to pitch/energy/style — invisible to users |
| ✨ Expression Engine | Giggle, Sigh, Question, Surprise, Dissatisfaction — auto-injected tags |
| Tag Parser | Version 3 per-sentence emotion markup |
| 100+ Languages | Grouped: English Accents · Indian Languages · Foreign Languages |

---

## Project Structure

```
Voice_Verge/
├── backend/
│ ├── main.py       ← FastAPI application (all endpoints)
│ ├── omnivoice_engine.py   ← OmniVoice model loader + inference
│ ├── emotion_engine.py   ← Emotion → pitch/energy/style mapping
│ ├── expression_engine.py  ← Expression → OmniVoice tag injection
│ ├── tag_parser.py     ← Version 3 emotion tag parser
│ ├── language_router.py  ← 100+ language catalogue + code mapping
│ ├── voice_design.py   ← Voice Design orchestration service
│ ├── voice_clone.py    ← Voice Clone orchestration service
│ └── requirements.txt
├── frontend/
│ ├── src/
│ │ ├── App.tsx
│ │ ├── main.tsx
│ │ ├── index.css     ← Design system (glassmorphism + animations)
│ │ ├── constants.ts    ← All shared data (languages, emotions, etc.)
│ │ ├── api.ts      ← API service layer (axios)
│ │ ├── components/
│ │ │ ├── Navbar.tsx
│ │ │ ├── AudioPlayer.tsx
│ │ │ ├── AudioUploader.tsx
│ │ │ ├── EmotionPicker.tsx
│ │ │ ├── ExpressionPicker.tsx
│ │ │ ├── GenderAgePicker.tsx
│ │ │ ├── LanguageSelector.tsx
│ │ │ └── VersionSwitcher.tsx
│ │ └── pages/
│ │   ├── VoiceDesignPage.tsx
│ │   └── VoiceClonePage.tsx
│ ├── package.json
│ ├── vite.config.ts
│ ├── tailwind.config.js
│ └── .env.example
└── OmniVoice_Studio.ipynb  ← Google Colab notebook (12 cells)
```

---

## Quick Start

### Option A: Google Colab (Recommended)

1. Open `OmniVoice_Studio.ipynb` in Google Colab
2. Set runtime to **GPU (T4 or better)**
3. Run all cells top-to-bottom
4. Copy the **ngrok public URL** from Cell 12
5. Set it in `frontend/.env.local`:
 ```
 VITE_API_BASE=https://xxxx.ngrok.io
 ```
6. Start the frontend locally

### Option B: Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (in a new terminal)
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Server + model status |
| GET | `/api/languages` | Grouped language catalogue |
| GET | `/api/emotions` | Available emotion labels |
| GET | `/api/expressions` | Available expression options |
| POST | `/api/voice-design` | Generate speech (voice design) |
| POST | `/api/voice-clone` | Generate speech (cross-lingual clone) |

### Voice Design — POST `/api/voice-design`

| Field | Type | Default | Description |
|---|---|---|---|
| `text` | string | required | Text to synthesise |
| `language` | string | `en-US` | Language code |
| `gender` | string | `neutral` | `male` / `female` / `neutral` |
| `age` | int | `30` | Speaker age (10–90) |
| `emotion` | string | `neutral` | Emotion label |
| `expression` | string | `none` | Expression label (v2+) |
| `version` | int | `2` | App version (1/2/3) |

### Voice Clone — POST `/api/voice-clone`

| Field | Type | Default | Description |
|---|---|---|---|
| `text` | string | required | Target text |
| `target_language` | string | `en-US` | Target language code |
| `reference_audio` | file | required | Reference voice audio (WAV/MP3/OGG/FLAC) |
| `gender` | string | `neutral` | Gender hint |
| `age` | int | `30` | Age hint |
| `emotion` | string | `neutral` | Emotion label |
| `expression` | string | `none` | Expression label (v2+) |
| `version` | int | `2` | App version |

---

## App Versions

| Version | Features |
|---|---|
| V1 | Text · Language · Gender · Age · Emotion |
| V2 | V1 + Expression dropdown (auto-injected tags) |
| V3 | Advanced: manual `<emotion>text</emotion>` tags in text |

---

## Emotion Map

| Emotion | Pitch | Energy | Style |
|---|---|---|---|
| Neutral | 0.0 st | 1.0x | neutral |
| Happy | +2.5 st | 1.35x | expressive |
| Excited | +4.5 st | 1.65x | expressive |
| Sad | -3.0 st | 0.70x | neutral |
| Angry | +1.5 st | 1.75x | expressive |
| Calm | -1.0 st | 0.80x | neutral |
| Whisper | -2.0 st | 0.45x | whisper |
| Fearful | +3.0 st | 0.65x | expressive |
| Surprised | +5.0 st | 1.50x | expressive |
| Disgusted | -1.5 st | 1.20x | neutral |

Age and gender apply additional fine corrections on top.

---

## Expression → OmniVoice Tags

| User Sees | OmniVoice Receives |
|---|---|
| Giggle | `[laughter]` |
| Sigh | `[sigh]` |
| Question | `[question-en]` |
| Surprise | `[surprise-ah]` |
| Dissatisfaction | `[dissatisfaction-hnn]` |
| Confirmation | `[confirmation-en]` |

---

## Technology Stack

- **Model**: OmniVoice (local inference)
- **Backend**: Python · FastAPI · PyTorch · soundfile
- **Frontend**: React 18 · TypeScript · Tailwind CSS · Vite · Axios
- **Deployment**: Google Colab T4 GPU · ngrok tunnel
