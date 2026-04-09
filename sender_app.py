import streamlit as st
import requests
from deep_translator import GoogleTranslator
import zlib
import os
import re
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

API_KEY = "$2a$10$Sfp9KhzSzJBDPcKJJZYSNeDKxmiuw8xc.Jn7/xMJbKLmFmaGikJVe"
BIN_ID = "69d68478856a6821891093db"
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY
}

st.set_page_config(page_title="CrypTalk Sender", page_icon="📤")
st.title("📤 CrypTalk Sender")

LANG_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml"
}

EMOJI_MAP = {
    "joy": "😊",
    "sadness": "😢",
    "anger": "😠",
    "fear": "😨",
    "surprise": "😲",
    "sarcasm": "😏",
    "neutral": "😐"
}

# 🔥 SARCASM DETECTION
def detect_sarcasm(text):
    text_lower = text.lower()

    sarcasm_phrases = [
        "as if", "yeah right", "sure", "you think so", "wow great",
        "just perfect", "nice job", "well done", "obviously", "totally"
    ]

    # repeated letters (sooo, greaaat)
    if re.search(r"(.)\1{2,}", text_lower):
        return True

    # excessive punctuation
    if "!!" in text or "??" in text or "!?" in text:
        return True

    # sarcastic phrases
    if any(p in text_lower for p in sarcasm_phrases):
        return True

    return False


# 🔥 IMPROVED EMOTION DETECTION
def detect_emotion(text):
    text = text.lower()

    # FIRST: sarcasm check
    if detect_sarcasm(text):
        return "sarcasm"

    joy_words = [
        "happy", "joy", "love", "awesome", "great", "fantastic", "excited",
        "good", "nice", "wonderful", "best", "glad", "yay", "smile",
        "delighted", "thrilled", "pleased", "enjoy", "brilliant"
    ]

    sadness_words = [
        "sad", "depressed", "unhappy", "cry", "miss", "lonely",
        "heartbroken", "down", "upset", "tired", "lost", "pain",
        "hurt", "miserable", "gloomy", "bad", "regret"
    ]

    anger_words = [
        "angry", "mad", "hate", "annoyed", "furious",
        "irritated", "frustrated", "rage", "stupid", "worst",
        "disgusting", "ridiculous", "nonsense", "trash"
    ]

    fear_words = [
        "scared", "afraid", "fear", "worried", "nervous",
        "help", "help me", "save me", "danger", "run", "running",
        "escape", "stuck", "trapped", "lost", "panic", "emergency",
        "something is wrong", "not safe", "underwater", "drowning",
        "chasing", "hiding", "terrified", "unsafe"
    ]

    surprise_words = [
        "wow", "amazing", "unexpected", "shocked",
        "unbelievable", "suddenly", "what", "seriously",
        "no way", "really", "omg"
    ]

    # phrase priority (important)
    for phrase in fear_words:
        if phrase in text:
            return "fear"

    for word in anger_words:
        if word in text:
            return "anger"

    for word in sadness_words:
        if word in text:
            return "sadness"

    for word in joy_words:
        if word in text:
            return "joy"

    for word in surprise_words:
        if word in text:
            return "surprise"

    return "neutral"


col1, col2 = st.columns(2)
with col1:
    sender_name = st.text_input("Sender Name")
with col2:
    receiver_name = st.text_input("Receiver Name")

sender_lang = st.selectbox("Sender Language", list(LANG_CODES.keys()))
receiver_lang = st.selectbox("Receiver Language", list(LANG_CODES.keys()))

user_text = st.text_area("Enter your message", height=140)

send = st.button("🔐 Send Secure Message")

def compress(text):
    return zlib.compress(text.encode())

def encrypt(data):
    key = AESGCM.generate_key(bit_length=128)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    encrypted = aes.encrypt(nonce, data, None)
    return encrypted, key, nonce


if send:
    if not sender_name or not receiver_name or not user_text:
        st.warning("Fill all fields")
    else:
        with st.spinner("Processing..."):

            translated_text = GoogleTranslator(
                source=LANG_CODES[sender_lang],
                target="en"
            ).translate(user_text)

            emotion = detect_emotion(translated_text)

            emoji = EMOJI_MAP.get(emotion, "💬")
            tagged_text = f"[{emotion.upper()} {emoji}] {translated_text}"

            compressed = compress(tagged_text)
            encrypted_data, key, nonce = encrypt(compressed)

            payload = {
                "sender": sender_name,
                "receiver": receiver_name,
                "sender_lang": sender_lang,
                "receiver_lang": receiver_lang,
                "emotion": f"{emotion.upper()} {emoji}",
                "encrypted": encrypted_data.hex(),
                "key": key.hex(),
                "nonce": nonce.hex(),
                "tagged_text": tagged_text,
            }

            try:
                response = requests.put(URL, json=payload, headers=HEADERS)
            except Exception as e:
                st.error(e)
            else:
                if response.status_code in (200, 201):
                    st.success("Message Sent ✅")
                    st.write("Emotion:", emotion.upper(), emoji)
                    st.code(tagged_text)
                else:
                    st.error("Failed to send")
                    st.write(response.text)
