import streamlit as st
import requests
from deep_translator import GoogleTranslator
from transformers import pipeline
import zlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

API_KEY = "$2a$10$Sfp9KhzSzJBDPcKJJZYSNeDKxmiuw8xc.Jn7/xMJbKLmFmaGikJVe"
BIN_ID = "69d68478856a6821891093db"
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY
}

st.set_page_config(page_title="CrypTalk Sender", page_icon="📤", layout="centered")
st.title("📤 CrypTalk Sender")
st.caption("Translate, encrypt, and send a secure message")

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
    "neutral": "😐"
}

@st.cache_resource
def load_models():
    return pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=1,
    )

emotion_classifier = load_models()

col1, col2 = st.columns(2)
with col1:
    sender_name = st.text_input("Sender Name")
with col2:
    receiver_name = st.text_input("Receiver Name")

sender_lang = st.selectbox("Sender Language", list(LANG_CODES.keys()))
receiver_lang = st.selectbox("Receiver Language", list(LANG_CODES.keys()))

user_text = st.text_area("Enter your message", placeholder="Type your message here…", height=140)

send = st.button("🔐 Send Secure Message")

def compress(text):
    return zlib.compress(text.encode())


def decompress(data):
    return zlib.decompress(data).decode()


def encrypt(data):
    key = AESGCM.generate_key(bit_length=128)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    encrypted = aes.encrypt(nonce, data, None)
    return encrypted, key, nonce


if send:
    if not sender_name.strip() or not receiver_name.strip() or not user_text.strip():
        st.warning("Please enter sender, receiver, and a message.")
    else:
        with st.spinner("Processing secure message..."):
            translated_text = GoogleTranslator(
                source=LANG_CODES[sender_lang], target="en"
            ).translate(user_text)

            prediction = emotion_classifier(translated_text)[0]
            emotion = prediction["label"]
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
            except requests.exceptions.RequestException as exc:
                st.error("❌ Unable to send secure message.")
                st.write(exc)
            else:
                if response.status_code in (200, 201):
                    st.success("✅ Secure message sent to cloud storage")
                    st.write("**Stored message details:**")
                    st.write("Sender:", sender_name)
                    st.write("Receiver:", receiver_name)
                    st.write("Emotion:", emotion.upper(), emoji)
                    st.write("Message stored as:")
                    st.code(tagged_text)
                else:
                    st.error("❌ Failed to send message")
                    st.write(response.text)
