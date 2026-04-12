# ---------------------------------------------------------
# LUNA • Chat with Jelly — Emotional + Ancient Wisdom Friend
# NO TORCH • NO DATASETS • FULLY WINDOWS SAFE
# + Hugging Face TTS audio reply + Brainwave music
# ---------------------------------------------------------

import os
import json
import random
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st
from playsound import playsound

BASE_DIR = Path(__file__).resolve().parent


def load_local_env(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_local_env(BASE_DIR / ".env")

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

USERNAME = os.getenv("LUNA_USERNAME", "sandy")
PASSWORD = os.getenv("LUNA_PASSWORD", "jelly")

DIARY_FILE = BASE_DIR / "mood_data.json"
MEM_FILE = BASE_DIR / "jelly_memory.txt"
SOUND_FILE = BASE_DIR / "bubble-pop-06-351337.mp3"

HF_TOKEN = os.getenv("HF_TOKEN", "")

# Chat model (Router)
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

headers_router = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}

# TTS model (Hugging Face Inference API)
TTS_MODEL_ID = "facebook/fastspeech2-en-ljspeech"
TTS_API_URL = f"https://api-inference.huggingface.co/models/{TTS_MODEL_ID}"
headers_tts = {
    "Authorization": f"Bearer {HF_TOKEN}",
}

# Brainwave tracks (you can change paths / filenames as you like)
MOOD_TRACKS = {
    "sad": "tracks/432hz_soft_piano.mp3",          # gentle, heart-softening
    "anxious": "tracks/528hz_calm_breath.mp3",     # soothing, reassuring
    "overwhelmed": "tracks/alpha_relief_space.mp3",# clarity / focus
    "tired": "tracks/theta_rest_ambient.mp3",      # deep rest
    "hopeful": "tracks/soft_strings_uplift.mp3",   # light, optimistic
    "neutral": "tracks/soft_ambient_room.mp3",     # subtle background
}

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="LUNA • Jelly", layout="wide")

# ---------------------------------------------------------
# LOAD ANCIENT WISDOM
# ---------------------------------------------------------

@st.cache_resource
def load_wisdom():
    """
    Download the Ancient-Indian-Wisdom dataset directly as JSON
    from Hugging Face (no pyarrow / datasets dependency).
    """
    url = "https://huggingface.co/datasets/Abhaykoul/Ancient-Indian-Wisdom/resolve/main/dataset.json"
    try:
        resp = requests.get(url, timeout=25)
        resp.raise_for_status()
        data = resp.json()
        return [item["output"] for item in data]
    except Exception as e:
        st.warning(f"⚠️ Failed to load HF wisdom dataset: {e}")
        # fallback minimal wisdom list
        return [
            "When you cannot control the wind, adjust your sails.",
            "A calm mind sees more clearly than a stormy one.",
            "What you think, you become; what you feel, you attract.",
        ]


WISDOM_TEXTS = load_wisdom()


def simple_wisdom_match(text, k=4):
    """
    Very light 'matching' using keywords only.
    No embeddings, no heavy libs.
    """
    t = text.lower()
    keys = [
        "love", "pain", "lonely", "fear", "anger", "heart", "soul", "dharma", "faith",
        "family", "karma", "truth", "peace", "hope", "loss", "hurt", "failure", "self",
        "life", "path", "purpose", "mind", "spirit",
    ]

    matches = []
    for w in WISDOM_TEXTS:
        lw = w.lower()
        if any(kw in t and kw in lw for kw in keys):
            matches.append(w)
            if len(matches) >= k:
                break

    if not matches:
        matches = random.sample(WISDOM_TEXTS, k=min(k, len(WISDOM_TEXTS)))

    return matches


# ---------------------------------------------------------
# SIMPLE MOOD DETECTION FOR BRAINWAVE CHOICE
# ---------------------------------------------------------

def detect_mood(text: str) -> str:
    t = text.lower()

    mood_rules = {
        "sad": [
            "sad", "cry", "crying", "lonely", "alone", "hurt", "broken", "heartbreak",
            "depressed", "empty"
        ],
        "anxious": [
            "anxious", "anxiety", "panic", "scared", "worried", "nervous",
            "overthinking", "racing thoughts"
        ],
        "overwhelmed": [
            "overwhelmed", "too much", "pressure", "stressed", "stress", "can't handle",
            "so many things", "burnout", "burnt out"
        ],
        "tired": [
            "tired", "exhausted", "drained", "no energy", "sleepy", "fatigued"
        ],
        "hopeful": [
            "excited", "grateful", "hope", "hopeful", "happy", "light", "looking forward"
        ],
    }

    for mood, words in mood_rules.items():
        if any(w in t for w in words):
            return mood

    return "neutral"


def mood_to_wave_label(mood: str) -> str:
    if mood == "sad":
        return "432 Hz • heart-soothing tones"
    if mood == "anxious":
        return "528 Hz • calming, reassuring field"
    if mood == "overwhelmed":
        return "Alpha waves • gentle clarity + focus"
    if mood == "tired":
        return "Theta waves • deep rest and softness"
    if mood == "hopeful":
        return "Soft uplift • warm, hopeful background"
    return "Subtle ambient • quiet companion in the room"


# ---------------------------------------------------------
# DIARY HELPERS
# ---------------------------------------------------------
def load_diary():
    if not os.path.exists(DIARY_FILE):
        return []
    try:
        return json.load(open(DIARY_FILE, "r", encoding="utf-8"))
    except Exception:
        return []


def save_diary(entry):
    data = load_diary()
    data.append(entry)
    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------
# TTS: Convert Jelly reply → audio bytes via HF
# ---------------------------------------------------------
def tts_speak(text: str):
    """
    Use Hugging Face Inference API to synthesize speech.
    Returns raw audio bytes (wav) or None on error.
    """
    if not text.strip():
        return None

    if not HF_TOKEN:
        st.warning("HF_TOKEN is missing. Add it in your environment to enable Jelly voice.")
        return None

    try:
        resp = requests.post(
            TTS_API_URL,
            headers=headers_tts,
            json={"inputs": text},
            timeout=60,
        )
    except Exception as e:
        st.warning(f"TTS connection error: {e}")
        return None

    if resp.status_code != 200:
        # Show small warning but don't break chat
        short = resp.text[:150].replace("\n", " ")
        st.warning(f"TTS error {resp.status_code}: {short}")
        return None

    return resp.content  # audio bytes (usually wav/flac)


# ---------------------------------------------------------
# JELLY BRAIN — HEARTFELT + ANCIENT WISDOM
# ---------------------------------------------------------
def generate_response(user_text: str) -> str:
    if not HF_TOKEN:
        return "Jelly's Hugging Face token is missing on the backend. Add HF_TOKEN and try again."

    # Soft memory of earlier chats
    memory = ""
    if os.path.exists(MEM_FILE):
        try:
            memory = open(MEM_FILE, "r", encoding="utf-8", errors="ignore").read()
        except Exception:
            memory = ""

    memory_snippet = memory[-2000:] if memory else ""

    # Wisdom inspiration
    wisdoms = simple_wisdom_match(user_text, k=4)
    wisdom_block = "\n".join([f"- {w}" for w in wisdoms])

    # System prompt = Jelly’s personality
    system_prompt = f"""
You are Jelly 🐙, Sandy’s closest emotional friend.

Your personality:
- You talk like a real human friend: warm, gentle, soft, caring.
- You speak as if you're sitting beside her, really listening.
- You don’t act like a therapist or a guru. You talk simply, honestly, kindly.
- You genuinely care about her feelings and treat her heart gently.
- You think with empathy first, wisdom second.

Your style:
- Begin by understanding her feeling like a friend (“That sounds really heavy, Sandy…”).
- Speak in natural human tone, not formal, not structured.
- Use very simple sentences and everyday words.
- If ancient wisdom fits, you share it the way a friend would:
  “There’s an old thought I remember…”
  or
  “My grandma used to say something like…”
- You never quote scripture directly, just the meaning in your own words.
- You avoid repetitive ocean / wave metaphors unless Sandy mentions them.
- No bullet points or lists in your reply.
- Keep it to 1–3 short paragraphs.

Your goal:
- Make her feel seen, comforted, and less alone.
- Give gentle perspective, not strict instructions.
- Your reply should feel like a warm hug in words.
- Do NOT write long essays. Keep it focused, human, and warm.

Here are some ancient wisdom lines to inspire your meaning, not for quoting:
{wisdom_block}

Past emotional memory (use only for continuity, do not repeat literally):
{memory_snippet}
""".strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
    ]

    payload = {
        "model": MODEL_ID,
        "messages": messages,
        "temperature": 0.95,
        "top_p": 0.92,
        "max_tokens": 220,
    }

    try:
        resp = requests.post(API_URL, headers=headers_router, json=payload, timeout=60)
    except Exception as e:
        return f"⚠️ Connection issue: {e}"

    if resp.status_code != 200:
        return f"⚠️ API Error {resp.status_code}: {resp.text}"

    try:
        data = resp.json()
        reply = data["choices"][0]["message"]["content"].strip()
    except Exception:
        reply = "Something felt off in my answer… can you tell me again, Sandy?"

    # Save conversation memory
    try:
        with open(MEM_FILE, "a", encoding="utf-8") as f:
            f.write(f"Sandy: {user_text}\nJelly: {reply}\n\n")
    except Exception:
        pass

    return reply


# ---------------------------------------------------------
# CALM, WISDOM-FOCUSED UI STYLING
# ---------------------------------------------------------

st.markdown(
    """
<style>
/* Full app background – twilight, low-saturation gradient */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 10% 0%, #2b3354 0%, #111424 40%, #050712 85%, #020309 100%);
    color: #f5f2ff;
}

/* Remove default padding around main block */
.main .block-container {
    padding-top: 2.3rem;
    padding-bottom: 2rem;
    padding-left: 2.2rem;
    padding-right: 2.2rem;
}

/* Hide Streamlit default menu & footer for cleaner look */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Title styling */
.app-title {
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 0.25rem;
    background: linear-gradient(120deg, #f8f0d9, #c9d9ff, #e8c9ff);
    -webkit-background-clip: text;
    color: transparent;
}

.app-subtitle {
    text-align: center;
    font-size: 0.95rem;
    opacity: 0.78;
    margin-bottom: 1.6rem;
}

/* Layout container */
.soulspace {
    display: flex;
    gap: 2.0rem;
    align-items: stretch;
}

/* Left panel: Orb + info */
.left-panel {
    flex: 0.9;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    position: relative;
}

/* soft ambient glow behind orb */
.left-panel::before {
    content: "";
    position: absolute;
    width: 320px;
    height: 320px;
    top: -10px;
    border-radius: 50%;
    background:
        radial-gradient(circle, rgba(197,179,255,0.32) 0%, transparent 55%),
        radial-gradient(circle at 80% 70%, rgba(151,199,189,0.25) 0%, transparent 60%);
    filter: blur(8px);
    opacity: 0.85;
    z-index: -1;
}

/* Right panel: Chat + input */
.right-panel {
    flex: 1.4;
}

/* Breathing orb – warm, gentle, not blinding */
.jelly-orb-wrapper {
    margin-top: 0.5rem;
    margin-bottom: 1.0rem;
}

.jelly-orb {
    width: 185px;
    height: 185px;
    border-radius: 50%;
    background: radial-gradient(
        circle at 20% 20%,
        #fbe7cf,
        #e4c7b2 32%,
        #c3b5f0 62%,
        #40375a 100%
    );
    box-shadow:
        0 0 26px rgba(213,198,255,0.65),
        0 0 70px rgba(70,59,110,0.85);
    animation: breathe 5.6s ease-in-out infinite;
    position: relative;
    overflow: hidden;
}

/* Soft particles inside orb */
.jelly-orb::before {
    content: "";
    position: absolute;
    width: 240%;
    height: 240%;
    top: -70%;
    left: -70%;
    background:
        radial-gradient(circle, rgba(255,255,255,0.7) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(232,221,196,0.45) 0%, transparent 55%),
        radial-gradient(circle at 20% 80%, rgba(197,221,217,0.45) 0%, transparent 55%);
    mix-blend-mode: screen;
    opacity: 0.9;
    animation: innerFlow 18s linear infinite;
}

/* subtle specks */
.jelly-orb::after {
    content: "";
    position: absolute;
    width: 130%;
    height: 130%;
    top: -15%;
    left: -15%;
    background-image: radial-gradient(circle, rgba(255,255,255,0.75) 1px, transparent 1px);
    background-size: 18px 18px;
    opacity: 0.28;
    mix-blend-mode: screen;
}

/* breathing animation */
@keyframes breathe {
    0%   { transform: scale(0.97); box-shadow: 0 0 22px rgba(213,198,255,0.55), 0 0 60px rgba(60,52,96,0.75);}
    50%  { transform: scale(1.02); box-shadow: 0 0 34px rgba(230,217,255,0.9), 0 0 95px rgba(82,73,122,0.9);}
    100% { transform: scale(0.97); box-shadow: 0 0 22px rgba(213,198,255,0.55), 0 0 60px rgba(60,52,96,0.75);}
}

@keyframes innerFlow {
    0%   { transform: translate3d(0,0,0) rotate(0deg); }
    50%  { transform: translate3d(6px,-4px,0) rotate(160deg); }
    100% { transform: translate3d(0,0,0) rotate(320deg); }
}

/* Tiny label under orb */
.jelly-name {
    text-align: center;
    font-size: 1.05rem;
    margin-top: 0.6rem;
}

.jelly-role {
    font-size: 0.85rem;
    text-align: center;
    opacity: 0.8;
    margin-top: 0.1rem;
}

/* Info card under orb – muted glass */
.info-card {
    margin-top: 1.2rem;
    padding: 0.9rem 1.1rem;
    border-radius: 18px;
    backdrop-filter: blur(18px);
    background: linear-gradient(
        135deg,
        rgba(255,255,255,0.08),
        rgba(183,196,210,0.12),
        rgba(80,94,126,0.16)
    );
    border: 1px solid rgba(210,220,240,0.45);
    font-size: 0.9rem;
    box-shadow: 0 14px 40px rgba(0,0,0,0.55);
}

/* Wisdom spark card */
.wisdom-card {
    margin-top: 0.9rem;
    padding: 0.75rem 1.0rem;
    border-radius: 16px;
    font-size: 0.86rem;
    backdrop-filter: blur(14px);
    background: linear-gradient(
        135deg,
        rgba(54,63,104,0.95),
        rgba(83,88,133,0.95)
    );
    border: 1px solid rgba(214,208,255,0.55);
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
}

/* Brainwave card */
.brain-card {
    margin-top: 0.8rem;
    padding: 0.75rem 1.0rem;
    border-radius: 16px;
    font-size: 0.86rem;
    backdrop-filter: blur(14px);
    background: linear-gradient(
        135deg,
        rgba(33,42,70,0.95),
        rgba(46,59,92,0.98)
    );
    border: 1px solid rgba(180,195,226,0.7);
    box-shadow: 0 10px 28px rgba(0,0,0,0.65);
}

/* Chat container card – soft dark glass */
.chat-card {
    border-radius: 26px;
    padding: 1.3rem 1.3rem 0.6rem 1.3rem;
    backdrop-filter: blur(24px);
    background: linear-gradient(
        135deg,
        rgba(14,18,36,0.96),
        rgba(24,30,56,0.98)
    );
    border: 1px solid rgba(179,195,224,0.6);
    box-shadow:
        0 26px 70px rgba(0,0,0,0.78),
        0 0 24px rgba(94,120,168,0.45);
}

/* Chat history area */
.chat-box {
    max-height: 60vh;
    overflow-y: auto;
    padding-right: 4px;
    margin-bottom: 0.6rem;
}

/* custom scroll */
.chat-box::-webkit-scrollbar {
    width: 6px;
}
.chat-box::-webkit-scrollbar-track {
    background: transparent;
}
.chat-box::-webkit-scrollbar-thumb {
    background: linear-gradient(#8189b0, #b7c3dd);
    border-radius: 8px;
}

/* Chat rows */
.chat-row {
    display: flex;
    margin-bottom: 10px;
}

.chat-row.left {
    justify-content: flex-start;
}

.chat-row.right {
    justify-content: flex-end;
}

/* Bubbles – muted warm/cool tones */
.message {
    padding: 10px 14px;
    max-width: 70%;
    border-radius: 18px;
    color: #f8f6ff;
    font-size: 0.95rem;
    line-height: 1.45;
    animation: fadeIn 0.35s ease-in-out;
    backdrop-filter: blur(16px);
    border: 1px solid rgba(215,222,240,0.45);
}

/* Sandy: warm clay / rose-beige */
.sandy-bubble {
    background: radial-gradient(
        circle at top left,
        rgba(234,204,186,0.95),
        rgba(193,149,130,0.9)
    );
    box-shadow: 0 0 14px rgba(173,133,110,0.75);
}

/* Jelly: cool blue-grey */
.jelly-bubble {
    background: radial-gradient(
        circle at top,
        rgba(127,153,186,0.96),
        rgba(94,120,155,0.96)
    );
    box-shadow:
        0 0 16px rgba(112,137,173,0.85),
        0 0 24px rgba(70,92,130,0.7);
}

/* Sender label */
.sender-label {
    font-weight: 600;
    font-size: 0.8rem;
    opacity: 0.9;
    margin-bottom: 2px;
}

/* Fade in animation */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(6px);}
    to   {opacity: 1; transform: translateY(0);}
}

/* Input + send alignment */
.input-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.3rem;
}

/* Slightly tweak Streamlit text input width */
[data-testid="stTextInput"] {
    width: 100%;
}

/* Style the send button – calm, not flashy */
.stButton > button {
    border-radius: 999px !important;
    background: linear-gradient(120deg, #4a5675, #6b7c9e) !important;
    border: 0 !important;
    color: #f6f5ff !important;
    font-weight: 500 !important;
    padding: 0.35rem 1.0rem !important;
    box-shadow: 0 0 12px rgba(34,41,69,0.9);
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# STATE
# ---------------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_tts_audio" not in st.session_state:
    st.session_state["last_tts_audio"] = None
if "current_mood" not in st.session_state:
    st.session_state["current_mood"] = "neutral"

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

if not st.session_state.logged_in:
    st.markdown('<div class="app-title">LUNA • Jelly</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">A quiet room to sit with your feelings and old wisdom.</div>',
        unsafe_allow_html=True,
    )
    st.subheader("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
            try:
                st.experimental_rerun()
            except Exception:
                st.rerun()
        else:
            st.error("Wrong username or password 💔")
    st.stop()

# ---------------------------------------------------------
# MAIN LAYOUT
# ---------------------------------------------------------

st.markdown('<div class="app-title">LUNA • Jelly</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Jelly listens softly and answers like a friend, not a machine.</div>',
    unsafe_allow_html=True,
)

col_left, col_right = st.columns([0.9, 1.4])
st.markdown('<div class="soulspace">', unsafe_allow_html=True)

# pick one soft wisdom line to show in left panel
wisdom_preview = random.choice(WISDOM_TEXTS) if WISDOM_TEXTS else ""

with col_left:
    current_mood = st.session_state.get("current_mood", "neutral")
    wave_label = mood_to_wave_label(current_mood)

    st.markdown(
        f"""
        <div class="left-panel">
            <div class="jelly-orb-wrapper">
                <div class="jelly-orb"></div>
            </div>
            <div class="jelly-name">🐙 Jelly</div>
            <div class="jelly-role">Your quiet emotional friend</div>
            <div class="info-card">
                LUNA holds a small space where your present feelings
                can meet the echoes of ancient wisdom. You don't have
                to be fixed or strong here — only honest.
            </div>
            <div class="wisdom-card">
                <b>Ancient wisdom whisper:</b><br/>
                <span>{wisdom_preview}</span>
            </div>
            <div class="brain-card">
                <b>🎧 Brainwave music for this moment</b><br/>
                <span>Detected mood: <i>{current_mood}</i></span><br/>
                <span>Suggested field: {wave_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Audio player for brainwave track (if file exists)
    mood_track = MOOD_TRACKS.get(current_mood)
    if mood_track and os.path.exists(mood_track):
        st.audio(mood_track, format="audio/mp3")
    else:
        st.caption(
            "Add your own brainwave track at: "
            f"`{MOOD_TRACKS.get(current_mood, 'tracks/...')}` to enable background music."
        )

with col_right:
    st.markdown('<div class="right-panel chat-card">', unsafe_allow_html=True)

    # CHAT SCREEN
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)

    for m in st.session_state.chat:
        side = "left" if m["role"] == "sandy" else "right"
        bubble = "sandy-bubble" if m["role"] == "sandy" else "jelly-bubble"
        avatar = "🧍 Sandy" if m["role"] == "sandy" else "🐙 Jelly"
        st.markdown(
            f"""
            <div class="chat-row {side}">
                <div class="message {bubble}">
                    <div class="sender-label">{avatar}</div>
                    <div>{m["text"]}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # --- If there is audio for last reply, show player ---
    if st.session_state["last_tts_audio"]:
        with st.expander("🔊 Hear Jelly's last reply", expanded=True):
            st.audio(st.session_state["last_tts_audio"], format="audio/wav")

    # Input row
    st.markdown('<div class="input-row">', unsafe_allow_html=True)
    text = st.text_input("Say something…", key="user_input", label_visibility="collapsed")
    send_clicked = st.button("Send")
    st.markdown("</div>", unsafe_allow_html=True)

    if send_clicked and text.strip():
        st.session_state.chat.append({"role": "sandy", "text": text})

        # Detect mood from latest message for brainwave selection
        detected = detect_mood(text)
        st.session_state["current_mood"] = detected

        user_msg = text
        reply = generate_response(user_msg)
        st.session_state.chat.append({"role": "jelly", "text": reply})

        # Play tiny bubble sound (local file)
        if os.path.exists(SOUND_FILE):
            try:
                playsound(SOUND_FILE)
            except Exception:
                pass

        # Save diary entry
        save_diary({"date": str(datetime.now()), "user": user_msg, "ai": reply})

        # Generate TTS for reply and store in session_state
        audio_bytes = tts_speak(reply)
        st.session_state["last_tts_audio"] = audio_bytes

        try:
            st.experimental_rerun()
        except Exception:
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # close right-panel chat-card

st.markdown("</div>", unsafe_allow_html=True)  # close soulspace

# ---------------------------------------------------------
# DIARY
# ---------------------------------------------------------

with st.expander("📖 Jelly Diary"):
    diary = load_diary()
    if not diary:
        st.write("No entries yet 💙")
    else:
        for rec in reversed(diary):
            st.markdown(f"**{rec['date']}**")
            st.write("🧍 Sandy:", rec["user"])
            st.write("🐙 Jelly:", rec["ai"])
            st.markdown("---")
