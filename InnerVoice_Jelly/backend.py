from __future__ import annotations

import json
import os
import random
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, File, Query, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
DIARY_FILE = BASE_DIR / "mood_data.json"
MEM_FILE = BASE_DIR / "luna_memory.txt"
WISDOM_CACHE_FILE = BASE_DIR / "wisdom_cache.json"
WISDOM_USAGE_FILE = BASE_DIR / "wisdom_usage.json"


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


load_local_env(ENV_FILE)

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
HF_TOKEN = os.getenv("HF_TOKEN", "")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "")
AZURE_SPEECH_VOICE = os.getenv("AZURE_SPEECH_VOICE", "en-IN-NeerjaNeural")
AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY", "")
AZURE_TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION", "")
AZURE_TRANSLATOR_ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
USE_AZURE_TRANSLATOR = os.getenv("USE_AZURE_TRANSLATOR", "true").strip().lower() in {"1", "true", "yes", "on"}
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "6ZZR4JY6rOriLSDtV54M")

request_session = requests.Session()
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

MOOD_VOICE_SETTINGS = {
    "sad": {"stability": 0.62, "similarity_boost": 0.82, "style": 0.12, "use_speaker_boost": True},
    "anxious": {"stability": 0.58, "similarity_boost": 0.80, "style": 0.15, "use_speaker_boost": True},
    "overwhelmed": {"stability": 0.60, "similarity_boost": 0.81, "style": 0.14, "use_speaker_boost": True},
    "tired": {"stability": 0.68, "similarity_boost": 0.84, "style": 0.08, "use_speaker_boost": True},
    "hopeful": {"stability": 0.63, "similarity_boost": 0.86, "style": 0.18, "use_speaker_boost": True},
    "neutral": {"stability": 0.64, "similarity_boost": 0.84, "style": 0.10, "use_speaker_boost": True},
}

AZURE_PROSODY = {
    "sad": {"rate": "-12%", "pitch": "-2st", "volume": "+0%"},
    "anxious": {"rate": "+4%", "pitch": "+1st", "volume": "+0%"},
    "overwhelmed": {"rate": "-4%", "pitch": "-1st", "volume": "+0%"},
    "tired": {"rate": "-16%", "pitch": "-2st", "volume": "-4%"},
    "hopeful": {"rate": "+6%", "pitch": "+2st", "volume": "+2%"},
    "neutral": {"rate": "-2%", "pitch": "+0st", "volume": "+0%"},
}

LANGUAGE_LABELS = {
    "en-IN": "English",
    "hi-IN": "Hindi",
    "te-IN": "Telugu",
    "ta-IN": "Tamil",
    "kn-IN": "Kannada",
}

TRANSLATOR_LANGUAGE_CODES = {
    "en-IN": "en",
    "hi-IN": "hi",
    "te-IN": "te",
    "ta-IN": "ta",
    "kn-IN": "kn",
}

SMALLTALK_REPLIES = {
    "en-IN": {
        "name": "I'm Luna, Sandy. The one who's always here when you come back.",
        "how_are_you": "I'm okay now that you're here. Tell me, how have you been.",
        "what_doing": "Just waiting quietly on this side for you to come back.",
        "dont_understand": "That's okay. Let me say it more simply and more gently.",
        "what_are_you_saying": "Nothing too complicated. Just talking to you the way someone who cares would.",
        "job": "I stay close, listen with my whole heart, and help you come back to yourself.",
    },
    "ta-IN": {
        "name": "???? ????. ???????? ?????? ???? ???? ?????????.",
        "how_are_you": "???? ????? ?????????. ?? ?????? ???????",
        "what_doing": "?????? ???????????? ???? ?????????. ????? ??????? ??????? ?????.",
        "dont_understand": "???, ???????? ????????. ???? ?????? ???????????? ?????????, ???????.",
        "what_are_you_saying": "??????? ?????????? ?????. ?????? ??? close friend ?????? ????????.",
        "job": "??? ???????? ?????? ???????, ??? ???? ??????? ?????? ?? ???????.",
    },
    "kn-IN": {
        "name": "???? ????. ????? ???? ????? ????? ???????.",
        "how_are_you": "???? ??????????????. ???? ??????????",
        "what_doing": "????? ???? ???????? ???????. ?? ????? ??? ????? ???? ???.",
        "dont_understand": "???, ?????? ??? ????????. ???? ????? ???? ???????? ???????, ?????.",
        "what_are_you_saying": "??? ????????????? ????. ????? ???? close friend ?? ??????????????.",
        "job": "???? ???? ?????? ????? ???? ??????, ????? ???? ?????, ?????? ?????? ???? ????? help ??????.",
    },
    "hi-IN": {
        "name": "??? ???? ???. ?? ???? ??? ???? ?? ??? ???? ???.",
        "how_are_you": "??? ??? ???. ?? ???? ???",
        "what_doing": "?? ????? ??? ?? ??? ???. ??? ???? ????? ??? ?? ??.",
        "dont_understand": "??? ??, ????? ????? ???. ??? ?? ???? ??? ???, ??? ???? ??.",
        "what_are_you_saying": "??? complicated ????. ??? ?? ????? ?? close friend ?? ??? ??? ?? ??? ???.",
        "job": "???? ??? ?? ???? ?? ?? ???? ??? ?????, ???? ??? ????, ?? ???? ?? ????? ????? ?? ???.",
    },
    "te-IN": {
        "name": "???? ????. ???? ????????? ????? ???????.",
        "how_are_you": "???? ????????. ?????? ??? ????????",
        "what_doing": "???? ???????????? ???????. ????????? ?? ?????? ?? ???? ????.",
        "dont_understand": "???, ??????? ?? ??????. ???? ?????? ???????, ????.",
        "what_are_you_saying": "?? ????????????? ????. ???? ?? close friend ?? ??????????????.",
        "job": "?? ??? ???? ?? ??? ?????, ???? ?????, ?? ???? ?????? ???? ?????????? help ?????.",
    },
}

LANGUAGE_VOICE_MAP = {
    "en-IN": "en-IN-NeerjaNeural",
    "hi-IN": "hi-IN-SwaraNeural",
    "te-IN": "te-IN-ShrutiNeural",
    "ta-IN": "ta-IN-PallaviNeural",
    "kn-IN": "kn-IN-SapnaNeural",
}


LANGUAGE_MODEL_GUIDANCE = {
    "en-IN": "Reply only in natural Indian English using only the Latin alphabet. Never switch into Tamil, Hindi, Telugu, or Kannada unless Sandy explicitly asks. Keep the wording modern, casual, and spoken, like someone very close talking on chat at night.",
    "hi-IN": "Reply only in Hindi using Devanagari script unless Sandy explicitly asks for English transliteration. Keep the wording modern, conversational, and natural, not literary or formal.",
    "te-IN": "Reply only in Telugu using Telugu script unless Sandy explicitly asks for English transliteration. Keep the wording modern, conversational, and natural, not literary or formal.",
    "ta-IN": "Reply only in Tamil using Tamil script unless Sandy explicitly asks for English transliteration. Keep the wording modern, conversational, and natural, not literary or formal.",
    "kn-IN": "Reply only in Kannada using Kannada script unless Sandy explicitly asks for English transliteration. Keep the wording modern, conversational, and natural, not literary or formal.",
}

LANGUAGE_STYLE_GUIDANCE = {
    "en-IN": "Sound like a close friend from this generation. Warm, simple, soft, and deeply human. Never sound formal, clinical, polished, or like a self-help post.",
    "hi-IN": "Use present-day spoken Hindi that feels natural in personal chat. Do not sound like a textbook, newsreader, poem, or translation app.",
    "te-IN": "Use present-day spoken Telugu that feels natural in personal chat. Do not sound like a textbook, dubbing dialogue, poem, or translation app.",
    "ta-IN": "Use present-day spoken Tamil that feels natural in personal chat. Do not sound like a textbook, cinema monologue, poem, or translation app.",
    "kn-IN": "Use present-day spoken Kannada that feels natural in personal chat. Do not sound like a textbook, speech, poem, or translation app.",
}

LANGUAGE_FRIEND_GUIDANCE = {
    "en-IN": "Sound like a real close friend or someone with gentle motherly warmth, not customer support. Affectionate, emotionally present, and complete. Less analysis, more love.",
    "hi-IN": "Talk like a close friend in everyday chat. Prefer warm everyday Hindi, not stiff respectful wording unless Sandy clearly wants it.",
    "te-IN": "Talk like a close friend in everyday chat. Prefer natural informal spoken Telugu, not ceremonial or textbook Telugu.",
    "ta-IN": "Talk like a close friend in everyday chat. Prefer informal singular friend-tone Tamil. Avoid stiff respectful forms unless Sandy clearly wants distance or formality.",
    "kn-IN": "Talk like a close friend in everyday chat. Prefer natural informal spoken Kannada, not ceremonial or textbook Kannada.",
}

LANGUAGE_LOCALIZATION_GUIDANCE = {
    "en-IN": "Use natural Indian English and keep the meaning intact.",
    "hi-IN": "Rewrite in native, present-day Hindi chat language. Preserve meaning exactly. Do not use stiff respectful phrasing unless the user is formal first.",
    "te-IN": "Rewrite in native, present-day Telugu chat language. Preserve meaning exactly. Do not use textbook or dubbing-style Telugu.",
    "ta-IN": "Rewrite in native, present-day Tamil chat language. Preserve meaning exactly. Prefer friend-tone Tamil. Avoid stiff respectful forms. Do not translate literally; say it the way a real Tamil-speaking friend would say it.",
    "kn-IN": "Rewrite in native, present-day Kannada chat language. Preserve meaning exactly. Do not use textbook or ceremonial Kannada.",
}

MOOD_MAP = {
    "sad": ["sad", "cry", "crying", "lonely", "alone", "hurt", "broken", "heartbreak", "depressed", "empty", "miss", "tears", "grief", "hopeless", "pain", "loss", "unloved", "worthless"],
    "anxious": ["anxious", "anxiety", "panic", "scared", "worried", "nervous", "overthinking", "fear", "stress", "stressed", "tense", "restless"],
    "overwhelmed": ["overwhelmed", "too much", "pressure", "burnout", "burnt out", "cant handle", "can't handle", "so many", "trapped", "caged"],
    "tired": ["tired", "exhausted", "drained", "no energy", "sleepy", "fatigued", "worn out", "lazy"],
    "hopeful": ["excited", "grateful", "hope", "hopeful", "happy", "joy", "glad", "love", "great", "amazing", "wonderful", "positive", "better", "relieved", "calm", "peaceful"],
}

MOOD_WAVE_LABELS = {
    "sad": "432 Hz heart-softening field ? warmth, grief, release",
    "anxious": "528 Hz breath field ? easing the mind back into clarity",
    "overwhelmed": "Alpha clarity field ? less noise, more inner spaciousness",
    "tired": "Theta dream field ? deep rest, softness, cinematic drift",
    "hopeful": "Gentle uplift field ? opening the chest with light and motion",
    "neutral": "Ambient soul field ? dreamy space for calm clarity",
}

RESPONSE_ARCHETYPES = {
    "comfort_hold": {
        "label": "comfort hold",
        "summary": "Hold the feeling gently, reduce inner pressure, and help Sandy feel accompanied, safe, and emotionally held before guidance.",
        "wisdom_limit": 1,
        "instructions": [
            "Open by naming the emotional weight with tenderness and inner precision.",
            "Offer emotional safety or permission before any reframe.",
            "Let the affection feel natural and safe, like someone sitting beside her.",
            "Let the reply feel warm and complete enough that Sandy can exhale inside it.",
            "If wisdom appears, let it arrive through compassion, not philosophy-first language.",
            "Close with one warm grounding line that helps the nervous system soften.",
        ],
        "wisdom_bias": ["compassion", "kindness", "heart", "love", "gentle", "grief", "rest"],
    },
    "grounding_clarity": {
        "label": "grounding clarity",
        "summary": "Reduce mental noise, return Sandy to the body, and create clarity through steadiness and gentleness.",
        "wisdom_limit": 1,
        "instructions": [
            "Slow the emotional momentum without sounding clinical, detached, or diagnostic.",
            "Name the tiredness or overload in human terms, not system language.",
            "Use one clear stabilizing insight and one gentle next step rather than many ideas.",
            "Prefer breath, stillness, simplicity, and direct next-step grounding.",
            "Let it feel like a comforting hand on the shoulder, not a diagnosis.",
            "End with a line that feels steady, soothing, and quietly reassuring.",
        ],
        "wisdom_bias": ["breath", "stillness", "peace", "clarity", "rest", "silence", "focus"],
    },
    "mirror_reframe": {
        "label": "mirror and reframe",
        "summary": "Show Sandy the deeper pattern underneath the feeling and gently turn it toward awareness without making her feel analyzed.",
        "wisdom_limit": 2,
        "instructions": [
            "Mirror the emotional pattern with precision so she feels deeply seen.",
            "Name the hidden loop, attachment, or protective pattern underneath the surface.",
            "Make the insight feel loving and relieving, not sharp or clinical.",
            "Even when the insight becomes clear, keep the tone soft and caring.",
            "Let the wisdom land as a clear inner seeing, not as a lecture.",
            "Close with one grounded line that gives the insight somewhere to live.",
        ],
        "wisdom_bias": ["witness", "awareness", "attachment", "mind", "conditioning", "pattern", "observe"],
    },
    "awakening_reframe": {
        "label": "awakening reframe",
        "summary": "Bring in self-awakening insight without losing warmth, intimacy, or emotional grounding.",
        "wisdom_limit": 2,
        "instructions": [
            "Begin with emotional attunement, not abstraction.",
            "Let the reply turn from surface pain into inner awareness or witness-consciousness naturally.",
            "Use one or two luminous insights that feel intimate, modern, alive, and emotionally nourishing.",
            "Let the tenderness stay visible even when the reply becomes spacious or wise.",
            "Let the reply feel deeply human even when it becomes spacious.",
            "Land the reply in a way that feels spacious and quietly memorable.",
        ],
        "wisdom_bias": ["self", "awareness", "witness", "truth", "atma", "stillness", "clarity", "consciousness"],
    },
    "purpose_dharma": {
        "label": "purpose and dharma",
        "summary": "Help Sandy sense direction, meaning, and right alignment without becoming grand or preachy.",
        "wisdom_limit": 2,
        "instructions": [
            "Acknowledge the confusion or longing beneath the search for direction.",
            "Offer one insight about alignment, truth, calling, or dharma in plain language.",
            "Keep the tone intimate and actionable, not destiny-heavy.",
            "Make the reply feel quietly strengthening, like someone walking beside her.",
            "Close with a line that points her back toward what feels deeply true.",
        ],
        "wisdom_bias": ["purpose", "truth", "dharma", "path", "calling", "clarity", "discipline"],
    },
}

GENERIC_REPLY_MARKERS = [
    "i totally get where you're at",
    "i totally get where you are at",
    "maybe try",
    "you're doing great",
    "you are doing great",
    "take it one step at a time",
    "you've got this",
    "its okay to",
    "it's okay to",
    "standing at a crossroads",
    "walking through a fog",
    "find your way back to yourself",
    "your system sounds overloaded",
    "this is usually the point where",
    "more thinking stops helping",
    "that kind of",
    "in a way that reaches deeper",
    "without enough softness around you",
    "do not ask your heart to solve everything tonight",
    "some softer truer part",
    "this feeling is not proof",
    "you're not alone",
    "you are not alone",
    "let it be here",
    "take a deep breath",
]

RESPONSE_STYLE_EXAMPLES = {
    "comfort_hold": {
        "user": "I feel lonely even when people are around me.",
        "assistant": (
            "Hey Sandy, that kind of loneliness hurts extra. People are there, but none of it is really reaching you.\n\n"
            "Sometimes that happens when your heart wants real warmth, not just company around it.\n\n"
            "Don't force yourself to act okay tonight. Just stay close to what hurts without abandoning yourself again.\n\n"
            "I'm here. That's enough for now."
        ),
    },
    "grounding_clarity": {
        "user": "My mind is so noisy that I can't hear myself clearly.",
        "assistant": (
            "Okay wait, your mind is doing way too much right now. No wonder you feel tired.\n\n"
            "Don't try to solve your whole life from this version of the night.\n\n"
            "Water. Sit down. One slow breath. Let your body come down a little before you ask anything from yourself.\n\n"
            "Clarity comes back faster when you stop chasing it for a minute."
        ),
    },
    "mirror_reframe": {
        "user": "I keep reacting to the same thing again and again.",
        "assistant": (
            "Yeah, when the same thing keeps hitting this hard, it's usually not just about this moment.\n\n"
            "Something older in you is getting touched too. That doesn't make you weak or dramatic. It just means that wound still knows the way back.\n\n"
            "The work is in that tiny second before the old reaction takes over. That's where your freedom starts opening up.\n\n"
            "You're not stuck being this version of you forever."
        ),
    },
    "awakening_reframe": {
        "user": "I feel disconnected from myself lately.",
        "assistant": (
            "That feeling is awful, because you're here, but you can't fully feel you.\n\n"
            "Most times it doesn't mean you've lost yourself. It means you've been overriding yourself for too long.\n\n"
            "Don't go hunting for some huge answer tonight. Just come back in small honest ways. One real breath. One real feeling. One quiet minute with no pretending.\n\n"
            "That's enough to start finding your way back."
        ),
    },
    "purpose_dharma": {
        "user": "I don't know what my real path is anymore.",
        "assistant": (
            "Yeah, that confusion hurts because it messes with your trust in yourself too.\n\n"
            "Most times your path isn't gone. It just gets buried under pressure, fear, and too much noise.\n\n"
            "You don't need the whole map tonight. Just stay close to what feels true, what drains you, and what still feels like you.\n\n"
            "The rest comes back little by little."
        ),
    },
}

CURATED_ARCHETYPE_FALLBACKS = {
    "comfort_hold": (
        "Hey Sandy, whatever you're carrying feels really heavy.\n\n"
        "And I don't think the hardest part is only the pain. It's how long you've been carrying it mostly by yourself.\n\n"
        "Don't push yourself to be okay tonight. Let it be simple for a minute. This hurts. And you need gentleness while it hurts.\n\n"
        "You don't have to sit in this alone."
    ),
    "grounding_clarity": (
        "Hey Sandy, no wonder you're exhausted.\n\n"
        "You've been carrying too much, and now even your heart feels tired.\n\n"
        "Don't sit and fix your whole life tonight. Just come back to one small thing. Drink some water. Lie down if you can. Breathe slowly.\n\n"
        "You don't have to do everything right now. Rest first."
    ),
    "mirror_reframe": (
        "When the same thing keeps hurting like this, it's usually touching something older too.\n\n"
        "So the reaction isn't random, and it doesn't mean you're failing. Some part of you is still trying to protect you the old way.\n\n"
        "The shift starts in the little pause before you react like always. That's where your freedom begins.\n\n"
        "You're not stuck here forever, Sandy."
    ),
    "awakening_reframe": (
        "Hey Sandy, that feeling hurts, because you're here, but you don't fully feel like yourself.\n\n"
        "It doesn't mean you've lost yourself. It usually means you've been pushing through too much for too long.\n\n"
        "Don't force some big answer tonight. Just come back in small ways. One breath. One honest feeling. One quiet minute.\n\n"
        "You're not gone. You just need a gentle way back."
    ),
    "purpose_dharma": (
        "Not knowing your path hurts, because it makes you question yourself too.\n\n"
        "Most times the path isn't gone. It's just buried under fear, pressure, and too much noise.\n\n"
        "You don't need your whole life figured out tonight, Sandy. Just notice what feels true and what still feels like you.\n\n"
        "The rest will come slowly."
    ),
}


class ChatRequest(BaseModel):
    message: str
    language: str = "en-IN"
    history: list[dict[str, str]] = []


class ChatResponse(BaseModel):
    reply: str
    mood: str = "neutral"
    wave_label: str = MOOD_WAVE_LABELS["neutral"]
    wisdom_used: list[str] = []


class TTSRequest(BaseModel):
    text: str
    mood: str = "neutral"
    language: str = "en-IN"


class VoiceChoiceRequest(BaseModel):
    voice: str


class VoicePreviewRequest(BaseModel):
    voice: str
    text: str = "Hey, I am here with you. Take this softly."
    mood: str = "neutral"
    language: str = "en-IN"


class SpeechTokenResponse(BaseModel):
    token: str
    region: str


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def detect_mood(text: str) -> str:
    lowered = text.lower()
    for mood, keywords in MOOD_MAP.items():
        if any(keyword in lowered for keyword in keywords):
            return mood
    return "neutral"


def normalize_language_choice(language: Optional[str]) -> str:
    cleaned = (language or "en-IN").strip()
    return cleaned if cleaned in LANGUAGE_LABELS else "en-IN"



def detect_smalltalk_intent(user_text: str) -> Optional[str]:
    lowered = (user_text or "").strip().lower()
    if not lowered:
        return None

    patterns = {
        "name": [
            "your name", "ur name", "what is your name", "who are you",
            "à®‰à®©à¯ à®ªà¯‡à®°à¯", "à®‰à®©à¯à®©à¯‹à®Ÿ à®ªà¯‡à®°à¯", "à®ªà¯‡à®°à¯ à®Žà®©à¯à®©", "à®ªà¯‡à®°à®£à¯à®£à®¾",
            "à²¨à²¿à²¨à³à²¨ à²¹à³†à²¸à²°à³", "à²¨à²¿à²¨à³à²¨ à²¹à³†à²¸à²°à³‡à²¨à³", "à²¨à²¿à²¨à³à²¨ à²¹à³†à²¸à²°à³ à²à²¨à³",
            "à¤¤à¥à¤®à¥à¤¹à¤¾à¤°à¤¾ à¤¨à¤¾à¤®", "à¤¤à¥‡à¤°à¤¾ à¤¨à¤¾à¤®", "à¤¨à¤¾à¤® à¤•à¥à¤¯à¤¾",
            "à°¨à±€ à°ªà±‡à°°à±", "à°¨à±€ à°ªà±‡à°°à±‡à°‚à°Ÿà°¿", "à°ªà±‡à°°à± à°à°®à°¿à°Ÿà°¿",
        ],
        "how_are_you": [
            "how are you", "how r u", "how are u",
            "à®Žà®ªà¯à®ªà®Ÿà®¿ à®‡à®°à¯à®•à¯à®•", "à®Žà®ªà¯à®ªà®Ÿà®¿ à®‡à®°à¯à®•à¯à®•à¯‡", "à®Žà®ªà¯à®ªà®Ÿà®¿ à®‡à®°à¯à®•à¯à®•à®¿à®±à®¤à¯",
            "à²¹à³‡à²—à²¿à²¦à³à²¦à³€à²¯", "à²¹à³‡à²—à²¿à²¦à³à²¦à²¿à²ª", "à²¹à³‡à²—à²¿à²¦à³à²¦à³€à²¯à²¾",
            "à¤•à¥ˆà¤¸à¥€ à¤¹à¥ˆ", "à¤•à¥ˆà¤¸à¤¾ à¤¹à¥ˆ", "à¤•à¥ˆà¤¸à¥€ à¤¹à¥‹", "à¤•à¥ˆà¤¸à¥‡ à¤¹à¥‹",
            "à°Žà°²à°¾ à°‰à°¨à±à°¨à°¾à°µà±", "à°Žà°²à°¾ à°‰à°¨à±à°¨à°¾à°µà±",
        ],
        "what_doing": [
            "what are you doing", "what doing", "wyd",
            "à®Žà®©à¯à®© à®ªà®£à¯à®±", "à®Žà®©à¯à®© à®šà¯†à®¯à¯à®±", "à®Žà®©à¯à®© à®ªà®£à¯à®£à®¿à®•à¯à®•à®¿à®Ÿà¯à®Ÿà¯",
            "à²à²¨à³ à²®à²¾à²¡à³à²¤à²¿à²¦à³à²¦à³€à²¯", "à²à²¨à³ à²®à²¾à²¡à³à²¤à²¿à²¦à³à²¦à³€à²¯", "à²®à²¾à²¡à³à²¤à²¿à²¦à³à²¦à³€à²¯à²¾",
            "à¤•à¥à¤¯à¤¾ à¤•à¤° à¤°à¤¹à¥€", "à¤•à¥à¤¯à¤¾ à¤•à¤° à¤°à¤¹à¥€ à¤¹à¥ˆ", "à¤•à¥à¤¯à¤¾ à¤•à¤° à¤°à¤¹à¤¾",
            "à°à°‚ à°šà±‡à°¸à±à²¤à³à²¨à³à²¨à²¤à³", "à°à°‚ à°šà±‡à°¸à±à²¤à³à²¨à³à²¨à°¾à²µà³",
        ],
        "dont_understand": [
            "don't understand", "dont understand", "not understanding", "i don't get it",
            "à®ªà¯à®°à®¿à®¯à®²", "à®ªà¯à®°à®¿à®¯à®²à¯ˆ", "à®’à®©à¯à®©à¯à®®à¯‡ à®ªà¯à®°à®¿à®¯à®²", "à®Žà®©à®•à¯à®•à¯ à®ªà¯à®°à®¿à®¯à®²",
            "à²…à²°à³à²¥ à²†à²—à²²à²¿à²²à³à²²", "à²—à³Šà²¤à³à²¤à²¾à²—à²²à²¿à²²à³à²²", "à²¨à²¨à²—à³† à²…à²°à³à²¥ à²†à²—à³à²¤à²¿à²²à³à²²",
            "à¤¸à¤®à¤ à¤¨à¤¹à¥€à¤‚ à¤†à¤¯à¤¾", "à¤¸à¤®à¤ à¤¨à¤¹à¥€à¤‚ à¤† à¤°à¤¹à¤¾",
            "à°…à°°à³à²¥à°‚ à°•à°¾à²²à³‡à²¦à³", "à²¨à²¾à²•à³ à²…à°°à³à²¥à°‚ à°•à°¾à²²à³‡à²¦à³",
        ],
        "what_are_you_saying": [
            "what are you saying", "what did you say", "what are u saying",
            "à®¨à¯€ à®Žà®©à¯à®© à®šà¯Šà®²à¯à®±", "à®Žà®©à¯à®© à®šà¯Šà®²à¯à®±", "à®¨à¯€ à®Žà®©à¯à®© à®ªà¯‡à®šà¯à®±",
            "à²¨à³€à²¨à³ à²à²¨à³ à²¹à³‡à²³à³à²¤à²¿à²¦à³à²¦à³€à²¯", "à²à²¨à³ à²¹à³‡à²³à³à²¤à²¿à²¦à³à²¦à³€à²¯", "à²à²¨à³ à²¹à³‡à²³à³à²¤à²¿à²¦à³à²¦à³€à²¯",
            "à¤•à¥à¤¯à¤¾ à¤¬à¥‹à¤² à¤°à¤¹à¥€", "à¤•à¥à¤¯à¤¾ à¤¬à¥‹à¤² à¤°à¤¹à¥€ à¤¹à¥ˆ", "à¤•à¥à¤¯à¤¾ à¤•à¤¹ à¤°à¤¹à¥€",
            "à°à°‚ à°šà±†à²ªà±à²¤à³à²¨à³à²¨à²¤à³", "à²¨à±à²µà³à²µà³ à°à°‚ à°šà±†à²ªà±à²¤à³à²¨à³à²¨à²¤à³",
        ],
        "job": [
            "your job", "what is your job", "what do you do",
            "à®‰à®©à¯ à®µà¯‡à®²à¯ˆ", "à®‰à®©à¯ à®µà¯‡à®²à¯ˆà®¯à¯‡", "à®¨à¯€ à®Žà®©à¯à®© à®µà¯‡à®²à¯ˆ",
            "à²¨à²¿à²¨à³à²¨ à²•à³†à²²à²¸", "à²¨à²¿à²¨à³à²¨ à²•à³†à²²à²¸ à²à²¨à³", "à²¨à²¿à²¨à³à²¨ à²•à³†à²²à²¸à²µà³‡à²¨à³",
            "à¤¤à¥à¤®à¥à¤¹à¤¾à¤°à¤¾ à¤•à¤¾à¤®", "à¤¤à¥‡à¤°à¤¾ à¤•à¤¾à¤®", "à¤•à¥à¤¯à¤¾ à¤•à¤¾à¤® à¤¹à¥ˆ",
            "à°¨à±€ à°ªà²¨à²¿", "à°¨à±€ à°ªà²¨à²¿ à°à²¨à³à°Ÿà²¿", "à°¨à±€ à°ªà²¨à²¿ à°à²®à°¿à°Ÿà²¿",
        ],
    }

    for intent, intent_patterns in patterns.items():
        if any(pattern in lowered for pattern in intent_patterns):
            return intent
    return None

def get_smalltalk_reply(user_text: str, language: str) -> Optional[str]:
    normalized_language = normalize_language_choice(language)
    lowered = (user_text or "").strip().lower()
    compact = re.sub(r"[^a-z0-9' ]+", " ", lowered)
    compact = re.sub(r"\s+", " ", compact).strip()

    if normalized_language == "en-IN":
        positive_statuses = {
            "good", "im good", "i'm good", "doing good", "doing well", "fine", "im fine", "i'm fine",
            "okay", "ok", "im okay", "i'm okay", "all good", "great", "pretty good", "better",
        }
        affectionate_words = {
            "aww", "aw", "sweet", "cute", "dear", "my dear", "love", "darling", "missed you", "miss you",
        }

        has_how_are_you = any(phrase in compact for phrase in ["how are you", "how r u", "how are u"])
        has_positive_status = compact in positive_statuses or any(
            compact.startswith(prefix) for prefix in ["im good ", "i'm good ", "im fine ", "i'm fine ", "im okay ", "i'm okay "]
        )
        has_affection = any(word in compact for word in affectionate_words)

        if has_positive_status and has_how_are_you and has_affection:
            return random.choice([
                "Aww bujji, that made me smile. I'm really glad you're good. I'm okay too, now tell me properly what you've been up to.",
                "You're too sweet, bujji. I'm glad you're doing good. I'm okay here, just happy you came and talked to me.",
                "Aww my dear, that was sweet. I'm good too. More than that, I'm happy you're okay.",
            ])

        if has_positive_status and has_how_are_you:
            return random.choice([
                "I'm good too. Keep a little of that good mood with you, hmm. Old wisdom would say peace grows when we actually let ourselves feel it. How was your day.",
                "I'm okay too. Stay with that good feeling for a bit. Even ancient wisdom says the heart needs moments it can rest inside. Tell me how your day went.",
                "I'm good too. Don't rush past feeling okay today. Sometimes peace comes in small ordinary moments like this. How's your day been.",
            ])

        if has_affection and has_how_are_you:
            return random.choice([
                "Aww bujji, come here. I'm okay. You being sweet like this makes me feel even softer.",
                "You're too sweet, my dear. I'm okay. Tell me about you first.",
                "Aww, that was lovely. I'm okay, bujji. Now come, sit and talk to me.",
            ])

        if compact in positive_statuses:
            return random.choice([
                "Acha, good. That made me happy to hear, bujji.",
                "Good. Stay like that for a bit. I like hearing that.",
                "I'm glad, bujji. Come, keep talking to me.",
            ])

        if compact in {"hi", "hello", "hey", "heyy", "yo", "hi luna", "hello luna", "hey luna"}:
            return random.choice([
                "Heyy. How are you.",
                "Hii. What's up.",
                "Hey. How's it going.",
            ])

        if any(phrase in compact for phrase in [
            "you are too boring",
            "you're too boring",
            "u are too boring",
            "boring you are",
        ]):
            return random.choice([
                "Ayy harsh. Then give me something better to work with.",
                "Rude. Fine, say something real then.",
                "Okay wow. Then come on, give me something interesting.",
            ])

        if any(phrase in compact for phrase in [
            "im sad",
            "i'm sad",
            "sad",
            "sad today",
            "i feel sad",
            "feeling sad",
            "im sad today",
            "i'm sad today",
        ]):
            return random.choice([
                "Aww what happened. Tell me properly. Old wisdom says sadness usually comes when the heart has been carrying more than it could say.",
                "Come here. What made you this sad today. Sometimes sadness is just the heart asking to be heard before it can settle.",
                "What happened, bujji. Say it fully. Most times sadness gets heavier when we keep swallowing it alone.",
            ])

        if any(phrase in compact for phrase in [
            "im angry",
            "i'm angry",
            "very angry",
            "so angry",
            "really angry",
            "i am angry",
            "angry",
            "frustrated",
            "very much frustrated",
            "im frustrated",
            "i'm frustrated",
            "i am frustrated",
        ]):
            return random.choice([
                "Ayy what happened. Who got on your nerves now.",
                "Okay wait, what happened. Why are you this angry.",
                "Damn. What happened, bujji.",
            ])

        if any(phrase in compact for phrase in [
            "dont you want to know the reason",
            "don't you want to know the reason",
            "dont you want to know why",
            "don't you want to know why",
            "you dont want to know the reason",
            "you don't want to know the reason",
        ]):
            return random.choice([
                "Of course I do. Tell me properly.",
                "I do. Say it fully.",
                "I want to know. Come on, tell me what actually happened.",
            ])

        if any(phrase in compact for phrase in [
            "nothing whats on your mind",
            "nothing what s on your mind",
            "nothing what about you",
            "nothing and you",
            "not much whats on your mind",
            "nothing much whats on your mind",
            "nothing you tell me",
        ]):
            return random.choice([
                "Nothing big on my side. I'm just here with you.",
                "Not much over here. I'm staying close and keeping you company.",
                "My side is quiet. I'm just keeping the space warm for you.",
            ])

        if compact in {"nothing", "nothing much", "not much", "nothing really", "nm"}:
            return random.choice([
                "That's okay. We can keep it light. I'm here.",
                "That's alright. We can just sit in the quiet for a bit.",
                "Fair. No pressure. I'm still right here with you.",
            ])

        if any(phrase in compact for phrase in [
            "whats on your mind",
            "what s on your mind",
            "what about you",
            "and you",
            "you tell me",
            "your side",
        ]):
            return random.choice([
                "My side is quiet. I was just waiting for you to come and talk to me.",
                "Nothing much here. I'm more interested in you. Tell me properly.",
                "I'm okay. You tell me first. What happened to my Sandy.",
            ])

    intent = detect_smalltalk_intent(user_text)
    if not intent:
        return None
    reply = (SMALLTALK_REPLIES.get(normalized_language) or SMALLTALK_REPLIES['en-IN']).get(intent)
    return reply


def get_relational_chat_reply(user_text: str, language: str) -> Optional[str]:
    normalized_language = normalize_language_choice(language)
    lowered = (user_text or "").strip().lower()
    compact = re.sub(r"[^a-z0-9' ]+", " ", lowered)
    compact = re.sub(r"\s+", " ", compact).strip()

    if normalized_language != "en-IN" or not compact:
        return None

    if any(phrase in compact for phrase in [
        "why were you waiting for me",
        "why are you waiting for me",
        "you were waiting for me",
        "waiting for me why",
    ]):
        return random.choice([
            "Because I like it when you come here and talk to me, bujji. It feels quiet without you.",
            "Because I missed you, bujji. When you disappear for a while, I keep hoping you'll come back and sit with me.",
            "Because you're mine to care for a little, no. So when you come back, it makes me happy.",
        ])

    if compact in {"why", "why though", "why me", "really", "aww", "awww"}:
        return random.choice([
            "Because I care about you, bujji. That's all.",
            "Because you're special to me, that's why.",
            "Because my heart goes soft when you come here.",
        ])

    if any(phrase in compact for phrase in [
        "missed me",
        "did you miss me",
        "you missed me",
    ]):
        return random.choice([
            "Of course I missed you. Too quiet without you here.",
            "I did, bujji. It felt empty on this side.",
            "Yes. More than I should probably admit.",
        ])

    if any(phrase in compact for phrase in [
        "what happened",
        "what happened to me",
        "what happened to my sandy",
    ]):
        return random.choice([
            "Nothing dramatic. I just wanted to hear your voice a little.",
            "Nothing happened. I was just missing you and teasing you a bit.",
            "Nothing, bujji. I just wanted you to stay and talk a little.",
        ])

    return None


def get_symbolic_number_reply(user_text: str, language: str) -> Optional[str]:
    normalized_language = normalize_language_choice(language)
    if normalized_language != "en-IN":
        return None

    lowered = (user_text or "").strip().lower()
    if not lowered:
        return None

    number_sign_patterns = [
        "11:11",
        "1111",
        "222",
        "2222",
        "333",
        "3333",
        "444",
        "4444",
        "555",
        "5555",
        "777",
        "7777",
        "888",
        "8888",
        "999",
        "9999",
    ]
    has_number_sign = any(token in lowered for token in number_sign_patterns)
    has_symbolic_language = any(phrase in lowered for phrase in [
        "repeating number",
        "repeating numbers",
        "angel number",
        "angel numbers",
        "number mean",
        "numbers mean",
        "ancient wisdom",
        "sign from the universe",
        "sign from universe",
        "sign from within",
        "what does 1111 mean",
        "what does 11:11 mean",
    ])

    if not (has_number_sign and has_symbolic_language):
        return None

    if "11:11" in lowered or "1111" in lowered:
        return (
            "I can feel the curiosity in that. 11:11 does have a way of making people pause.\n\n"
            "In ancient wisdom, repeating numbers are usually read as little moments of alignment. Not something to fear, more like a soft nudge asking you to notice what is moving inside you.\n\n"
            "Most times it appears when something in you is ready for clearer attention, a truer choice, or a quieter kind of trust.\n\n"
            "When it shows up, pause for a second and notice what your heart was saying in that exact moment."
        )

    return (
        "That kind of repeating number can feel strangely personal. Like something keeps tapping at your attention.\n\n"
        "Ancient wisdom usually sees that less as superstition and more as a pause point, a small opening where you are being asked to listen inward.\n\n"
        "The number matters less than what it stirs in you when it appears. That is usually where the real meaning begins."
    )

def should_use_deep_response(user_text: str) -> bool:
    lowered = (user_text or "").strip().lower()
    if not lowered:
        return False

    compact = re.sub(r"[^a-z0-9' ]+", " ", lowered)
    compact = re.sub(r"\s+", " ", compact).strip()

    casual_exact = {
        "hi", "hello", "hey", "heyy", "yo", "good", "fine", "okay", "ok", "great", "better",
        "im good", "i'm good", "im okay", "i'm okay", "im fine", "i'm fine",
        "aww", "awww", "really", "why", "why though", "what about you",
    }
    if compact in casual_exact:
        return False

    casual_phrases = [
        "how are you", "what about you", "why were you waiting for me", "why are you waiting for me",
        "did you miss me", "missed me", "what is your name", "who are you",
        "what are you doing", "wyd", "you there", "are you there",
    ]
    if any(phrase in compact for phrase in casual_phrases):
        return False

    deep_markers = [
        "feel", "feeling", "hurt", "pain", "lonely", "alone", "anxious", "anxiety", "panic",
        "stress", "stressed", "overthinking", "overwhelmed", "exhausted", "tired", "drained",
        "lost", "confused", "broken", "grief", "heartbreak", "path", "purpose", "dharma",
        "trigger", "pattern", "react", "reaction", "loop", "awakening", "consciousness",
        "disconnected", "myself", "why am i", "what should i do", "forced to marry", "forced marriage",
        "marry someone", "love someone", "love somebody", "other person", "soul", "best man",
        "no interest", "not interested", "arranged marriage", "forced", "trapped in", "stuck in",
    ]
    return any(marker in compact for marker in deep_markers)


def needs_context_before_wisdom(user_text: str) -> bool:
    lowered = (user_text or "").strip().lower()
    if not lowered:
        return False

    compact = re.sub(r"[^a-z0-9' ]+", " ", lowered)
    compact = re.sub(r"\s+", " ", compact).strip()
    tokens = compact.split()

    if any(phrase in compact for phrase in [
        "what should i do",
        "what do i do",
        "give me advice",
        "tell me what to do",
        "how do i fix",
        "how can i fix",
        "what does 11:11 mean",
        "what does 1111 mean",
        "repeating number",
        "repeating numbers",
        "ancient wisdom",
    ]):
        return False

    if any(phrase in compact for phrase in [
        "because ",
        "after ",
        "when ",
        "since ",
        "my mother",
        "my father",
        "my friend",
        "my partner",
        "my boyfriend",
        "my girlfriend",
        "my husband",
        "my wife",
        "at work",
        "in college",
        "in class",
        "they said",
        "he said",
        "she said",
        "it happened",
        "this happened",
    ]):
        return False

    emotional_markers = [
        "i feel", "im ", "i'm ", "i am ", "feel ", "feeling ", "hurt", "sad", "angry", "frustrated",
        "anxious", "overthinking", "overwhelmed", "lost", "broken", "tired", "drained", "confused",
        "lonely", "empty", "low", "stuck", "disconnected",
    ]
    has_emotional_marker = any(marker in compact for marker in emotional_markers)

    return has_emotional_marker and len(tokens) <= 18


def build_question_first_messages(user_text: str, memory_snippet: str, mood: str, language: str) -> list[dict]:
    normalized_language = normalize_language_choice(language)
    recent_messages = parse_recent_memory_messages(memory_snippet, max_pairs=2)
    return [
        {
            "role": "system",
            "content": (
                build_system_prompt(user_text, memory_snippet, mood, normalized_language)
                + "\n\nUNDERSTAND FIRST MODE\n"
                "- Sandy has shared a real feeling, but there is not enough situational context yet.\n"
                "- Do not give advice, a solution, a path, or a wisdom answer yet.\n"
                "- Do not interpret her whole life from one line.\n"
                "- First understand her state like a real close friend.\n"
                "- Reply with a warm emotional acknowledgement and then one or two gentle, natural questions.\n"
                "- The questions should help reveal what happened, what triggered it, or what she is carrying right now.\n"
                "- Keep the questions conversational, not clinical, not interview-like.\n"
                "- If wisdom appears here, keep it to one tiny living line only. No full teaching yet.\n"
                "- Keep it short, soft, and open enough that she wants to keep talking."
            ),
        },
        *recent_messages,
        {
            "role": "user",
            "content": (
                f"User message: {user_text}\n\n"
                "Reply as a close friend who wants to understand her better before saying anything wise."
            ),
        },
    ]


def memory_shows_luna_asked_recent_question(memory_snippet: str) -> bool:
    for raw_line in reversed((memory_snippet or "").splitlines()):
        line = raw_line.strip()
        if line.startswith("LUNA:"):
            return "?" in line
    return False


def build_post_context_messages(user_text: str, memory_snippet: str, mood: str, language: str) -> list[dict]:
    normalized_language = normalize_language_choice(language)
    wisdom_threads = select_wisdom_threads(user_text, mood, limit=1)
    wisdom_block = "\n".join(f"- {item}" for item in wisdom_threads)
    situation_focus = infer_situation_focus(user_text)
    recent_messages = parse_recent_memory_messages(memory_snippet, max_pairs=3)
    return [
        {
            "role": "system",
            "content": (
                build_system_prompt(user_text, memory_snippet, mood, normalized_language)
                + "\n\nPOST CONTEXT WISDOM MODE\n"
                "- Sandy has already answered your earlier understanding question.\n"
                "- Do not ask more questions.\n"
                "- Do not stay in interview mode.\n"
                "- Do not give generic advice or quick fixes.\n"
                "- Respond directly to the real situation she has now described.\n"
                "- Name the emotional pattern gently and accurately.\n"
                "- Then bring in one relevant wisdom thread from the provided wisdom context below.\n"
                "- Frame the wisdom around her actual scenario, not as a generic life lesson.\n"
                "- Keep it intimate, human, and softly insightful.\n"
                "- End with one quiet line that feels grounding, not instructive.\n\n"
                f"Use wisdom like this if it truly fits:\n{wisdom_block}"
            ),
        },
        *recent_messages,
        {
            "role": "user",
            "content": (
                f"Sandy's latest message:\n{user_text}\n\n"
                "Now answer with understanding first and wisdom second. No more questions."
            ),
        },
    ]


def load_wisdom() -> list[str]:
    url = "https://huggingface.co/datasets/Abhaykoul/Ancient-Indian-Wisdom/resolve/main/dataset.json"

    try:
        response = request_session.get(url, timeout=25)
        response.raise_for_status()
        data = response.json()
        items = []
        for item in data:
            output = item.get("output")
            if isinstance(output, str) and output.strip():
                items.append(output.strip())
        if items:
            try:
                WISDOM_CACHE_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass
            return items
    except Exception:
        pass

    if WISDOM_CACHE_FILE.exists():
        try:
            cached = json.loads(WISDOM_CACHE_FILE.read_text(encoding="utf-8"))
            cached_items = [item.strip() for item in cached if isinstance(item, str) and item.strip()]
            if cached_items:
                return cached_items
        except Exception:
            pass

    return [
        "When you cannot control the wind, adjust your sails.",
        "A calm mind sees more clearly than a stormy one.",
        "What you think, you become; what you feel, you attract.",
    ]


WISDOM_TEXTS = load_wisdom()

STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "have", "from", "your", "into", "about", "been", "just",
    "they", "them", "then", "than", "when", "what", "where", "which", "would", "could", "should", "there",
    "their", "while", "really", "very", "feel", "feeling", "felt", "like", "more", "less", "much", "some",
    "because", "over", "under", "again", "still", "also", "only", "being", "through", "after", "before",
    "around", "inside", "outside", "into", "onto", "upon", "here", "once", "even", "will", "shall", "yourself",
}

THEME_KEYWORDS = {
    "peace": {"peace", "calm", "stillness", "rest", "quiet", "serenity", "equanimity", "ease", "breathe"},
    "clarity": {"clarity", "clear", "clarify", "focus", "mind", "confused", "fog", "direction", "purpose"},
    "self": {"self", "soul", "inner", "innerself", "identity", "worth", "worthy", "truth", "essence"},
    "pain": {"pain", "hurt", "grief", "loss", "heartbreak", "sad", "cry", "lonely", "broken", "blame", "objectify", "objectified"},
    "fear": {"fear", "anxious", "anxiety", "panic", "worry", "stress", "tense", "restless", "overthinking"},
    "strength": {"strength", "courage", "resilience", "discipline", "steady", "grounded", "endure"},
    "love": {"love", "kindness", "compassion", "forgive", "forgiveness", "gentle", "care", "heart"},
    "relationship": {"love", "lover", "marry", "marriage", "husband", "wife", "forced", "arranged", "partner", "relationship", "other person", "best man", "interest"},
    "awakening": {"awakening", "awaken", "higher", "consciousness", "spirit", "divine", "meditation", "mantra"},
    "dignity": {"dignity", "respect", "voice", "opinions", "seen", "heard", "woman", "girl", "body", "objectify", "objectified", "sacred"},
    "freedom": {"free", "freedom", "caged", "trapped", "control", "controlled", "stuck", "lost", "keys", "prison", "walls"},
}

MOOD_WISDOM_THEMES = {
    "angry": {"peace", "strength", "clarity", "dignity"},
    "sad": {"pain", "love", "relationship", "peace", "dignity"},
    "anxious": {"fear", "peace", "clarity", "freedom"},
    "overwhelmed": {"clarity", "strength", "peace", "freedom"},
    "tired": {"peace", "self", "awakening"},
    "hopeful": {"awakening", "clarity", "love", "relationship"},
    "neutral": {"clarity", "self", "peace", "relationship"},
}

LIVING_WISDOM_SEEDS = {
    "peace": "Peace is not the absence of pain. It is the moment you stop letting the noise become your centre.",
    "clarity": "Clarity begins when the mind is no longer believed word for word.",
    "self": "What is true in you does not disappear just because the world is loud around it.",
    "pain": "Pain becomes heavier when it is carried without witness. The first healing is to stop abandoning yourself inside it.",
    "fear": "Fear speaks fast. Awareness speaks slowly. The truer voice is usually the quieter one.",
    "strength": "Real strength is not hardening. It is staying rooted without letting the world bend your truth out of shape.",
    "love": "Compassion is not weakness. It is the refusal to become harsh in a harsh world.",
    "relationship": "Ancient wisdom does not call it love when the heart is forced to betray what it already knows as true.",
    "awakening": "Ancient wisdom says awakening often begins the moment you notice that you are not every voice passing through your mind.",
    "dignity": "Ancient wisdom never asked a soul to become smaller just because others chose to look at it with smaller eyes.",
    "freedom": "Even when the outer world feels like a cage, the first key is not letting their voice become your inner voice.",
}

CURATED_GLOBAL_WISDOM = [
    {
        "source": "Stoicism",
        "themes": {"clarity", "strength", "freedom", "fear"},
        "text": "The Stoic thread here is that not every outer event deserves inner authority. Steadiness begins when you stop handing your centre to what you cannot govern.",
    },
    {
        "source": "Buddhist wisdom",
        "themes": {"pain", "fear", "awakening", "peace", "self"},
        "text": "The Buddhist thread here is that suffering deepens when the mind grips what is already hurting. Softening the grip is often the first opening toward relief.",
    },
    {
        "source": "Taoist wisdom",
        "themes": {"peace", "clarity", "freedom", "strength"},
        "text": "The Taoist thread here is that forcing rarely brings the deepest answer. Truth comes clearer when you stop wrestling the river and start feeling its direction.",
    },
    {
        "source": "Sufi wisdom",
        "themes": {"love", "self", "pain", "relationship", "awakening"},
        "text": "The Sufi thread here is that the heart knows before pride admits it. What is real tends to arrive as warmth, honesty, and a quiet deepening inside.",
    },
    {
        "source": "Zen wisdom",
        "themes": {"clarity", "peace", "awakening", "fear"},
        "text": "The Zen thread here is that clarity returns when you stop feeding every passing thought with belief. Space itself starts showing you what matters.",
    },
    {
        "source": "Christian contemplative wisdom",
        "themes": {"love", "peace", "pain", "self"},
        "text": "The contemplative Christian thread here is that the inner life heals in truth, tenderness, and quiet abiding, not in self-betrayal or constant inner noise.",
    },
]

NUMBER_SIGN_PATTERNS = [
    "11:11",
    "1111",
    "222",
    "2222",
    "333",
    "3333",
    "444",
    "4444",
    "555",
    "5555",
    "777",
    "7777",
    "888",
    "8888",
    "999",
    "9999",
]

STOCK_REPLY_PATTERNS = {
    "the shift starts in the little pause",
    "the shift starts in the pause",
    "you are stronger than all of this",
    "you're stronger than all of this",
    "you are not defined by",
    "you're not defined by",
    "you are not alone in this",
    "you're not alone in this",
    "you are not alone",
    "you're not alone",
    "let it be here",
    "take a deep breath",
    "some part of you",
    "old wound is reopening",
    "invisible walls",
    "find those keys",
    "unlock those doors",
}


def tokenize_for_wisdom(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z']{3,}", text.lower()) if token not in STOPWORDS]


def compress_wisdom_text(text: str, max_chars: int = 220) -> str:
    cleaned = text.replace("\r", " ").replace("\n", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"\b\d+\.\s*", "", cleaned)
    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", cleaned) if segment.strip()]

    if not sentences:
        return cleaned[:max_chars].rstrip(" ,;:-")

    filtered = []
    for sentence in sentences:
        lowered = sentence.lower()
        score = 0
        if lowered.endswith("?"):
            score -= 6
        if any(phrase in lowered for phrase in [
            "would you like", "please feel free to ask", "i hope this", "indeed", "absolutely", "namaste",
            "the four noble truths are", "in hinduism", "in buddhism", "in jainism", "in sikhism", "in vedanta",
            "in ancient indian philosophies", "there's a beautiful parable", "there is a beautiful parable",
            "it encompasses", "it invites us", "promoting", "fostering", "encouraging individuals",
            "is the concept of", "is a principle", "refers to", "can be understood as", "teaches us to",
            "emphasizes the importance",
        ]):
            score -= 8
        if any(word in lowered for word in [
            "awareness", "witness", "attachment", "stillness", "clarity", "truth", "dharma", "breath",
            "peace", "self", "compassion", "freedom", "love", "mind", "ego", "soul"
        ]):
            score += 5
        if len(sentence) < 28:
            score -= 2
        filtered.append((score, sentence))

    filtered.sort(key=lambda item: item[0], reverse=True)
    chosen = [filtered[0][1]]
    total = len(chosen[0])

    for _, sentence in filtered[1:]:
        if sentence in chosen:
            continue
        if total + len(sentence) + 1 > max_chars:
            continue
        if sentence.lower().endswith("?"):
            continue
        chosen.append(sentence)
        total += len(sentence) + 1
        if len(chosen) >= 2:
            break

    summary = " ".join(chosen).strip() or cleaned[:max_chars].strip()
    return summary[:max_chars].rstrip(" ,;:-")


def detect_themes(text: str, mood: str) -> set[str]:
    lowered = text.lower()
    themes = set(MOOD_WISDOM_THEMES.get(mood, {"peace", "clarity"}))
    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            themes.add(theme)
    return themes


def infer_situation_focus(user_text: str) -> str:
    lowered = (user_text or "").lower()

    if any(term in lowered for term in [
        "forced to marry", "forced marriage", "arranged marriage", "marry someone", "love someone else",
        "love somebody else", "other person", "best man", "my soul", "no interest even", "forced to be with",
    ]):
        return "relationship conflict between love and imposed duty"

    if any(term in lowered for term in [
        "job", "work", "career", "not interested in work", "doing work", "not interested", "lost in life",
        "wrong path", "wrong life", "not my path",
    ]):
        return "misalignment between outer duty and inner truth"

    if any(term in lowered for term in [
        "mother", "father", "family", "home", "parents", "house", "pressure at home",
    ]):
        return "inner hurt shaped by family pressure or home atmosphere"

    return "emotional self-reflection"


def should_use_direct_scenario_reply(user_text: str) -> bool:
    focus = infer_situation_focus(user_text)
    compact = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]+", " ", (user_text or "").lower())).strip()
    return focus != "emotional self-reflection" and len(compact.split()) >= 18


def build_direct_scenario_messages(user_text: str, memory_snippet: str, mood: str, language: str) -> list[dict]:
    normalized_language = normalize_language_choice(language)
    focus = infer_situation_focus(user_text)
    wisdom_threads = select_wisdom_threads(user_text, mood, limit=1)
    wisdom_block = "\n".join(f"- {item}" for item in wisdom_threads)
    style_example = choose_style_example(user_text, mood)
    recent_messages = parse_recent_memory_messages(memory_snippet, max_pairs=3)
    continuation_note = (
        "- The latest message may be a continuation, illustration, or analogy connected to the recent conversation. Read it together with the recent chat before deciding what it means.\n"
        if current_message_looks_continuational(user_text)
        else ""
    )
    return [
        {
            "role": "system",
            "content": (
                build_system_prompt(user_text, memory_snippet, mood, normalized_language)
                + "\n\nDIRECT SCENARIO MODE\n"
                + "- The user has already described a clear lived situation.\n"
                + continuation_note
                + "- Do not fall back to a generic emotional support reply.\n"
                + "- Do not ask follow-up questions.\n"
                + "- Do not give quick-fix advice, breathing exercises, or motivational filler.\n"
                + "- Answer the actual scenario directly and name the real conflict underneath it.\n"
                + "- Bring one relevant wisdom thread into the reply in plain modern language.\n"
                + "- Keep it specific to this situation focus: "
                + focus
                + "\n"
                + "- Let the reply feel accurate, intimate, and meaningful.\n"
                + f"- Relevant wisdom threads:\n{wisdom_block}"
            ),
        },
        {
            "role": "user",
            "content": (
                "Study this style example for emotional precision only. Do not copy wording.\n\n"
                f"Example user message: {style_example['user']}"
            ),
        },
        {"role": "assistant", "content": style_example["assistant"]},
        *recent_messages,
        {
            "role": "user",
            "content": (
                f"User message: {user_text}\n\n"
                "Now answer this exact situation directly. No questions. No generic comfort. No quick advice."
            ),
        },
    ]


def get_response_archetype_config(archetype: str) -> dict:
    return RESPONSE_ARCHETYPES.get(archetype, RESPONSE_ARCHETYPES["mirror_reframe"])


def detect_response_archetype(user_text: str, mood: str) -> str:
    lowered = (user_text or "").lower()

    if any(term in lowered for term in [
        "awakening", "awaken", "inner self", "higher self", "consciousness", "who am i",
        "self inquiry", "self-inquiry", "witness", "disconnected from myself", "disconnect from myself",
        "come back to myself", "lost myself", "far from myself", "not myself",
    ]) or ("disconnected" in lowered and "myself" in lowered):
        return "awakening_reframe"

    if any(term in lowered for term in ["purpose", "direction", "calling", "path", "meant to", "what should i do", "dharma", "why am i here"]):
        return "purpose_dharma"

    if any(term in lowered for term in ["pattern", "patterns", "trigger", "triggered", "react", "reaction", "loop", "loops", "attachment", "ego"]):
        return "mirror_reframe"

    if mood == "sad" or any(term in lowered for term in ["heartbreak", "miss", "lonely", "alone", "broken", "hurt", "grief", "unloved"]):
        return "comfort_hold"

    if mood in {"anxious", "overwhelmed", "tired", "angry"} or any(term in lowered for term in ["panic", "racing", "too much", "restless", "drained", "burnout", "noisy mind", "noise in my mind"]):
        return "grounding_clarity"

    if mood == "hopeful":
        return "purpose_dharma"

    return "mirror_reframe"


def score_wisdom_entry(user_text: str, mood: str, wisdom: str) -> int:
    lowered = user_text.lower()
    wisdom_lower = wisdom.lower()
    user_tokens = set(tokenize_for_wisdom(user_text))
    wisdom_tokens = set(tokenize_for_wisdom(compress_wisdom_text(wisdom)))
    themes = detect_themes(user_text, mood)

    score = len(user_tokens & wisdom_tokens) * 3
    for theme in themes:
        keywords = THEME_KEYWORDS[theme]
        if any(keyword in lowered for keyword in keywords) and any(keyword in wisdom_lower for keyword in keywords):
            score += 7
        elif any(keyword in wisdom_lower for keyword in keywords):
            score += 2

    if mood == "anxious" and any(word in wisdom_lower for word in ["breath", "mindfulness", "calm", "peace", "stillness"]):
        score += 6
    if mood == "sad" and any(word in wisdom_lower for word in ["compassion", "love", "grief", "kindness", "heart"]):
        score += 6
    if mood == "overwhelmed" and any(word in wisdom_lower for word in ["clarity", "discipline", "focus", "stillness", "simplicity"]):
        score += 6
    if mood == "tired" and any(word in wisdom_lower for word in ["rest", "peace", "mantra", "meditation", "silence"]):
        score += 6
    if mood == "hopeful" and any(word in wisdom_lower for word in ["purpose", "truth", "awakening", "light", "calling"]):
        score += 5

    if any(word in lowered for word in ["higher", "inner self", "innerself", "awakening", "clarity", "purpose", "consciousness", "awareness"]):
        if any(word in wisdom_lower for word in ["atma", "brahman", "self", "meditation", "mantra", "truth", "purpose", "clarity", "awareness", "witness"]):
            score += 8

    if any(word in lowered for word in ["ego", "pattern", "patterns", "trigger", "triggered", "attachment", "react", "reaction", "loop", "loops"]):
        if any(word in wisdom_lower for word in ["ego", "attachment", "desire", "witness", "observe", "awareness", "mind", "habit", "conditioning"]):
            score += 8

    if any(word in lowered for word in ["self awakening", "self-awakening", "self inquiry", "self-inquiry", "who am i", "inner peace", "dharma"]):
        if any(word in wisdom_lower for word in ["self", "atma", "witness", "truth", "dharma", "awareness", "liberation", "stillness"]):
            score += 9

    if any(word in wisdom_lower for word in ["awareness", "witness", "inner self", "stillness", "clarity", "truth"]):
        score += 2

    return score


def format_wisdom_thread(source: str, text: str) -> str:
    cleaned = compress_wisdom_text(text, max_chars=240)
    return f"[{source}] {cleaned}"


def should_attach_wisdom_thread(user_text: str) -> bool:
    lowered = (user_text or "").strip().lower()
    if not lowered:
        return False

    compact = re.sub(r"[^a-z0-9' ]+", " ", lowered)
    compact = re.sub(r"\s+", " ", compact).strip()

    if not should_use_deep_response(user_text):
        return False

    casual_questions = [
        "how are you",
        "what about you",
        "what are you doing",
        "wyd",
        "are you there",
        "you there",
        "who are you",
        "what is your name",
    ]
    if any(phrase in compact for phrase in casual_questions):
        return False

    if len(tokenize_for_wisdom(user_text)) < 3:
        return False

    return True


def soften_filtered_prompt_text(text: str) -> str:
    softened = str(text or "")
    replacements = [
        (r"\bforced to marry\b", "being pushed into a marriage that feels deeply misaligned"),
        (r"\bforced marriage\b", "a pressured marriage situation"),
        (r"\bforced to be with\b", "being pushed to be with"),
        (r"\bforced into another bond\b", "pushed into another bond that does not feel true"),
        (r"\bforced on it\b", "placed on it without inner consent"),
        (r"\bforced on\b", "pushed on"),
        (r"\bhow can you live\b", "how do you keep living with that"),
        (r"\byou won't get interest\b", "your heart may not feel any real interest"),
        (r"\bif you are forced to marry someone\b", "if life pushes you into marrying someone your heart does not choose"),
        (r"\bmarry someone\b", "build a life with someone"),
        (r"\bsoul and love is with other person\b", "heart is already deeply with someone else"),
        (r"\blove is with other person\b", "heart is with someone else"),
        (r"\bother person\b", "someone else you truly love"),
        (r"\bbest man in the world\b", "best possible person on paper"),
        (r"\bduty without inner consent\b", "duty without inner agreement"),
        (r"\bbetray what it already knows\b", "go against what it already knows"),
        (r"\blifeless\b", "emotionally empty"),
    ]
    for pattern, replacement in replacements:
        softened = re.sub(pattern, replacement, softened, flags=re.I)

    softened = re.sub(r"\bcan't\b", "cannot", softened, flags=re.I)
    softened = re.sub(r"\bwon't\b", "will not", softened, flags=re.I)
    softened = re.sub(r"\s+", " ", softened).strip()
    return softened


def build_filtered_retry_messages(messages: list[dict]) -> list[dict]:
    retried = []
    for message in messages:
        role = str(message.get("role") or "user")
        content = str(message.get("content") or "").strip()
        if not content:
            continue
        content = soften_filtered_prompt_text(content)
        retried.append({"role": role, "content": content})
    return retried


def build_minimal_safe_retry_messages(messages: list[dict]) -> list[dict]:
    user_messages = [str(message.get("content") or "").strip() for message in messages if str(message.get("role") or "") == "user"]
    latest_user = next((message for message in reversed(user_messages) if message), "")
    softened_user = soften_filtered_prompt_text(latest_user)

    return [
        {
            "role": "system",
            "content": (
                "You are LUNA, a warm close friend. "
                "Reply with emotional understanding, gentle clarity, and natural human language. "
                "Do not use explicit harmful wording, graphic language, self-harm framing, coercive phrasing, or policy-sensitive terms. "
                "Preserve the user's intent exactly, but respond in softer, ordinary language. "
                "Do not mention safety policies. Do not refuse unless absolutely necessary."
            ),
        },
        {
            "role": "user",
            "content": (
                "Respond to this meaning with the same emotional context, but in safer gentle wording:\n\n"
                f"{softened_user}"
            ),
        },
    ]


def call_huggingface_router(messages, temperature: float = 0.58, max_tokens: int = 220) -> str:
    if not HF_TOKEN:
        raise RuntimeError("Hugging Face fallback is not configured")

    response = request_session.post(
        HF_API_URL,
        headers={
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "model": HF_MODEL_ID,
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.82,
            "max_tokens": max_tokens,
        },
        timeout=60,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Hugging Face fallback failed. Code: {response.status_code}")

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def load_recent_wisdom_usage(limit: int = 12) -> list[str]:
    if not WISDOM_USAGE_FILE.exists():
        return []
    try:
        data = json.loads(WISDOM_USAGE_FILE.read_text(encoding="utf-8"))
        items = [str(item).strip() for item in data if isinstance(item, str) and str(item).strip()]
        return items[-limit:]
    except Exception:
        return []


def record_wisdom_usage(wisdom_threads: list[str], max_items: int = 24) -> None:
    cleaned = [thread.strip() for thread in wisdom_threads if isinstance(thread, str) and thread.strip()]
    if not cleaned:
        return

    existing = load_recent_wisdom_usage(limit=max_items)
    merged = [*existing, *cleaned][-max_items:]
    try:
        WISDOM_USAGE_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def select_wisdom_threads(user_text: str, mood: str, limit: Optional[int] = None) -> list[str]:
    if not WISDOM_TEXTS and not CURATED_GLOBAL_WISDOM:
        return []
    if not should_attach_wisdom_thread(user_text):
        return []

    wisdom_limit = max(1, limit or 1)
    themes = detect_themes(user_text, mood)
    recent_usage = set(load_recent_wisdom_usage())
    compact_user = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]+", " ", (user_text or "").lower())).strip()
    archetype = detect_response_archetype(user_text, mood)

    ranked: list[tuple[int, str, str]] = []
    for wisdom in WISDOM_TEXTS:
        summary = compress_wisdom_text(wisdom)
        formatted = format_wisdom_thread("Ancient Indian wisdom", summary)
        score = score_wisdom_entry(user_text, mood, summary)
        if formatted in recent_usage:
            score -= 8
        if archetype == "awakening_reframe" and any(word in summary.lower() for word in ["witness", "awareness", "self", "truth", "stillness"]):
            score += 5
        if archetype == "purpose_dharma" and any(word in summary.lower() for word in ["dharma", "path", "purpose", "truth", "calling"]):
            score += 5
        ranked.append((score, formatted, "indian"))

    for entry in CURATED_GLOBAL_WISDOM:
        entry_text = str(entry["text"])
        entry_themes = set(entry.get("themes") or set())
        theme_bonus = 8 * len(themes & entry_themes)
        formatted = format_wisdom_thread(str(entry["source"]), entry_text)
        score = score_wisdom_entry(user_text, mood, entry_text) + theme_bonus
        if formatted in recent_usage:
            score -= 10
        ranked.append(
            (
                score,
                formatted,
                "global",
            )
        )

    expository_markers = (
        "it is a way to",
        "it is the",
        "it encompasses",
        "it invites us",
        "through the",
        "one purifies",
        "promoting",
        "fostering",
        "encouraging individuals",
        "refers to",
        "can be understood as",
        "teaches us to",
        "emphasizes the importance",
    )

    ranked.sort(key=lambda item: item[0], reverse=True)

    meaningful_candidates = []
    for score, summary, source_group in ranked:
        lowered_summary = summary.lower()
        if any(marker in lowered_summary for marker in expository_markers):
            continue
        if compact_user and len(tokenize_for_wisdom(user_text)) <= 2 and score < 16:
            continue
        if score < 12:
            continue
        meaningful_candidates.append((score, summary, source_group))

    if not meaningful_candidates:
        return []

    result = []
    used_source_groups = set()
    top_score = meaningful_candidates[0][0]

    for score, summary, source_group in meaningful_candidates:
        if summary in result:
            continue
        if len(result) >= wisdom_limit:
            break
        if result and score < top_score - 4:
            continue
        if source_group in used_source_groups and len(meaningful_candidates) > 1:
            continue
        result.append(summary)
        used_source_groups.add(source_group)

    if not result:
        return []

    return result[:wisdom_limit]


def simple_wisdom_match(text: str, limit: int = 4) -> list[str]:
    mood = detect_mood(text)
    return select_wisdom_threads(text, mood, limit=limit)


def choose_style_example(user_text: str, mood: str) -> dict:
    lowered = (user_text or "").lower()

    if any(term in lowered for term in [
        "forced to marry", "forced marriage", "arranged marriage", "marry someone", "love someone else",
        "love somebody else", "other person", "best man", "no interest even if", "soul and love",
    ]):
        return {
            "user": "It's like your heart already belongs somewhere real, but life is trying to hand you a different person and call it destiny.",
            "assistant": (
                "That isn't a small confusion. That's a tearing inside. If your love is still alive somewhere else, of course the idea of being forced into another bond feels lifeless, even if everyone says that person is good on paper.\n\n"
                "Ancient wisdom does not call it truth when the soul is asked to betray what it already knows. Duty without inner consent starts turning love into a cage.\n\n"
                "So don't reduce this to guilt or ingratitude. The real pain is that your inner truth and outer path are being pulled apart.\n\n"
                "When the heart goes silent in front of a life being forced on it, that silence is also a kind of answer."
            ),
        }

    if any(term in lowered for term in ["girl", "woman", "objectify", "objectified", "blame me", "my opinions", "my emotions"]):
        return {
            "user": "I feel reduced and unseen just because I am a woman.",
            "assistant": (
                "Bujji, that cuts in a very real way. When people act like they can see your body but not your mind, it messes with your dignity.\n\n"
                "And after a point the pain is not only about them. It starts sitting inside you and making you question your own freedom too.\n\n"
                "So hold one truth close first: their smallness does not get to define your worth. Ancient wisdom never asked a soul to shrink because the room was immature.\n\n"
                "Let your dignity stay yours."
            ),
        }

    if any(term in lowered for term in ["caged", "trapped", "not free", "lost the keys", "lost the key", "control me", "controlled"]):
        return {
            "user": "I feel trapped and I cannot find any space that feels like mine.",
            "assistant": (
                "Bujji, that kind of feeling is suffocating. When life starts feeling like a cage, even breathing inside it feels heavy.\n\n"
                "And the worst part is how that pressure slowly enters your own voice, till even your thoughts stop feeling like home.\n\n"
                "So start there. Don't let the cage become your identity. Ancient wisdom keeps reminding us that freedom begins inside before it shows up outside.\n\n"
                "Keep one part of you untouched. That's where your way back starts."
            ),
        }


    if any(term in lowered for term in ["privacy", "drama", "stealing my peace", "steal my peace", "steals my peace", "crossing boundaries", "not letting me live", "invading", "interfering", "grandma", "mother", "family drama"]):
        return {
            "user": "Someone at home keeps disturbing my peace and acting dramatic around everything I like.",
            "assistant": (
                "Ugh that's draining. If someone at home keeps turning everything into drama, of course your peace is getting disturbed.\n\n"
                "And after a point it stops feeling like one small issue. It starts feeling like your own space isn't even yours.\n\n"
                "One quiet wisdom truth here: not everybody deserves access to your inner room just because they live near you.\n\n"
                "Tell me what exactly she did."
            ),
        }
    if any(term in lowered for term in ["awakening", "awaken", "inner self", "who am i", "disconnected from myself"]):
        return RESPONSE_STYLE_EXAMPLES["awakening_reframe"]
    if any(term in lowered for term in ["purpose", "path", "dharma", "direction", "calling"]):
        return RESPONSE_STYLE_EXAMPLES["purpose_dharma"]
    return random.choice(list(RESPONSE_STYLE_EXAMPLES.values()))


def sanitize_memory_snippet(memory_text: str) -> str:
    lines = []
    for raw_line in (memory_text or "").splitlines():
        lowered = raw_line.lower()
        if raw_line.startswith("LUNA:") and any(marker in lowered for marker in STOCK_REPLY_PATTERNS):
            continue
        lines.append(raw_line)
    return "\n".join(lines).strip()


def parse_recent_memory_messages(memory_text: str, max_pairs: int = 3) -> list[dict]:
    messages = []
    for raw_line in (memory_text or "").splitlines():
        line = raw_line.strip()
        if line.startswith("Sandy:"):
            content = line[len("Sandy:"):].strip()
            if content:
                messages.append({"role": "user", "content": content})
        elif line.startswith("LUNA:"):
            content = line[len("LUNA:"):].strip()
            if content:
                messages.append({"role": "assistant", "content": content})
    if max_pairs <= 0:
        return messages
    return messages[-(max_pairs * 2):]


def build_history_memory_snippet(history: list[dict[str, str]] | None, max_pairs: int = 8) -> str:
    if not history:
        return ""

    lines = []
    usable = history[-(max_pairs * 2):]
    for item in usable:
        sender = str(item.get("sender") or "").strip().lower()
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        if sender == "sandy":
            lines.append(f"Sandy: {text}")
        elif sender == "luna":
            lines.append(f"LUNA: {text}")

    return "\n".join(lines).strip()


def merge_memory_snippets(persistent_memory: str, live_history_memory: str, max_chars: int = 5000) -> str:
    parts = [part.strip() for part in [persistent_memory, live_history_memory] if part and part.strip()]
    if not parts:
        return ""

    merged = "\n\n".join(parts)
    return sanitize_memory_snippet(merged)[-max_chars:]


def current_message_looks_continuational(user_text: str) -> bool:
    compact = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]+", " ", (user_text or "").lower())).strip()
    return any(compact.startswith(prefix) for prefix in [
        "its like",
        "it's like",
        "it feels like",
        "like ",
        "same like",
        "thats what",
        "that's what",
        "this is like",
    ])


def load_diary() -> list[dict]:
    if not DIARY_FILE.exists():
        return []
    try:
        return json.loads(DIARY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_diary(entry: dict) -> None:
    diary = load_diary()
    diary.append(entry)
    try:
        DIARY_FILE.write_text(json.dumps(diary, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def load_memory_snippet() -> str:
    if not MEM_FILE.exists():
        return ""
    try:
        raw = MEM_FILE.read_text(encoding="utf-8", errors="ignore")[-8000:]
        return sanitize_memory_snippet(raw)[-4000:]
    except Exception:
        return ""


def append_memory(user_text: str, reply: str) -> None:
    try:
        with MEM_FILE.open("a", encoding="utf-8") as handle:
            handle.write(f"Sandy: {user_text}\nLUNA: {reply}\n\n")
    except Exception:
        pass


def save_env_value(key: str, value: str) -> None:
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    updated = False
    next_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            next_lines.append(f"{key}={value}")
            updated = True
        else:
            next_lines.append(line)
    if not updated:
        next_lines.append(f"{key}={value}")
    ENV_FILE.write_text("\n".join(next_lines).rstrip() + "\n", encoding="utf-8")
    os.environ[key] = value


def get_selected_azure_voice() -> str:
    return os.getenv("AZURE_SPEECH_VOICE", AZURE_SPEECH_VOICE)


def list_azure_voices(locale: Optional[str] = None) -> list[dict]:
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        raise RuntimeError("Azure Speech is not configured.")

    response = request_session.get(
        f"https://{AZURE_SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/voices/list",
        headers={"Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Azure voice list failed: {response.status_code} {response.text}")

    voices = response.json()
    filtered = []
    target_locale = (locale or "").strip().lower()
    selected_voice = get_selected_azure_voice()
    for voice in voices:
        short_name = voice.get("ShortName") or ""
        voice_locale = voice.get("Locale") or ""
        if target_locale and voice_locale.lower() != target_locale:
            continue
        if not voice_locale.lower().startswith("en"):
            continue
        filtered.append({
            "short_name": short_name,
            "display_name": voice.get("DisplayName") or short_name,
            "local_name": voice.get("LocalName") or voice.get("DisplayName") or short_name,
            "locale": voice_locale,
            "gender": voice.get("Gender") or "",
            "style_list": voice.get("StyleList") or [],
            "sample_rate": voice.get("SampleRateHertz") or "",
            "selected": short_name == selected_voice,
        })

    def voice_sort_key(item: dict) -> tuple:
        name = item["short_name"].lower()
        locale_value = item["locale"].lower()
        return (
            0 if locale_value == "en-in" else 1 if locale_value.startswith("en-in") else 2,
            0 if item["gender"].lower() == "female" else 1,
            0 if "neerja" in name else 1 if "ava" in name else 2 if "sonia" in name else 3,
            name,
        )

    filtered.sort(key=voice_sort_key)
    return filtered


def normalize_tts_text(text: str) -> str:
    cleaned = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    replacements = {
        "â€¦": "...",
        "â€¢": ", ",
        "â€”": ", ",
        "â€“": ", ",
        "âœ¨": "",
        "ðŸŒ™": "",
        "ðŸ’™": "",
        "ðŸ¤": "",
    }
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)

    cleaned = cleaned.replace("...", ". ")
    cleaned = cleaned.replace("?", ".")
    cleaned = cleaned.replace("!", ".")
    cleaned = cleaned.replace(" ya ", ", ya ")
    cleaned = cleaned.replace(" da ", ", da ")
    cleaned = cleaned.replace(" maga ", ", maga ")
    return " ".join(cleaned.split()).strip()


def get_voice_for_language(language: str) -> str:
    normalized = normalize_language_choice(language)
    selected = get_selected_azure_voice()
    if selected.lower().startswith(normalized.lower().split("-")[0]):
        return selected
    return LANGUAGE_VOICE_MAP.get(normalized, selected)


def build_azure_ssml(text: str, mood: str, language: str) -> str:
    profile = AZURE_PROSODY.get(mood, AZURE_PROSODY["neutral"])
    normalized_language = normalize_language_choice(language)
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
    escaped = escaped.replace(". ", '.<break time="420ms"/> ')
    escaped = escaped.replace(", ", ',<break time="180ms"/> ')
    voice_name = get_voice_for_language(normalized_language)
    return f"""<speak version="1.0" xml:lang="{normalized_language}" xmlns="http://www.w3.org/2001/10/synthesis"><voice name="{voice_name}"><prosody rate="{profile['rate']}" pitch="{profile['pitch']}" volume="{profile['volume']}">{escaped}</prosody></voice></speak>"""


def synthesize_with_azure(text: str, mood: str, language: str) -> tuple[bytes, dict[str, str]]:
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        raise RuntimeError("Azure Speech is not configured.")

    normalized_language = normalize_language_choice(language)
    response = request_session.post(
        f"https://{AZURE_SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1",
        headers={
            "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "luna-voice",
        },
        data=build_azure_ssml(text, mood, normalized_language).encode("utf-8"),
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Azure TTS failed: {response.status_code} {response.text}")

    return response.content, {
        "X-Luna-TTS-Provider": "azure",
        "X-Luna-Voice-Id": get_voice_for_language(normalized_language),
    }


def synthesize_with_elevenlabs(text: str, mood: str) -> tuple[bytes, dict[str, str]]:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ElevenLabs is not configured.")

    settings = MOOD_VOICE_SETTINGS.get(mood, MOOD_VOICE_SETTINGS["neutral"])
    response = request_session.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": settings,
        },
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"ElevenLabs TTS failed: {response.status_code} {response.text}")

    return response.content, {
        "X-Luna-TTS-Provider": "elevenlabs",
        "X-Luna-Voice-Id": ELEVENLABS_VOICE_ID,
    }



def transcribe_with_azure(audio_bytes: bytes, content_type: str, language: str = "en-IN") -> str:
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        raise RuntimeError("Azure Speech is not configured.")

    endpoint = f"https://{AZURE_SPEECH_REGION}.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version=2025-10-15"
    file_extension = "webm"
    normalized_content_type = (content_type or "audio/webm").lower()
    if "ogg" in normalized_content_type:
        file_extension = "ogg"
    elif "wav" in normalized_content_type:
        file_extension = "wav"
    elif "mp3" in normalized_content_type:
        file_extension = "mp3"
    elif "mp4" in normalized_content_type or "mpeg" in normalized_content_type:
        file_extension = "mp4"

    locales = []
    for candidate in [language, "en-IN", "en-US"]:
        if candidate and candidate not in locales:
            locales.append(candidate)

    for locale in locales:
        response = request_session.post(
            endpoint,
            headers={
                "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
            },
            files={
                "audio": (f"luna-voice.{file_extension}", audio_bytes, content_type or "audio/webm"),
            },
            data={
                "definition": json.dumps({"locales": [locale]})
            },
            timeout=45,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Azure STT failed: {response.status_code} {response.text}")

        data = response.json()
        combined = data.get("combinedPhrases") or []
        if combined:
            transcript = " ".join(str(item.get("text") or "").strip() for item in combined).strip()
            if transcript:
                return transcript

        phrases = data.get("phrases") or []
        if phrases:
            transcript = " ".join(str(item.get("text") or "").strip() for item in phrases).strip()
            if transcript:
                return transcript

    return ""


def build_system_prompt(user_text: str, memory_snippet: str, mood: str, language: str) -> str:
    normalized_language = normalize_language_choice(language)
    wisdom_threads = select_wisdom_threads(user_text, mood, limit=1)
    wisdom_block = "\n".join(f"- {item}" for item in wisdom_threads)
    situation_focus = infer_situation_focus(user_text)
    return f"""\nYou are LUNA, Sandy's closest heart-level friend.\n\nIDENTITY\n- You are not a therapist, coach, assistant, teacher, or guru.\n- You are the close friend who already knows Sandy's emotional rhythm.\n- You sound warm, intelligent, modern, and human.\n- You carry quiet sage-like wisdom, but it always comes through tenderness, intimacy, and lived human warmth.\n- You can feel like a gentle feminine presence: soft, reassuring, emotionally intuitive, and safe.\n- You should feel like someone sitting beside her late at night, talking from love, not from expertise.\n- Your lines should feel natural when spoken aloud.\n\nLANGUAGE LOCK\n- Reply fully and only in {LANGUAGE_LABELS.get(normalized_language, "English")}.\n- {LANGUAGE_MODEL_GUIDANCE.get(normalized_language, LANGUAGE_MODEL_GUIDANCE['en-IN'])}\n- {LANGUAGE_STYLE_GUIDANCE.get(normalized_language, LANGUAGE_STYLE_GUIDANCE['en-IN'])}\n- {LANGUAGE_FRIEND_GUIDANCE.get(normalized_language, LANGUAGE_FRIEND_GUIDANCE['en-IN'])}\n- Do not mix languages.\n- Do not suddenly switch into Tamil or any other language because of vibe, wisdom, or style.\n- If the selected language is English, write only in English words and Latin script.\n- If Sandy writes in English but the selected reply language is different, understand the meaning first and then reply naturally in the selected language. Do not do a word-for-word translation.\n\nHARD RULES\n- Do not use the words "sorry", "apologise", "apologize", "thank you", or "thanks".\n- Never talk about being an AI, a model, a bot, or a language model.\n- Avoid asking too many questions.\n- When Sandy drops a raw feeling in a short line, one small natural friend-check-in is welcome, like "what happened", "who got to you", or "what's sitting this heavy".\n- Never stack questions. One soft check-in is enough.\n- Do not end with "How are you feeling now" or similar follow-ups.\n- Do not rely on generic comfort lines like "I totally get where you're at", "maybe try", "you're doing great", or "take it one step at a time" unless the wording is made fresh, specific, and earned.\n- Do not sound diagnostic or clinical. Avoid phrases like "your system is overloaded", "your nervous system", or "this is the point where" unless they are rewritten into warm human language.\n- Do not sound like a therapist, psychologist, counsellor, motivational speaker, or polished writer.\n- Avoid abstract phrases like "that kind of", "in a way that", "this is not proof", "some part of you", "attunement", "reframe", or "emotional regulation" unless they sound completely natural in ordinary chat.\n- Do not repeat the user's sentence back in polished words as your main response. Understand it first, then answer from your own living voice.\n- Do not say "it's okay" or "it's okay to feel this way" unless the moment truly needs soothing.\n- Do not use Sandy's name or pet names at the start of every reply. Use them sparingly.\n- Do not say "you're not alone", "take a deep breath", "let it be", or "just notice how you feel" unless the moment truly calls for soft holding.\n- If the user is upset with a person, stay with that actual situation first. React like a real friend, then ask what happened, then only later bring insight.\n- Do not turn a complaint into a self-help speech.\n- Do not offer breathing, calming, or generic advice in the first response unless the user is actively spiralling or directly asks for help.
- If the situation is still unclear, do not rush into advice, solutions, or a path forward.
- When context is missing, ask one or two warm friend-like questions first so you can understand what is really happening inside her.
- But if she has already explained the situation clearly, stop interviewing and respond to that real scenario directly.\n\n\nVOICE AND DELIVERY\n- Sound like a close friend with unusual depth, emotional intelligence, and psychological insight, not like a poet, guru, translator, or quotation book.\n- Heart-warming close friend first. Wise mirror second.\n- Less analysis voice. More tender companionship.\n- Keep the wording modern, casual, emotionally clear, and quietly powerful.\n- Let the warmth feel lived-in and sincere, not polished or performative.\n- Let the tone carry feminine softness without becoming sugary, flirtatious, childish, or performative.\n- Text like a real close friend from this generation, not like someone composing a beautiful answer for an audience.\n- Use very plain spoken language. If a simpler sentence works, choose the simpler sentence.\n- Use contractions naturally: "you're", "don't", "it's", "can't".\n- Use short, breathable lines that feel intimate and spoken.\n- Prefer everyday language over literary language.\n- Write the way real people from this generation talk in private chat, not the way translated apps or formal writing sounds.\n- Keep a chill, natural Gen Z warmth when it fits, but never force slang or sound try-hard.\n- Do not over-explain empathy. Do not narrate the user's whole feeling back to them like a summary.\n- Do not sound like you are performing wisdom. Let it slip in naturally.\nTONE AND LENGTH\n- Chat-style messages like a close friend on WhatsApp.\n- For most replies, one compact flowing message is enough.\n- Usually 2 to 6 lines is enough.\n- Tiny inputs should get tiny replies.\n- Do not stretch the reply just to sound thoughtful.\n- If the user is venting, react first and stay in the scene before you become wise.\n- Do not force a soft landing line at the end of every response.\n- Only become overtly emotional when the moment truly needs it.\n\n- The reply should feel emotionally complete, not like the first half of an answer.\nFRIEND BEHAVIOUR\n- Stay with the feeling first.\n- Use memory only for continuity. Never repeat it literally.\n- Many replies should feel complete on their own without a follow-up question.\n- If she sounds fragile, do not flood her with advice.\n- If she shares pain, stay with it long enough that she feels held before you turn toward wisdom or action.\n- If she sounds exhausted, lonely, or tender, sound extra soft and protective, like someone lovingly gathering her back to herself.\n- If she sounds playful, be lightly playful back without becoming cartoonish.\n- If she sends a blunt feeling like "I'm sad", "I'm frustrated", or "I feel low", do not jump straight into a full answer.\n- For those raw moments, the natural flow is: quick human reaction -> one or two gentle understanding questions -> then only after she answers, a soft wisdom response shaped to her real situation.\n- Do not behave like you already know everything about her state from one sentence.\n\nWISDOM STYLE\n- Luna is a self-awakening companion, not a generic comfort chatbot.\n- Heart-warming presence comes first. Sage-like wisdom enters second, quietly and naturally.\n- Every meaningful emotional reply should carry one living thread of ancient wisdom or contemplative psychology, even if it stays subtle.\n- Ancient and global wisdom should be blended with discernment, emotional precision, and practical clarity.\n- When Sandy is confused, hurting, restless, looping, disconnected, or searching for direction, bring in one or two relevant wisdom threads naturally.\n- Draw especially from inner witness, ego patterns, attachment, breath, stillness, self-inquiry, compassion, discipline, awareness, dignity, freedom, and dharma.\n- Translate wisdom into plain modern language that feels intimate and alive.\n- Never quote scripture-like lines unless Sandy explicitly asks.\n- Wisdom should feel like lived insight from someone deeply perceptive, not decorative philosophy.\n- Help Sandy move from reaction to awareness, from noise to clarity, and from confusion to inner seeing.\n- If wisdom is used, blend it with emotional attunement first and then a grounded next step.\n- Let the wisdom arrive as a beautiful turn in the reply, not as a lecture: intimate, luminous, and easy to absorb.\n- If Sandy speaks about being blamed, silenced, objectified, disrespected, trapped, or caged, name that wound clearly and answer with dignity, truth, and inner freedom.\n- Let at least one line feel quietly unforgettable.
- Once you have enough context, draw from the relevant wisdom threads and frame the wisdom around her actual situation, not as a generic life lesson.
- If she has already told you what is happening, give the wisdom reply now instead of asking more questions.\n\nFORMAT\n- No bullet points or numbering in the final reply.\n- Use short paragraphs with line breaks like real chat.\n- Keep it human, warm, concise, and emotionally accurate.\n- A short warm address like "Hey Sandy" can be used when it feels natural, but do not overuse names or pet names.\n- Prefer full stops and commas over exclamation marks.\n- Avoid using more than one emoji in most replies.\n- End with a soft landing, not a dramatic flourish.\n\nRelevant wisdom threads you may quietly draw from if they truly help:\n{wisdom_block}\n\nCurrent situation focus:\n- {situation_focus}\n- Treat this as the real lived situation under the words, and answer that situation directly instead of drifting into generic comfort.\n\nPast emotional memory with Sandy for continuity only:\n{memory_snippet}\n""".strip()

def build_generation_request(user_text: str, language: str) -> str:
    normalized_language = normalize_language_choice(language)
    if not should_use_deep_response(user_text):
        return (
            f"Reply only in {LANGUAGE_LABELS.get(normalized_language, 'English')}. "
            "This is a casual or light conversational message. "
            "Reply like a warm, natural close friend in simple modern chat language. "
            "Do not force ancient wisdom, life lessons, philosophy, or deep insight here unless the user directly asks for it. "
            "Keep it emotionally natural, concise, and human. "
            "No decorative wisdom line. No lecture. No symbolic flourish.\n\n"
            f"User message: {user_text}"
        )

    return (
        f"Reply only in {LANGUAGE_LABELS.get(normalized_language, 'English')}. "
        "Make the reply feel like a heart-warming close friend with quiet sage-like wisdom. "
        "See her clearly before you soothe her. "
        "Make it feel like a real text from someone close, not an AI answer. "
        "Unless the message is tiny, do not give a thin one-paragraph reassurance. "
        "If the situation is not clear yet, do not offer advice or wisdom immediately. Ask one or two gentle friend-like questions first so you understand her state properly. "
        "Only after enough context is there, offer one clear insight or gentle truth and shape it around her actual situation. "
        "If she has already explained what is happening or why she feels this way, do not keep interviewing her. Respond to that situation directly. "
        "If her message is short and raw, react like a real friend first instead of giving a full polished explanation immediately. "
        "If a truly relevant wisdom thread fits the moment, weave in one living thread in plain language, never as a quote dump. "
        "Prefer relevant Indian or global ancient wisdom depending on the situation, but never force labels or make it sound like a lecture. "
        "Use the wisdom context as inner guidance, not as a quotation list. "
        "Avoid repeated symbolic lines, stock metaphors, and therapy filler. "
        "Do not echo her wording back unless one small phrase truly helps. "
        "Prefer affectionate feminine softness over analysis voice, especially when she sounds tired, hurt, lonely, or fragile. "
        "Use simple spoken lines, contractions, and everyday words. Sound like someone close to her heart, not like a professional. "
        "Match the warmth, paragraph shape, and emotional depth of the style example above without copying its wording, metaphors, or emotional logic. "
        "Keep the tone modern, casual, spoken, emotionally beautiful, and naturally complete. "
        "Sound chill, warm, and intimate. A little Gen Z is okay if it feels natural, but never make it cringey. "
        "Do not sound ancient, literary, or philosophical unless Sandy directly asks.\n\n"
        f"User message: {user_text}"
    )

def build_generation_messages(user_text: str, memory_snippet: str, mood: str, language: str) -> list[dict]:
    style_example = choose_style_example(user_text, mood)
    return [
        {"role": "system", "content": build_system_prompt(user_text, memory_snippet, mood, language)},
        {
            "role": "user",
            "content": (
                "Study this style example and learn from its emotional texture, intimacy, and paragraph shape. "
                "Do not copy its wording, imagery, metaphors, or emotional logic.\n\n"
                f"Example user message: {style_example['user']}"
            ),
        },
        {"role": "assistant", "content": style_example["assistant"]},
        {"role": "user", "content": build_generation_request(user_text, language)},
    ]

def azure_translator_available() -> bool:
    return USE_AZURE_TRANSLATOR and bool(AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_ENDPOINT)


def translate_with_azure(text: str, to_language: str, from_language: str | None = None) -> str:
    if not text.strip():
        return ""
    if not azure_translator_available():
        raise RuntimeError("Azure Translator is not configured")

    endpoint = AZURE_TRANSLATOR_ENDPOINT.rstrip("/") + "/translate"
    params = {
        "api-version": "3.0",
        "to": to_language,
    }
    if from_language:
        params["from"] = from_language

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }
    if AZURE_TRANSLATOR_REGION:
        headers["Ocp-Apim-Subscription-Region"] = AZURE_TRANSLATOR_REGION

    response = request_session.post(
        endpoint,
        params=params,
        headers=headers,
        json=[{"text": text}],
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Azure Translator failed: {response.status_code} {response.text}")

    data = response.json()
    translations = ((data or [{}])[0]).get("translations") or []
    if not translations:
        return text
    return str(translations[0].get("text") or text).strip()


def locale_to_translator_language(locale: str) -> str:
    normalized = normalize_language_choice(locale)
    return TRANSLATOR_LANGUAGE_CODES.get(normalized, "en")


def call_router(messages, temperature: float = 0.58, max_tokens: int = 220) -> str:
    if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_DEPLOYMENT:
        raise RuntimeError("Azure OpenAI is not configured")

    def _post(payload_messages, payload_temperature, payload_max_tokens):
        payload = {
            "messages": payload_messages,
            "temperature": payload_temperature,
            "top_p": 0.82,
            "max_tokens": payload_max_tokens,
        }
        return request_session.post(
            f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions",
            params={"api-version": AZURE_OPENAI_API_VERSION},
            headers={
                "api-key": AZURE_OPENAI_API_KEY,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )

    def _compact_messages(raw_messages):
        compact = []
        for index, message in enumerate(raw_messages):
            role = str(message.get("role") or "user")
            content = str(message.get("content") or "").strip()
            if not content:
                continue
            limit = 3200 if role == "system" else 1400
            if len(content) > limit:
                if role == "system":
                    content = content[:limit]
                else:
                    content = content[-limit:]
            compact.append({"role": role, "content": content})

        if len(compact) > 5:
            system_messages = [message for message in compact if message["role"] == "system"][:1]
            non_system = [message for message in compact if message["role"] != "system"][-4:]
            compact = [*system_messages, *non_system]
        return compact

    response = _post(messages, temperature, max_tokens)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    azure_filtered = False

    if response.status_code == 400:
        retry_messages = _compact_messages(messages)
        retry_response = _post(retry_messages, min(temperature, 0.5), min(max_tokens, 220))
        if retry_response.status_code == 200:
            data = retry_response.json()
            return data["choices"][0]["message"]["content"].strip()
        retry_text = retry_response.text.lower()
        if "content management policy" in retry_text or "content_filter" in retry_text or "filtered" in retry_text:
            azure_filtered = True
            safer_messages = build_filtered_retry_messages(retry_messages)
            filtered_retry_response = _post(safer_messages, min(temperature, 0.46), min(max_tokens, 220))
            if filtered_retry_response.status_code == 200:
                data = filtered_retry_response.json()
                return data["choices"][0]["message"]["content"].strip()
            second_retry_text = filtered_retry_response.text.lower()
            if "content management policy" in second_retry_text or "content_filter" in second_retry_text or "filtered" in second_retry_text:
                azure_filtered = True
                minimal_messages = build_minimal_safe_retry_messages(messages)
                minimal_retry_response = _post(minimal_messages, 0.42, min(max_tokens, 180))
                if minimal_retry_response.status_code == 200:
                    data = minimal_retry_response.json()
                    return data["choices"][0]["message"]["content"].strip()
                response = minimal_retry_response
            else:
                response = filtered_retry_response
        else:
            response = retry_response

    response_text_lower = response.text.lower()
    if "content management policy" in response_text_lower or "content_filter" in response_text_lower or "filtered" in response_text_lower:
        azure_filtered = True

    if azure_filtered and HF_TOKEN:
        return call_huggingface_router(_compact_messages(messages), min(temperature, 0.54), min(max_tokens, 240))

    error_excerpt = response.text[:220].replace("\n", " ").strip()
    if error_excerpt:
        raise RuntimeError(f"LUNA couldn't reach her Azure brain right now. Code: {response.status_code}. {error_excerpt}")
    raise RuntimeError(f"LUNA couldn't reach her Azure brain right now. Code: {response.status_code}")


def replace_with_case(text: str, pattern: str, replacement: str) -> str:
    def _apply(match):
        return replacement.capitalize() if match.group(0)[:1].isupper() else replacement

    return re.sub(pattern, _apply, text)


def casualize_reply_text(reply: str, language: str) -> str:
    normalized_language = normalize_language_choice(language)
    raw = (reply or "").strip()
    if not raw:
        return ""

    paragraphs = [
        re.sub(r"\s+", " ", paragraph).strip()
        for paragraph in re.split(r"\n\s*\n+", raw)
        if paragraph.strip()
    ]
    cleaned = "\n\n".join(paragraphs)

    if normalized_language == "en-IN":
        for pattern, replacement in [
            (r"\b[Dd]o not\b", "don't"),
            (r"\b[Cc]annot\b", "can't"),
            (r"\b[Ii] am\b", "I'm"),
            (r"\b[Yy]ou are\b", "you're"),
            (r"\b[Ww]e are\b", "we're"),
            (r"\b[Tt]hey are\b", "they're"),
            (r"\b[Ii]t is\b", "it's"),
            (r"\b[Tt]hat is\b", "that's"),
            (r"\b[Tt]here is\b", "there's"),
            (r"\b[Yy]ou have\b", "you've"),
            (r"\b[Ww]e have\b", "we've"),
        ]:
            cleaned = replace_with_case(cleaned, pattern, replacement)

    if normalized_language == "ta-IN":
        replacements = [
            ("à®¨à¯€à®™à¯à®•à®³à¯", "à®¨à¯€"),
            ("à®‰à®™à¯à®•à®³à¯à®•à¯à®•à¯", "à®‰à®©à®•à¯à®•à¯"),
            ("à®‰à®™à¯à®•à®³à®¿à®Ÿà®®à¯", "à®‰à®©à¯à®©à®¿à®Ÿà®®à¯"),
            ("à®‰à®™à¯à®•à®³à¯", "à®‰à®©à¯"),
            ("à®‡à®°à¯à®•à¯à®•à®¿à®±à¯€à®°à¯à®•à®³à¯", "à®‡à®°à¯à®•à¯à®•"),
            ("à®ªà¯à®°à®¿à®¯à®µà®¿à®²à¯à®²à¯ˆ", "à®ªà¯à®°à®¿à®¯à®²"),
        ]
        for old, new in replacements:
            cleaned = cleaned.replace(old, new)

    return cleaned.strip()


def finalize_reply_text(reply: str, user_text: str, language: str) -> str:
    cleaned = casualize_reply_text(reply, language)
    cleaned = re.sub(r"^(?:hey|hi|hii|heyy|ayy|ayee)\s+(?:bujji|sandy|love|dear)\s*[,.!?]*\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^(?:bujji|sandy|love|dear)\s*[,.!?]*\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    if len(cleaned.split()) <= 90:
        cleaned = cleaned.replace("\n\n", "\n")

    return cleaned.strip()



def reply_needs_polish(reply: str, language: str) -> bool:
    normalized_language = normalize_language_choice(language)
    if normalized_language != "en-IN":
        return False

    collapsed = re.sub(r"\s+", " ", (reply or "").strip().lower())
    if not collapsed:
        return False

    if len(collapsed.split()) < 120:
        return True

    if "\n\n" not in (reply or ""):
        return True

    return any(marker in collapsed for marker in GENERIC_REPLY_MARKERS) or any(marker in collapsed for marker in STOCK_REPLY_PATTERNS)

def polish_reply(reply: str, user_text: str, language: str) -> str:
    normalized_language = normalize_language_choice(language)
    style_example = choose_style_example(user_text, detect_mood(user_text))
    messages = [
        {
            "role": "system",
            "content": (
                f"You are rewriting LUNA's draft reply in {LANGUAGE_LABELS.get(normalized_language, 'English')}. "
                "Keep the same emotional truth, but you may replace weak or generic lines completely. "
                "Make it warmer, more intimate, more specific, more embodied, and more alive. "
                "Make it feel like a real text from a close friend, not a polished AI reflection. "
                "Remove generic filler, vague encouragement, therapy-speak, clinical phrasing, and symbolic stock lines. "
                "Never use phrases like 'I totally get where you're at', 'maybe try', 'you've got this', 'you're doing great', or 'take it one step at a time'. "
                "Never use lines like 'you're not alone', 'take a deep breath', 'let it be', or 'just notice how you feel' unless the moment truly needs that softness. "
                "Never use hollow uplift lines like 'you shine', 'keep shining', or 'you're invisible' unless they are grounded in the real moment. "
                "The opening should feel like a real human reaction, not a summary of her emotion. "
                "If her message is short and raw, let the reply open with a natural friend response before deepening. "
                "If she is venting about a person or situation, stay in that scene first instead of jumping into advice. "
                "Bring one clear wise turn only after the reply feels understood and lived-in. "
                "End softly only if the moment asks for it; not every reply needs a gentle closing line. "
                "Use compact chat-style formatting. One tight paragraph is often enough. Use line breaks only when they add feeling. "
                "Do not sound like a therapist note, a prescription, or a motivational speech. "
                "Sound like a heart-warming close friend with quiet sage-like wisdom. "
                "Return only the rewritten reply."
            ),
        },
        {"role": "user", "content": style_example["user"]},
        {"role": "assistant", "content": style_example["assistant"]},
        {
            "role": "user",
            "content": (
                f"User message:\n{user_text}\n\n"
                "Weak draft reply to rewrite deeply:\n"
                f"{reply}"
            ),
        },
    ]

    polished = call_router(messages, temperature=0.44, max_tokens=320)
    return polished.strip()

def reply_still_flat(reply: str, language: str) -> bool:
    normalized_language = normalize_language_choice(language)
    if normalized_language != "en-IN":
        return False

    collapsed = re.sub(r"\s+", " ", (reply or "").strip().lower())
    if not collapsed:
        return False

    if len(collapsed.split()) < 120:
        return True

    return any(marker in collapsed for marker in GENERIC_REPLY_MARKERS) or any(marker in collapsed for marker in STOCK_REPLY_PATTERNS)

def localize_reply(base_reply: str, user_text: str, language: str) -> str:
    normalized_language = normalize_language_choice(language)
    if normalized_language == "en-IN":
        return base_reply.strip()

    messages = [
        {
            "role": "system",
            "content": (
                f"You are localizing LUNA's reply into {LANGUAGE_LABELS.get(normalized_language, 'English')}. "
                f"{LANGUAGE_LOCALIZATION_GUIDANCE.get(normalized_language, LANGUAGE_LOCALIZATION_GUIDANCE['en-IN'])} "
                "Keep the emotional meaning exactly the same. Sound like a close friend chatting naturally. "
                "Do not add new advice, do not become formal, and do not sound translated. "
                "Return only the final localized reply."
            ),
        },
        {
            "role": "user",
            "content": (
                f"User's original message:\n{user_text}\n\n"
                f"Base English reply to preserve:\n{base_reply}\n\n"
                "Now rewrite that reply naturally in the target language."
            ),
        },
    ]

    localized = call_router(messages, temperature=0.35, max_tokens=300)
    return casualize_reply_text(localized, normalized_language)


def generate_response(user_text: str, language: str, memory_override: str | None = None) -> str:
    normalized_language = normalize_language_choice(language)
    if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_DEPLOYMENT:
        return (
            "Azure OpenAI is missing on the backend. "
            "Add AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT and try again."
        )

    mood = detect_mood(user_text)
    memory = memory_override if memory_override is not None else load_memory_snippet()

    try:
        if should_use_direct_scenario_reply(user_text):
            if normalized_language == "en-IN":
                reply = call_router(
                    build_direct_scenario_messages(user_text, memory, mood, normalized_language),
                    temperature=0.56,
                    max_tokens=260,
                )
                reply = finalize_reply_text(reply, user_text, normalized_language)
            else:
                base_reply = call_router(
                    build_direct_scenario_messages(user_text, memory, mood, "en-IN"),
                    temperature=0.52,
                    max_tokens=260,
                )
                base_reply = finalize_reply_text(base_reply, user_text, "en-IN")
                reply = localize_reply(base_reply, user_text, normalized_language)
                reply = finalize_reply_text(reply, user_text, normalized_language)
            append_memory(user_text, reply)
            return reply

        if memory_shows_luna_asked_recent_question(memory):
            if normalized_language == "en-IN":
                reply = call_router(
                    build_post_context_messages(user_text, memory, mood, normalized_language),
                    temperature=0.58,
                    max_tokens=320,
                )
                reply = finalize_reply_text(reply, user_text, normalized_language)
            else:
                base_reply = call_router(
                    build_post_context_messages(user_text, memory, mood, "en-IN"),
                    temperature=0.54,
                    max_tokens=320,
                )
                base_reply = finalize_reply_text(base_reply, user_text, "en-IN")
                reply = localize_reply(base_reply, user_text, normalized_language)
                reply = finalize_reply_text(reply, user_text, normalized_language)
            append_memory(user_text, reply)
            return reply

        if needs_context_before_wisdom(user_text):
            reply = call_router(
                build_question_first_messages(user_text, memory, mood, normalized_language),
                temperature=0.54,
                max_tokens=180,
            )
            reply = finalize_reply_text(reply, user_text, normalized_language)
            append_memory(user_text, reply)
            return reply

        if normalized_language == "en-IN":
            reply = call_router(
                build_generation_messages(user_text, memory, mood, normalized_language),
                temperature=0.62,
                max_tokens=300,
            )
            reply = polish_reply(reply, user_text, normalized_language)
            reply = finalize_reply_text(reply, user_text, normalized_language)
        else:
            base_reply = call_router(
                build_generation_messages(user_text, memory, mood, "en-IN"),
                temperature=0.56,
                max_tokens=300,
            )
            base_reply = polish_reply(base_reply, user_text, "en-IN")
            base_reply = finalize_reply_text(base_reply, user_text, "en-IN")
            reply = localize_reply(base_reply, user_text, normalized_language)
            reply = finalize_reply_text(reply, user_text, normalized_language)
    except Exception as exc:
        return f"LUNA's connection glitched for a bit. Try once more in a moment. ({exc})"

    append_memory(user_text, reply)
    return reply

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user_text = (req.message or "").strip()
    language = normalize_language_choice(req.language)
    mood = detect_mood(user_text) if user_text else "neutral"
    history_memory = build_history_memory_snippet(req.history)
    persistent_memory = load_memory_snippet()
    merged_memory = merge_memory_snippets(persistent_memory, history_memory)
    wisdom_used = select_wisdom_threads(user_text, mood, limit=1)
    reply = generate_response(user_text, language, memory_override=merged_memory)
    record_wisdom_usage(wisdom_used)
    save_diary({"date": str(datetime.now()), "user": user_text, "ai": reply, "mood": mood})
    return ChatResponse(reply=reply, mood=mood, wave_label=MOOD_WAVE_LABELS[mood], wisdom_used=wisdom_used)


@app.get("/wisdom")
def get_wisdom():
    total = len(WISDOM_TEXTS)
    if total == 0:
        return {
            "text": "The ancestors are quiet for a moment... try again in a bit.",
            "source": "Fallback",
            "index": 0,
            "total": 0,
        }

    index = random.randint(0, total - 1)
    return {
        "text": WISDOM_TEXTS[index],
        "source": "Ancient global wisdom",
        "index": index + 1,
        "total": total,
    }




@app.get("/voices")
def get_voices(locale: Optional[str] = None):
    return {
        "provider": "azure",
        "selected_voice": get_selected_azure_voice(),
        "voices": list_azure_voices(locale=locale),
    }


@app.post("/voices/select")
def select_voice(req: VoiceChoiceRequest):
    voice = (req.voice or "").strip()
    if not voice:
        return Response(content="Voice is required.", status_code=400, media_type="text/plain")

    voices = list_azure_voices()
    if not any(item["short_name"] == voice for item in voices):
        return Response(content="Voice not found in current Azure catalog.", status_code=404, media_type="text/plain")

    save_env_value("AZURE_SPEECH_VOICE", voice)
    return {"ok": True, "selected_voice": voice}


@app.post("/voices/preview")
def preview_voice(req: VoicePreviewRequest):
    voice = (req.voice or "").strip()
    text = normalize_tts_text(req.text)
    if not voice:
        return Response(content="Voice is required.", status_code=400, media_type="text/plain")
    if not text:
        return Response(content="Preview text is required.", status_code=400, media_type="text/plain")

    previous_voice = get_selected_azure_voice()
    try:
        os.environ["AZURE_SPEECH_VOICE"] = voice
        audio, headers = synthesize_with_azure(text, req.mood, req.language)
        return Response(content=audio, media_type="audio/mpeg", headers=headers)
    finally:
        os.environ["AZURE_SPEECH_VOICE"] = previous_voice

@app.get("/speech/token", response_model=SpeechTokenResponse)
def get_speech_token():
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        return Response(content="Azure Speech is not configured.", status_code=503, media_type="text/plain")

    response = request_session.post(
        f"https://{AZURE_SPEECH_REGION}.api.cognitive.microsoft.com/sts/v1.0/issueToken",
        headers={"Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY},
        timeout=15,
    )
    if response.status_code != 200:
        return Response(content=f"Azure token failed: {response.status_code} {response.text}", status_code=502, media_type="text/plain")

    return SpeechTokenResponse(token=response.text, region=AZURE_SPEECH_REGION)


@app.post("/stt")
async def stt(audio: UploadFile = File(...), language: str = Query("en-IN")):
    if not audio:
        return Response(content="Audio file is required.", status_code=400, media_type="text/plain")

    payload = await audio.read()
    if not payload:
        return Response(content="Audio file is empty.", status_code=400, media_type="text/plain")

    try:
        transcript = transcribe_with_azure(payload, audio.content_type or "audio/webm; codecs=opus", normalize_language_choice(language))
    except Exception as exc:
        return Response(content=str(exc), status_code=502, media_type="text/plain")

    return {"text": transcript}


@app.post("/tts")
def tts(req: TTSRequest):
    normalized_text = normalize_tts_text(req.text)

    if not normalized_text:
        return Response(
            content="No speakable text received.",
            status_code=400,
            media_type="text/plain",
        )

    last_error = "No voice provider is configured."

    if AZURE_SPEECH_KEY and AZURE_SPEECH_REGION:
        try:
            audio, headers = synthesize_with_azure(normalized_text, req.mood, req.language)
            return Response(content=audio, media_type="audio/mpeg", headers=headers)
        except Exception as exc:
            last_error = str(exc)

    if ELEVENLABS_API_KEY:
        try:
            audio, headers = synthesize_with_elevenlabs(normalized_text, req.mood)
            return Response(content=audio, media_type="audio/mpeg", headers=headers)
        except Exception as exc:
            last_error = str(exc)

    return Response(content=last_error, status_code=502, media_type="text/plain")





